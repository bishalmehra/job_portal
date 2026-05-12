import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'

export default function AuthPage({ mode }) {
  const isLogin = mode === 'login'
  const navigate = useNavigate()
  const { login } = useAuth()

  const [form, setForm]     = useState({ name: '', email: '', password: '', role: 'user' })
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup'
      const payload  = isLogin
        ? { email: form.email, password: form.password }
        : { name: form.name, email: form.email, password: form.password, role: form.role }

      const { data } = await api.post(endpoint, payload)
      login({ name: data.name, role: data.role, id: data.user_id, email: form.email }, data.access_token)
      navigate(data.role === 'host' ? '/host' : '/jobs')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
    }}>
      {/* Left panel */}
      <div style={{
        background: 'var(--blue-700)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '4rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative circles */}
        <div style={{
          position: 'absolute', width: 400, height: 400,
          borderRadius: '50%', border: '1px solid rgba(255,255,255,0.1)',
          top: -100, right: -100,
        }} />
        <div style={{
          position: 'absolute', width: 300, height: 300,
          borderRadius: '50%', border: '1px solid rgba(255,255,255,0.08)',
          bottom: 40, left: -80,
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '3rem' }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'rgba(255,255,255,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
              </svg>
            </div>
            <span style={{ fontFamily: 'Fraunces, serif', fontSize: '1.5rem', color: 'white', fontWeight: 600 }}>JobHive</span>
          </div>

          <h1 style={{ fontFamily: 'Fraunces, serif', fontSize: '2.75rem', color: 'white', fontWeight: 300, lineHeight: 1.2, marginBottom: '1.5rem' }}>
            {isLogin ? 'Welcome\nback.' : 'Find your\nnext role.'}
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: '1rem', lineHeight: 1.7, maxWidth: 340 }}>
            {isLogin
              ? 'Sign in to continue your job search or manage your listings.'
              : 'Join thousands of job seekers and top employers on JobHive.'}
          </p>

          <div style={{ marginTop: '3rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {[
              { icon: '🔍', text: 'Smart full-text job search' },
              { icon: '⚡', text: 'Real-time listings from top employers' },
              { icon: '🛡️', text: 'Secure, role-based access' },
            ].map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
                <span style={{ color: 'rgba(255,255,255,0.75)', fontSize: '0.9rem' }}>{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel — form */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 2rem',
        background: 'var(--white)',
      }}>
        <div style={{ width: '100%', maxWidth: 400, animation: 'fadeIn 0.4s ease both' }}>
          <h2 style={{ fontFamily: 'Fraunces, serif', fontSize: '1.75rem', fontWeight: 600, color: 'var(--slate-900)', marginBottom: '0.5rem' }}>
            {isLogin ? 'Sign in' : 'Create account'}
          </h2>
          <p style={{ color: 'var(--slate-500)', fontSize: '0.9rem', marginBottom: '2rem' }}>
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <Link to={isLogin ? '/signup' : '/login'} style={{ color: 'var(--blue-600)', fontWeight: 500 }}>
              {isLogin ? 'Sign up' : 'Sign in'}
            </Link>
          </p>

          {error && (
            <div style={{
              background: '#fef2f2', border: '1px solid #fecaca',
              color: '#dc2626', borderRadius: 'var(--radius)',
              padding: '0.75rem 1rem', fontSize: '0.875rem',
              marginBottom: '1.25rem',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {!isLogin && (
              <Field label="Full name" name="name" type="text" placeholder="Rahul Sharma"
                value={form.name} onChange={handleChange} required />
            )}
            <Field label="Email address" name="email" type="email" placeholder="you@example.com"
              value={form.email} onChange={handleChange} required />
            <Field label="Password" name="password" type="password" placeholder="Min. 6 characters"
              value={form.password} onChange={handleChange} required />

            {!isLogin && (
              <div>
                <label style={labelStyle}>I am a</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.4rem' }}>
                  {['user', 'host'].map(r => (
                    <button key={r} type="button"
                      onClick={() => setForm(f => ({ ...f, role: r }))}
                      style={{
                        padding: '0.75rem',
                        borderRadius: 'var(--radius)',
                        border: `2px solid ${form.role === r ? 'var(--blue-500)' : 'var(--slate-200)'}`,
                        background: form.role === r ? 'var(--blue-50)' : 'var(--white)',
                        color: form.role === r ? 'var(--blue-700)' : 'var(--slate-500)',
                        fontWeight: 500, fontSize: '0.9rem',
                        transition: 'all 0.15s',
                      }}>
                      {r === 'user' ? '👤 Job Seeker' : '🏢 Employer'}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <button type="submit" disabled={loading} style={{
              marginTop: '0.5rem',
              padding: '0.875rem',
              borderRadius: 'var(--radius)',
              background: loading ? 'var(--slate-300)' : 'var(--blue-600)',
              color: 'white',
              fontWeight: 600,
              fontSize: '0.95rem',
              transition: 'all 0.15s',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}>
              {loading ? 'Please wait…' : (isLogin ? 'Sign in' : 'Create account')}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

const labelStyle = {
  display: 'block',
  fontSize: '0.8rem',
  fontWeight: 600,
  color: 'var(--slate-600)',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
  marginBottom: '0.4rem',
}

function Field({ label, name, type, placeholder, value, onChange, required }) {
  const [focused, setFocused] = useState(false)
  return (
    <div>
      <label style={labelStyle}>{label}</label>
      <input
        name={name} type={type} placeholder={placeholder}
        value={value} onChange={onChange} required={required}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        style={{
          width: '100%', padding: '0.75rem 1rem',
          borderRadius: 'var(--radius)',
          border: `1.5px solid ${focused ? 'var(--blue-500)' : 'var(--slate-200)'}`,
          background: 'var(--white)', fontSize: '0.95rem',
          color: 'var(--slate-800)',
          transition: 'border-color 0.15s',
          boxShadow: focused ? '0 0 0 3px rgba(59,130,246,0.1)' : 'none',
        }}
      />
    </div>
  )
}