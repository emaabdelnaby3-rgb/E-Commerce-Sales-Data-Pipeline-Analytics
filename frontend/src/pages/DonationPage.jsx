import { useState } from 'react'
import api from '../services/api'

function DonationPage() {
  const [form, setForm] = useState({ case_id: '', amount: '', payment_method: 'card' })
  const [created, setCreated] = useState(null)
  const [message, setMessage] = useState('')

  async function initiate(e) {
    e.preventDefault()
    try {
      const { data } = await api.post('/donor/donate', form)
      setCreated(data)
      setMessage(`Donation initiated (${data.payment_status}). Transaction: ${data.transaction_ref}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Donation initiation failed')
    }
  }

  async function confirm() {
    if (!created?.donation_id) return
    try {
      const { data } = await api.post(`/donor/donations/${created.donation_id}/confirm`)
      setMessage(`Donation confirmed: ${data.payment_status}; case ${data.case_status}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Confirmation failed')
    }
  }

  return (
    <section>
      <h1>Donation Page</h1>
      <form onSubmit={initiate} className="form-grid">
        <input placeholder="Case ID" value={form.case_id} onChange={(e) => setForm({ ...form, case_id: e.target.value })} />
        <input placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
          <option value="card">Card</option>
          <option value="bank_transfer">Bank Transfer</option>
        </select>
        <button>Initiate Donation</button>
      </form>
      <button onClick={confirm} disabled={!created}>Confirm Donation</button>
      <p>{message}</p>
    </section>
  )
}

export default DonationPage
