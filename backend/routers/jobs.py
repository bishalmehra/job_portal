from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.database import get_db
from core.security import get_current_user, require_role
from models.schemas import JobType, ExperienceLevel

router = APIRouter()


def _serialize_job(job: dict) -> dict:
    job["id"] = str(job.pop("_id"))
    if "host_id" in job:
        job["host_id"] = str(job["host_id"])
    return job


@router.get(
    "/search",
    summary="Search & filter active job listings",
    description="""
Full-text search over job title, description, and skills.
Combine with any filter to narrow results.
Results are sorted by MongoDB text relevance score, then by newest first.
""",
)
async def search_jobs(
    q:                Optional[str]            = Query(None,  description="Free-text search (title, description, skills)"),
    location:         Optional[str]            = Query(None,  description="City or region"),
    job_type:         Optional[JobType]        = Query(None),
    experience_level: Optional[ExperienceLevel]= Query(None),
    category:         Optional[str]            = Query(None),
    salary_min:       Optional[int]            = Query(None,  description="Minimum salary (INR)"),
    salary_max:       Optional[int]            = Query(None,  description="Maximum salary (INR)"),
    page:             int                      = Query(1,     ge=1),
    page_size:        int                      = Query(10,    ge=1, le=50),
    current_user: dict = Depends(require_role("user")),
):
    db = get_db()
    pipeline = []

    # ── Stage 1: Text search (if query provided) ──────────────────────────────
    if q:
        pipeline.append({
            "$match": {
                "$text": {"$search": q},
                "is_active": True,
            }
        })
        pipeline.append({"$addFields": {"score": {"$meta": "textScore"}}})
    else:
        pipeline.append({"$match": {"is_active": True}})

    # ── Stage 2: Structured filters ───────────────────────────────────────────
    filters = {}
    if location:
        filters["location"] = {"$regex": location, "$options": "i"}
    if job_type:
        filters["job_type"] = job_type.value
    if experience_level:
        filters["experience_level"] = experience_level.value
    if category:
        filters["category"] = {"$regex": category, "$options": "i"}
    if salary_min is not None:
        filters.setdefault("salary.min", {})["$gte"] = salary_min
    if salary_max is not None:
        filters.setdefault("salary.max", {})["$lte"] = salary_max

    if filters:
        pipeline.append({"$match": filters})

    # ── Stage 3: Sort ─────────────────────────────────────────────────────────
    if q:
        pipeline.append({"$sort": {"score": -1, "posted_at": -1}})
    else:
        pipeline.append({"$sort": {"posted_at": -1}})

    # ── Stage 4: Count total (before pagination) ──────────────────────────────
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result   = await db.jobs.aggregate(count_pipeline).to_list(1)
    total          = count_result[0]["total"] if count_result else 0

    # ── Stage 5: Paginate ─────────────────────────────────────────────────────
    pipeline.append({"$skip":  (page - 1) * page_size})
    pipeline.append({"$limit": page_size})

    # ── Stage 6: Project (hide internal _id, expose id) ───────────────────────
    pipeline.append({
        "$project": {
            "title": 1, "description": 1, "company": 1,
            "location": 1, "job_type": 1, "experience_level": 1,
            "category": 1, "skills": 1, "salary": 1,
            "is_active": 1, "host_id": 1, "posted_at": 1, "updated_at": 1,
            **({"score": 1} if q else {}),
        }
    })

    jobs = await db.jobs.aggregate(pipeline).to_list(page_size)
    jobs = [_serialize_job(j) for j in jobs]

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "pages":     (total + page_size - 1) // page_size,
        "jobs":      jobs,
    }


@router.get(
    "/{job_id}",
    summary="Get full details of a single job listing",
)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    from bson import ObjectId
    db  = get_db()
    try:
        oid = ObjectId(job_id)
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = await db.jobs.find_one({"_id": oid, "is_active": True})
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")

    return _serialize_job(job)
