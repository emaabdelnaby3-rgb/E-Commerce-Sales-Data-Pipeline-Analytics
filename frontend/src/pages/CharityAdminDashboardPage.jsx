import { useEffect, useState } from 'react'
import api from '../services/api'

function CharityAdminDashboardPage() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/admin/stats').then(({ data }) => setStats(data)).catch(() => setStats(null))
  }, [])

  return (
    <section>
      <h1>Charity Admin Dashboard</h1>
      {stats ? (
        <div className="cards-grid">
          <div className="card">Total cases: {stats.total_cases}</div>
          <div className="card">Approved: {stats.approved_cases}</div>
          <div className="card">Funded: {stats.funded_cases}</div>
          <div className="card">Donations: {stats.total_donations}</div>
        </div>
      ) : <p>No data</p>}
    </section>
  )
}

export default CharityAdminDashboardPage
