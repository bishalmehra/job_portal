import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav style={{
      background: 'var(--white)',
      borderBottom: '1px solid var(--slate-200)',
      padding: '0 2rem',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'var(--blue-600)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/>
            <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
          </svg>
        </div>
        <span style={{ fontFamily: 'Fraunces, serif', fontSize: '1.25rem', fontWeight: 600, color: 'var(--slate-900)' }}>
          JobHive
        </span>
        <span style={{
          marginLeft: '0.25rem',
          fontSize: '0.7rem',
          fontWeight: 600,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          background: user?.role === 'host' ? 'var(--blue-100)' : 'var(--slate-100)',
          color: user?.role === 'host' ? 'var(--blue-700)' : 'var(--slate-500)',
          padding: '2px 8px',
          borderRadius: 99,
        }}>
          {user?.role === 'host' ? 'Employer' : 'Job Seeker'}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--slate-800)' }}>{user?.name}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--slate-400)' }}>{user?.email || user?.role}</div>
        </div>
        <button onClick={handleLogout} style={{
          padding: '0.5rem 1rem',
          borderRadius: 'var(--radius)',
          background: 'var(--slate-100)',
          color: 'var(--slate-600)',
          fontSize: '0.875rem',
          fontWeight: 500,
          transition: 'all 0.15s',
        }}
        onMouseOver={e => { e.target.style.background = 'var(--slate-200)' }}
        onMouseOut={e => { e.target.style.background = 'var(--slate-100)' }}
        >
          Sign out
        </button>
      </div>
    </nav>
  )
}