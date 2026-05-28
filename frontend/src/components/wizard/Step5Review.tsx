import { useApplication } from '@/hooks/useApplications'
import { useTriggerUnderwriting } from '@/hooks/useUnderwriting'
import { useNavigate } from 'react-router-dom'

interface Props {
  applicationId: string
  onBack: () => void
}

function Row({ label, value }: { label: string; value: string | number | null | undefined }) {
  if (value == null || value === '') return null
  return (
    <div className="flex justify-between py-1.5 text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-900">{String(value)}</span>
    </div>
  )
}

export default function Step5Review({ applicationId, onBack }: Props) {
  const { data: app, isLoading } = useApplication(applicationId)
  const trigger = useTriggerUnderwriting()
  const navigate = useNavigate()

  const handleSubmit = async () => {
    const run = await trigger.mutateAsync(applicationId)
    navigate(`/underwriting/${run.id}`)
  }

  if (isLoading || !app) {
    return <div className="text-gray-400 text-sm">Loading application...</div>
  }

  const b = app.business
  const g = app.guarantors[0]
  const bc = app.business_credit
  const lr = app.loan_request

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">Review &amp; Submit</h2>
      <p className="text-sm text-gray-500">Review the application details below, then submit for underwriting.</p>

      <div className="space-y-4">
        {/* Business */}
        <div className="card p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Business</h3>
          <div className="divide-y divide-gray-100">
            <Row label="Business Name" value={b?.business_name} />
            <Row label="Owner" value={b?.owner_name} />
            <Row label="Email" value={b?.owner_email} />
            <Row label="State" value={b?.state} />
            <Row label="Business Type" value={b?.business_type} />
            <Row label="Years in Business" value={b?.years_in_biz} />
            <Row label="Annual Revenue" value={b?.annual_revenue ? `$${b.annual_revenue.toLocaleString()}` : null} />
          </div>
        </div>

        {/* Guarantor */}
        {g && (
          <div className="card p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Guarantor</h3>
            <div className="divide-y divide-gray-100">
              <Row label="Name" value={g.full_name} />
              <Row label="Credit Score" value={g.credit_score} />
              <Row label="Ownership" value={g.ownership_pct ? `${g.ownership_pct}%` : null} />
            </div>
          </div>
        )}

        {/* Loan Request */}
        {lr && (
          <div className="card p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Loan Request</h3>
            <div className="divide-y divide-gray-100">
              <Row label="Amount" value={`$${lr.requested_amount.toLocaleString()}`} />
              <Row label="Term" value={`${lr.requested_term_mo} months`} />
              <Row label="Equipment Type" value={lr.equipment_type} />
              <Row label="Condition" value={lr.equipment_condition} />
              <Row label="Equipment Year" value={lr.equipment_year} />
              <Row label="State of Operation" value={lr.state_of_operation} />
              <Row label="Down Payment" value={lr.down_payment_pct ? `${lr.down_payment_pct}%` : null} />
            </div>
          </div>
        )}
      </div>

      {trigger.isError && (
        <p className="text-sm text-red-600">Failed to submit. Please try again.</p>
      )}

      <div className="flex justify-between pt-2">
        <button type="button" className="btn-secondary" onClick={onBack}>Back</button>
        <button
          type="button"
          className="btn-primary"
          onClick={handleSubmit}
          disabled={trigger.isPending}
        >
          {trigger.isPending ? 'Submitting...' : 'Submit for Underwriting'}
        </button>
      </div>
    </div>
  )
}
