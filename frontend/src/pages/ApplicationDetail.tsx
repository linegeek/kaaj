import { useParams, useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'
import { ArrowLeftIcon, BoltIcon } from '@heroicons/react/24/outline'
import { useApplication } from '@/hooks/useApplications'
import { useTriggerUnderwriting } from '@/hooks/useUnderwriting'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500">{title}</h2>
      {children}
    </div>
  )
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-gray-500">{label}</dt>
      <dd className="mt-0.5 text-sm font-medium text-gray-900">{value ?? '-'}</dd>
    </div>
  )
}

function formatCurrency(amount: number | null | undefined) {
  if (amount == null) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount)
}

export default function ApplicationDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: application, isLoading, isError } = useApplication(id!)
  const triggerMutation = useTriggerUnderwriting()
  const [runError, setRunError] = useState<string | null>(null)

  async function handleRunUnderwriting() {
    setRunError(null)
    try {
      const run = await triggerMutation.mutateAsync(id!)
      navigate(`/underwriting/${run.id}`)
    } catch {
      setRunError('Failed to start underwriting. Please try again.')
    }
  }

  if (isLoading) {
    return <div className="p-8 text-sm text-gray-500">Loading application...</div>
  }
  if (isError || !application) {
    return <div className="p-8 text-sm text-red-600">Application not found.</div>
  }

  const biz = application.business
  const lr = application.loan_request
  const bc = application.business_credit

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Link to="/applications" className="text-gray-400 hover:text-gray-600">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              {biz?.business_name ?? 'Application'}
            </h1>
            <p className="mt-0.5 text-sm text-gray-500">
              Status: <span className="font-medium capitalize">{application.status}</span>
              {' · '}
              Submitted {new Date(application.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <button
            onClick={handleRunUnderwriting}
            disabled={triggerMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <BoltIcon className="h-4 w-4" />
            {triggerMutation.isPending ? 'Starting...' : 'Run Underwriting'}
          </button>
          {runError && <p className="text-xs text-red-600">{runError}</p>}
        </div>
      </div>

      {/* Business Info */}
      {biz && (
        <Section title="Business Information">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Field label="Business Name" value={biz.business_name} />
            <Field label="DBA" value={biz.dba_name} />
            <Field label="Business Type" value={biz.business_type?.replace(/_/g, ' ')} />
            <Field label="State" value={biz.state} />
            <Field label="Years in Business" value={biz.years_in_biz} />
            <Field label="Annual Revenue" value={formatCurrency(biz.annual_revenue)} />
            <Field label="Employee Count" value={biz.employee_count} />
            <Field label="NAICS Code" value={biz.naics_code} />
          </dl>
        </Section>
      )}

      {/* Owner / Guarantors */}
      {(biz || application.guarantors.length > 0) && (
        <Section title="Owners &amp; Guarantors">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {biz && (
              <>
                <Field label="Owner Name" value={biz.owner_name} />
                <Field label="Owner Email" value={biz.owner_email} />
                <Field label="Owner Phone" value={biz.owner_phone} />
              </>
            )}
          </dl>
          {application.guarantors.length > 0 && (
            <div className="mt-4">
              <p className="mb-2 text-xs font-medium text-gray-500">Personal Guarantors</p>
              <div className="divide-y divide-gray-100 rounded-lg border border-gray-200">
                {application.guarantors.map(g => (
                  <div key={g.id} className="flex items-center justify-between px-4 py-3 text-sm">
                    <span className="font-medium text-gray-900">{g.full_name}</span>
                    <div className="flex gap-6 text-gray-500">
                      <span>Credit: {g.credit_score ?? '-'}</span>
                      <span>Ownership: {g.ownership_pct != null ? `${g.ownership_pct}%` : '-'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>
      )}

      {/* Loan Request */}
      {lr && (
        <Section title="Loan Request">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Field label="Requested Amount" value={formatCurrency(lr.requested_amount)} />
            <Field label="Term" value={`${lr.requested_term_mo} months`} />
            <Field label="Equipment Type" value={lr.equipment_type?.replace(/_/g, ' ')} />
            <Field label="Equipment Condition" value={lr.equipment_condition} />
            <Field label="Equipment Year" value={lr.equipment_year} />
            <Field label="Equipment Age" value={lr.equipment_age_yrs != null ? `${lr.equipment_age_yrs} yrs` : '-'} />
            <Field label="State of Operation" value={lr.state_of_operation} />
            <Field label="Down Payment" value={lr.down_payment_pct != null ? `${lr.down_payment_pct}%` : '-'} />
          </dl>
          {lr.equipment_description && (
            <div className="mt-4">
              <dt className="text-xs text-gray-500">Description</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{lr.equipment_description}</dd>
            </div>
          )}
        </Section>
      )}

      {/* Business Credit */}
      {bc && (
        <Section title="Business Credit">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Field label="FICO SBSS" value={bc.fico_sbss} />
            <Field label="Experian Intelliscore" value={bc.experian_intelliscore} />
            <Field label="D&amp;B Paydex" value={bc.duns_paydex} />
            <Field label="Bankruptcies" value={bc.bankruptcies} />
            <Field label="Liens" value={bc.liens} />
            <Field label="Judgments" value={bc.judgments} />
          </dl>
        </Section>
      )}
    </div>
  )
}
