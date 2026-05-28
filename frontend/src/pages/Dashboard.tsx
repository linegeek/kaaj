import { Link } from 'react-router-dom'
import {
  PlusCircleIcon,
  BuildingLibraryIcon,
  DocumentTextIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

const steps = [
  { n: '1', title: 'Submit Application', desc: 'Enter business info, guarantor details, credit data, and equipment loan request through the guided wizard.' },
  { n: '2', title: 'Run Underwriting', desc: 'The engine evaluates the application against every active lender program using 26 weighted eligibility rules.' },
  { n: '3', title: 'Review Results', desc: 'View ranked lender matches with fit scores, pass/fail breakdowns, and per-rule reasoning.' },
]

export default function Dashboard() {
  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Equipment Finance Platform</h1>
        <p className="mt-1 text-sm text-gray-500">
          Underwrite applications and match borrowers with the best-fit lender programs automatically.
        </p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Link
          to="/applications/new"
          className="card flex items-start gap-4 p-5 hover:border-brand-300 hover:shadow-md transition-all group"
        >
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 group-hover:bg-brand-100 transition-colors">
            <PlusCircleIcon className="h-6 w-6 text-brand-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">New Application</p>
            <p className="mt-0.5 text-sm text-gray-500">
              Start a 5-step wizard to submit a new equipment finance application for underwriting.
            </p>
          </div>
        </Link>

        <Link
          to="/lenders"
          className="card flex items-start gap-4 p-5 hover:border-brand-300 hover:shadow-md transition-all group"
        >
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 group-hover:bg-brand-100 transition-colors">
            <BuildingLibraryIcon className="h-6 w-6 text-brand-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">Manage Lenders</p>
            <p className="mt-0.5 text-sm text-gray-500">
              Add lenders, configure programs, set eligibility rules, and import policy PDFs.
            </p>
          </div>
        </Link>
      </div>

      {/* How it works */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 mb-4">How it works</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {steps.map(({ n, title, desc }) => (
            <div key={n} className="card p-5">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white mb-3">
                {n}
              </div>
              <p className="font-medium text-gray-900">{title}</p>
              <p className="mt-1 text-sm text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Rule engine overview */}
      <div className="card p-5">
        <div className="flex items-center gap-3 mb-3">
          <ChartBarIcon className="h-5 w-5 text-brand-600" />
          <h2 className="text-base font-semibold text-gray-900">Rule Engine</h2>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Each application is scored against every active lender program using 26 weighted eligibility rules across 4 categories.
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: 'Credit Rules', count: 6, color: 'bg-blue-50 text-blue-700' },
            { label: 'Business Rules', count: 7, color: 'bg-green-50 text-green-700' },
            { label: 'Equipment Rules', count: 7, color: 'bg-orange-50 text-orange-700' },
            { label: 'Geographic Rules', count: 6, color: 'bg-purple-50 text-purple-700' },
          ].map(({ label, count, color }) => (
            <div key={label} className={`rounded-lg px-4 py-3 ${color}`}>
              <p className="text-2xl font-bold">{count}</p>
              <p className="text-xs font-medium mt-0.5">{label}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
          <DocumentTextIcon className="h-4 w-4" />
          <span>Fit score = base (85 pts on rule compliance) + bonus (up to 15 pts for strong credit, tenure, revenue)</span>
        </div>
      </div>
    </div>
  )
}
