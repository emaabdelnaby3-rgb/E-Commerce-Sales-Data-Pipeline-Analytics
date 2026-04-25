import { Link } from 'react-router-dom'

const links = [
  ['Login', '/login'],
  ['Register', '/register'],
  ['Request', '/beneficiary/request'],
  ['Upload', '/beneficiary/upload'],
  ['Cases', '/cases'],
  ['Donate', '/donate'],
  ['Beneficiary Dash', '/dashboard/beneficiary'],
  ['Donor Dash', '/dashboard/donor'],
  ['Charity Dash', '/dashboard/charity-admin'],
  ['Gov Dash', '/dashboard/government-admin'],
  ['Case Review', '/admin/review'],
  ['Analytics', '/analytics']
]

function AppLayout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Charity Platform</h2>
        <nav>
          {links.map(([label, path]) => (
            <Link key={path} to={path} className="nav-link">
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="page">{children}</main>
    </div>
  )
}

export default AppLayout
