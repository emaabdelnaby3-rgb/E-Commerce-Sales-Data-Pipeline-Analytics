import { useEffect, useState } from 'react'
import api from '../services/api'

function DonationCasesPage() {
  const [cases, setCases] = useState([])
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    api.get('/donor/cases')
      .then(({ data }) => {
        setCases(data.items || [])
        setMessage('')
      })
      .catch((err) => setMessage(err.response?.data?.error || 'Could not load cases'))
  }, [])

  return (
    <section>
      <h1>Donation Cases Listing</h1>
      {message && <p>{message}</p>}
      <div className="cards-grid">
        {cases.map((c) => (
          <article key={c.case_id} className="card">
            <h3>{c.title}</h3>
            <p>Category: {c.category}</p>
            <p>Requested: {c.amount_requested}</p>
            <p>Funded: {c.amount_funded}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default DonationCasesPage
