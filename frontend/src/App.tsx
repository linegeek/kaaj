import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import ApplicationList from '@/pages/ApplicationList'
import ApplicationDetail from '@/pages/ApplicationDetail'
import ApplicationWizard from '@/pages/ApplicationWizard'
import UnderwritingResults from '@/pages/UnderwritingResults'
import LenderList from '@/pages/LenderList'
import LenderDetail from '@/pages/LenderDetail'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="applications" element={<ApplicationList />} />
        <Route path="applications/new" element={<ApplicationWizard />} />
        <Route path="applications/:id" element={<ApplicationDetail />} />
        <Route path="underwriting/:runId" element={<UnderwritingResults />} />
        <Route path="lenders" element={<LenderList />} />
        <Route path="lenders/:id" element={<LenderDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
