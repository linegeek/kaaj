import { useForm } from 'react-hook-form'
import type { GuarantorCreatePayload } from '@/types'

interface Props {
  onNext: (data: GuarantorCreatePayload) => void
  onBack: () => void
  loading: boolean
}

export default function Step2Guarantor({ onNext, onBack, loading }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<GuarantorCreatePayload>()

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">Personal Guarantor</h2>
      <p className="text-sm text-gray-500">Enter the primary guarantor who will personally guarantee the loan.</p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="label">Full Name *</label>
          <input className="input" placeholder="Jane Smith" {...register('full_name', { required: true })} />
          {errors.full_name && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Personal Credit Score</label>
          <input className="input" type="number" min="300" max="850" placeholder="720" {...register('credit_score', { valueAsNumber: true })} />
          <p className="mt-1 text-xs text-gray-400">FICO score (300-850)</p>
        </div>
        <div>
          <label className="label">Ownership Percentage (%)</label>
          <input className="input" type="number" min="0" max="100" step="0.1" placeholder="100" {...register('ownership_pct', { valueAsNumber: true })} />
        </div>
        <div>
          <label className="label">SSN Last 4 Digits</label>
          <input className="input" maxLength={4} placeholder="1234" {...register('ssn_last4')} />
        </div>
      </div>

      <div className="flex justify-between pt-2">
        <button type="button" className="btn-secondary" onClick={onBack}>Back</button>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Next: Credit Data'}
        </button>
      </div>
    </form>
  )
}
