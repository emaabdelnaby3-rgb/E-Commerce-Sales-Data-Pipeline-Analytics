import { useState } from 'react'
import api from '../services/api'

function BeneficiaryRequestPage() {
  const [form, setForm] = useState({ organization_id: '', category: '', title: '', description: '', amount_requested: '' })
  const [message, setMessage] = useState('')

  async function submit(e) {
    e.preventDefault()
    try {
      const { data } = await api.post('/beneficiary/requests', form)
      setMessage(`Case ${data.case_id} submitted with status ${data.status}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Submit failed')
    }
  }

  return (
    <section>
      <h1>Beneficiary Request Form</h1>
      <form onSubmit={submit} className="form-grid">
        <input placeholder="Organization ID" value={form.organization_id} onChange={(e) => setForm({ ...form, organization_id: e.target.value })} />
        <input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
        <input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input placeholder="Amount requested" value={form.amount_requested} onChange={(e) => setForm({ ...form, amount_requested: e.target.value })} />
        <button>Submit Request</button>
      </form>
      <p>{message}</p>
    </section>
  )
}

export default BeneficiaryRequestPage
