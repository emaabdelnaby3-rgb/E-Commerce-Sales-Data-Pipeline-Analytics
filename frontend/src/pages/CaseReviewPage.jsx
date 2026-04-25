import { useState } from 'react'
import api from '../services/api'

function CaseReviewPage() {
  const [form, setForm] = useState({ caseId: '', decision: 'approved', notes: '' })
  const [message, setMessage] = useState('')

  async function submit(e) {
    e.preventDefault()
    try {
      const { data } = await api.post(`/admin/cases/${form.caseId}/review`, {
        decision: form.decision,
        notes: form.notes
      })
      setMessage(`Case ${data.case_id} is now ${data.status}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Review failed')
    }
  }

  return (
    <section>
      <h1>Case Review Page</h1>
      <form onSubmit={submit} className="form-grid">
        <input placeholder="Case ID" value={form.caseId} onChange={(e) => setForm({ ...form, caseId: e.target.value })} />
        <select value={form.decision} onChange={(e) => setForm({ ...form, decision: e.target.value })}>
          <option value="approved">Approve</option>
          <option value="rejected">Reject</option>
          <option value="needs_info">Needs Info</option>
        </select>
        <textarea placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        <button>Submit Review</button>
      </form>
      <p>{message}</p>
    </section>
  )
}

export default CaseReviewPage
