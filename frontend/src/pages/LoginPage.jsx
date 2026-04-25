import { useState } from 'react'
import api, { setAuthToken } from '../services/api'

function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      const { data } = await api.post('/auth/login', form)
      localStorage.setItem('access_token', data.access_token)
      setAuthToken(data.access_token)
      setMessage(`Logged in as ${data.roles.join(', ')}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Login failed')
    }
  }

  return (
    <section>
      <h1>Login</h1>
      <form onSubmit={handleSubmit} className="form-grid">
        <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button>Login</button>
      </form>
      <p>{message}</p>
    </section>
  )
}

export default LoginPage
