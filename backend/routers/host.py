from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime, timezone
from bson import ObjectId
from core.database import get_db
from core.security import require_role
from models.schemas import JobCreate, JobUpdate, JobOut
from typing import Optional

router = APIRouter()

HOST_ROLE = require_role("host")


def _serialize_job(job: dict) -> dict:
    job["id"]      = str(job.pop("_id"))
    job["host_id"] = str(job["host_id"])
    return job


def _valid_oid(job_id: str) -> ObjectId:
    try:
        return ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post(
    "/jobs",
    status_code=status.HTTP_201_CREATED,
    summary="Post a new job listing",
)
async def create_job(
    body: JobCreate,
    host: dict = Depends(HOST_ROLE),
):
    db  = get_db()
    now = datetime.now(timezone.utc)

    job_doc = {
        **body.model_dump(),
        "host_id":   ObjectId(host["id"]),
        "posted_at": now,
        "updated_at": now,
    }
    # Flatten nested Pydantic objects
    if job_doc.get("salary"):
        job_doc["salary"] = job_doc["salary"] if isinstance(job_doc["salary"], dict) else job_doc["salary"].model_dump()
    if job_doc.get("job_type") and hasattr(job_doc["job_type"], "value"):
        job_doc["job_type"] = job_doc["job_type"].value
    if job_doc.get("experience_level") and hasattr(job_doc["experience_level"], "value"):
        job_doc["experience_level"] = job_doc["experience_level"].value

    result = await db.jobs.insert_one(job_doc)
    created = await db.jobs.find_one({"_id": result.inserted_id})
    return _serialize_job(created)


# ── List own jobs ──────────────────────────────────────────────────────────────

@router.get(
    "/jobs",
    summary="List all jobs posted by this host",
)
async def list_my_jobs(
    is_active: Optional[bool] = Query(None, description="Filter by active/inactive"),
    page:      int            = Query(1,    ge=1),
    page_size: int            = Query(10,   ge=1, le=50),
    host: dict = Depends(HOST_ROLE),
):
    db = get_db()
    query: dict = {"host_id": ObjectId(host["id"])}
    if is_active is not None:
        query["is_active"] = is_active

    total = await db.jobs.count_documents(query)
    skip  = (page - 1) * page_size
    jobs  = await db.jobs.find(query).sort("posted_at", -1).skip(skip).limit(page_size).to_list(page_size)
    jobs  = [_serialize_job(j) for j in jobs]

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "pages":     (total + page_size - 1) // page_size,
        "jobs":      jobs,
    }


# ── Get single own job ─────────────────────────────────────────────────────────

@router.get(
    "/jobs/{job_id}",
    summary="Get details of one of the host's own job listings",
)
async def get_my_job(job_id: str, host: dict = Depends(HOST_ROLE)):
    db  = get_db()
    oid = _valid_oid(job_id)
    job = await db.jobs.find_one({"_id": oid, "host_id": ObjectId(host["id"])})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _serialize_job(job)


# ── Update ─────────────────────────────────────────────────────────────────────

@router.patch(
    "/jobs/{job_id}",
    summary="Update any field of an existing job listing",
)
async def update_job(
    job_id: str,
    body:   JobUpdate,
    host:   dict = Depends(HOST_ROLE),
):
    db  = get_db()
    oid = _valid_oid(job_id)

    # Only the owning host can update
    existing = await db.jobs.find_one({"_id": oid, "host_id": ObjectId(host["id"])})
    if not existing:
        raise HTTPException(status_code=404, detail="Job not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    # Serialize enum values
    for enum_field in ("job_type", "experience_level"):
        if enum_field in updates and hasattr(updates[enum_field], "value"):
            updates[enum_field] = updates[enum_field].value
    if "salary" in updates and updates["salary"]:
        updates["salary"] = updates["salary"] if isinstance(updates["salary"], dict) else updates["salary"].model_dump()

    updates["updated_at"] = datetime.now(timezone.utc)

    await db.jobs.update_one({"_id": oid}, {"$set": updates})
    updated = await db.jobs.find_one({"_id": oid})
    return _serialize_job(updated)


# ── Soft delete (deactivate) ───────────────────────────────────────────────────

@router.delete(
    "/jobs/{job_id}",
    summary="Remove (deactivate) a job listing",
    description="Sets `is_active = false`. The record is kept in DB for history.",
)
async def delete_job(job_id: str, host: dict = Depends(HOST_ROLE)):
    db  = get_db()
    oid = _valid_oid(job_id)

    result = await db.jobs.update_one(
        {"_id": oid, "host_id": ObjectId(host["id"])},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Job listing deactivated successfully", "job_id": job_id}


# ── Hard delete ────────────────────────────────────────────────────────────────

@router.delete(
    "/jobs/{job_id}/permanent",
    summary="Permanently delete a job listing from the database",
)
async def hard_delete_job(job_id: str, host: dict = Depends(HOST_ROLE)):
    db  = get_db()
    oid = _valid_oid(job_id)

    result = await db.jobs.delete_one({"_id": oid, "host_id": ObjectId(host["id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Job listing permanently deleted", "job_id": job_id}


# ── Stats ──────────────────────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Dashboard stats for the host",
)
async def host_stats(host: dict = Depends(HOST_ROLE)):
    db       = get_db()
    host_oid = ObjectId(host["id"])

    pipeline = [
        {"$match": {"host_id": host_oid}},
        {"$group": {
            "_id": "$is_active",
            "count": {"$sum": 1},
        }}
    ]
    results = await db.jobs.aggregate(pipeline).to_list(10)

    active   = next((r["count"] for r in results if r["_id"] is True),  0)
    inactive = next((r["count"] for r in results if r["_id"] is False), 0)

    return {
        "total_jobs":    active + inactive,
        "active_jobs":   active,
        "inactive_jobs": inactive,
    }
