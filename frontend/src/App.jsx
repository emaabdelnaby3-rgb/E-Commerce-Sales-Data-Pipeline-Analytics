import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import BeneficiaryRequestPage from './pages/BeneficiaryRequestPage'
import DocumentUploadPage from './pages/DocumentUploadPage'
import DonationCasesPage from './pages/DonationCasesPage'
import DonationPage from './pages/DonationPage'
import BeneficiaryDashboardPage from './pages/BeneficiaryDashboardPage'
import DonorDashboardPage from './pages/DonorDashboardPage'
import CharityAdminDashboardPage from './pages/CharityAdminDashboardPage'
import GovernmentAdminDashboardPage from './pages/GovernmentAdminDashboardPage'
import CaseReviewPage from './pages/CaseReviewPage'
import AnalyticsDashboardPage from './pages/AnalyticsDashboardPage'

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/beneficiary/request" element={<BeneficiaryRequestPage />} />
        <Route path="/beneficiary/upload" element={<DocumentUploadPage />} />
        <Route path="/cases" element={<DonationCasesPage />} />
        <Route path="/donate" element={<DonationPage />} />
        <Route path="/dashboard/beneficiary" element={<BeneficiaryDashboardPage />} />
        <Route path="/dashboard/donor" element={<DonorDashboardPage />} />
        <Route path="/dashboard/charity-admin" element={<CharityAdminDashboardPage />} />
        <Route path="/dashboard/government-admin" element={<GovernmentAdminDashboardPage />} />
        <Route path="/admin/review" element={<CaseReviewPage />} />
        <Route path="/analytics" element={<AnalyticsDashboardPage />} />
      </Routes>
    </AppLayout>
  )
}

export default App
