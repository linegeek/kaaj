import { Link } from 'react-router-dom'
import { PlusCircleIcon } from '@heroicons/react/24/outline'
import { useApplicationsList } from '@/hooks/useApplications'
import type { ApplicationSummary } from '@/types'

const STATUS_CLASSES: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-600',
  submitted: 'bg-blue-100 text-blue-700',
  underwriting: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  declined: 'bg-red-100 text-red-700',
}

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_CLASSES[status] ?? 'bg-gray-100 text-gray-600'
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {status}
    </span>
  )
}

function formatCurrency(amount: number | null) {
  if (amount == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount)
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function ApplicationRow({ app }: { app: ApplicationSummary }) {
  return (
    <tr className="hover:bg-gray-50">
      <td className="whitespace-nowrap px-6 py-4">
        <div className="font-medium text-gray-900">{app.business_name ?? 'Unnamed'}</div>
        <div className="text-xs text-gray-500">{app.owner_name ?? '-'}</div>
      </td>
      <td className="whitespace-nowrap px-6 py-4">
        <StatusBadge status={app.status} />
      </td>
      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700">
        {formatCurrency(app.requested_amount)}
      </td>
      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-700 capitalize">
        {app.equipment_type?.replace(/_/g, ' ') ?? '-'}
      </td>
      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
        {formatDate(app.created_at)}
      </td>
      <td className="whitespace-nowrap px-6 py-4 text-right text-sm">
        <Link
          to={`/applications/${app.id}`}
          className="font-medium text-brand-600 hover:text-brand-800"
        >
          View
        </Link>
      </td>
    </tr>
  )
}

export default function ApplicationList() {
  const { data: applications, isLoading, isError } = useApplicationsList()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Applications</h1>
          <p className="mt-1 text-sm text-gray-500">All submitted loan applications</p>
        </div>
        <Link to="/applications/new" className="btn-primary flex items-center gap-2">
          <PlusCircleIcon className="h-4 w-4" />
          New Application
        </Link>
      </div>

      <div className="card overflow-hidden p-0">
        {isLoading && (
          <div className="px-6 py-12 text-center text-sm text-gray-500">Loading applications...</div>
        )}
        {isError && (
          <div className="px-6 py-12 text-center text-sm text-red-600">Failed to load applications.</div>
        )}
        {!isLoading && !isError && applications?.length === 0 && (
          <div className="px-6 py-12 text-center">
            <p className="text-sm text-gray-500">No applications yet.</p>
            <Link to="/applications/new" className="mt-3 inline-block text-sm font-medium text-brand-600 hover:text-brand-800">
              Create your first application
            </Link>
          </div>
        )}
        {!isLoading && !isError && applications && applications.length > 0 && (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Business</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Equipment</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Date</th>
                <th className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {applications.map(app => (
                <ApplicationRow key={app.id} app={app} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
