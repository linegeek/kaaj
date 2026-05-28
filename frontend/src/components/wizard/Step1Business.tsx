import { useForm } from 'react-hook-form'
import { useStates, useBusinessTypes } from '@/hooks/useReference'
import type { BusinessCreatePayload } from '@/types'

interface Props {
  onNext: (data: BusinessCreatePayload) => void
  loading: boolean
}

export default function Step1Business({ onNext, loading }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<BusinessCreatePayload>()
  const { data: states = [] } = useStates()
  const { data: bizTypes = [] } = useBusinessTypes()

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">Business Information</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="label">Business Name *</label>
          <input className="input" placeholder="Acme Construction LLC" {...register('business_name', { required: true })} />
          {errors.business_name && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">DBA Name</label>
          <input className="input" placeholder="Operating as..." {...register('dba_name')} />
        </div>
        <div>
          <label className="label">Owner Name *</label>
          <input className="input" placeholder="Jane Smith" {...register('owner_name', { required: true })} />
          {errors.owner_name && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Owner Email *</label>
          <input className="input" type="email" placeholder="jane@acme.com" {...register('owner_email', { required: true })} />
          {errors.owner_email && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Owner Phone</label>
          <input className="input" placeholder="555-000-1234" {...register('owner_phone')} />
        </div>
        <div>
          <label className="label">Business State *</label>
          <select className="input" {...register('state', { required: true })}>
            <option value="">Select state...</option>
            {states.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
          </select>
          {errors.state && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Business Type *</label>
          <select className="input" {...register('business_type', { required: true })}>
            <option value="">Select type...</option>
            {bizTypes.map(t => (
              <option key={t} value={t}>{t.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
            ))}
          </select>
          {errors.business_type && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Years in Business *</label>
          <input className="input" type="number" step="0.5" min="0" placeholder="5" {...register('years_in_biz', { required: true, valueAsNumber: true })} />
          {errors.years_in_biz && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Annual Revenue ($)</label>
          <input className="input" type="number" min="0" placeholder="500000" {...register('annual_revenue', { valueAsNumber: true })} />
        </div>
        <div>
          <label className="label">Employee Count</label>
          <input className="input" type="number" min="1" placeholder="12" {...register('employee_count', { valueAsNumber: true })} />
        </div>
        <div>
          <label className="label">NAICS Code</label>
          <input className="input" placeholder="484110" {...register('naics_code')} />
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Next: Guarantor'}
        </button>
      </div>
    </form>
  )
}
