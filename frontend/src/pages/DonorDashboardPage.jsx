import { useEffect, useState } from 'react'
import api from '../services/api'

function DonorDashboardPage() {
  const [donations, setDonations] = useState([])

  useEffect(() => {
    api.get('/donor/donations').then(({ data }) => setDonations(data.items || [])).catch(() => setDonations([]))
  }, [])

  return (
    <section>
      <h1>Donor Dashboard</h1>
      <ul>
        {donations.map((d) => (
          <li key={d.donation_id}>Donation #{d.donation_id} - Case {d.case_id} - ${d.amount} ({d.payment_status})</li>
        ))}
      </ul>
    </section>
  )
}

export default DonorDashboardPage
