import { useState } from 'react'
import api from '../services/api'

function RegisterPage() {
  const [form, setForm] = useState({
    email: '', password: '', full_name: '', phone: '', national_id: '', role: 'beneficiary', organization_id: ''
  })
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const payload = { ...form, organization_id: form.organization_id || undefined }
    try {
      const { data } = await api.post('/auth/register', payload)
      setMessage(`Registered user ID ${data.user_id}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Registration failed')
    }
  }

  return (
    <section>
      <h1>Registration</h1>
      <form onSubmit={handleSubmit} className="form-grid">
        <input placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input placeholder="National ID" value={form.national_id} onChange={(e) => setForm({ ...form, national_id: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="beneficiary">Beneficiary</option>
          <option value="donor">Donor</option>
          <option value="charity_admin">Charity Admin</option>
          <option value="government_admin">Government Admin</option>
        </select>
        <input placeholder="Organization ID (admin roles)" value={form.organization_id} onChange={(e) => setForm({ ...form, organization_id: e.target.value })} />
        <button>Register</button>
      </form>
      <p>{message}</p>
    </section>
  )
}

export default RegisterPage
