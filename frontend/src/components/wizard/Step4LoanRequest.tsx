import { useForm } from 'react-hook-form'
import { useEquipmentTypes, useStates } from '@/hooks/useReference'
import type { LoanRequestPayload } from '@/types'

interface Props {
  onNext: (data: LoanRequestPayload) => void
  onBack: () => void
  loading: boolean
}

const CONDITIONS = ['new', 'used', 'refurbished']

export default function Step4LoanRequest({ onNext, onBack, loading }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<LoanRequestPayload>()
  const { data: equipmentTypes = [] } = useEquipmentTypes()
  const { data: states = [] } = useStates()

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">Loan Request</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="label">Loan Amount ($) *</label>
          <input className="input" type="number" min="1000" placeholder="150000" {...register('requested_amount', { required: true, valueAsNumber: true })} />
          {errors.requested_amount && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Term (months) *</label>
          <input className="input" type="number" min="12" max="120" placeholder="60" {...register('requested_term_mo', { required: true, valueAsNumber: true })} />
          {errors.requested_term_mo && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Equipment Type *</label>
          <select className="input" {...register('equipment_type', { required: true })}>
            <option value="">Select type...</option>
            {equipmentTypes.map(t => (
              <option key={t} value={t}>{t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
            ))}
          </select>
          {errors.equipment_type && <p className="mt-1 text-xs text-red-600">Required</p>}
        </div>
        <div>
          <label className="label">Equipment Condition</label>
          <select className="input" {...register('equipment_condition')}>
            <option value="">Select...</option>
            {CONDITIONS.map(c => (
              <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Equipment Year</label>
          <input className="input" type="number" min="1990" max={new Date().getFullYear()} placeholder="2021" {...register('equipment_year', { valueAsNumber: true })} />
        </div>
        <div>
          <label className="label">State of Operation</label>
          <select className="input" {...register('state_of_operation')}>
            <option value="">Same as business state</option>
            {states.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
          </select>
          <p className="mt-1 text-xs text-gray-400">Where the equipment will be operated</p>
        </div>
        <div>
          <label className="label">Down Payment (%)</label>
          <input className="input" type="number" min="0" max="100" step="1" placeholder="10" {...register('down_payment_pct', { valueAsNumber: true })} />
        </div>
        <div className="sm:col-span-2">
          <label className="label">Equipment Description</label>
          <textarea className="input" rows={2} placeholder="2021 Caterpillar 320 Excavator, 3,200 hrs..." {...register('equipment_description')} />
        </div>
      </div>

      <div className="flex justify-between pt-2">
        <button type="button" className="btn-secondary" onClick={onBack}>Back</button>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Next: Review'}
        </button>
      </div>
    </form>
  )
}
