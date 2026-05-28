import { useForm } from 'react-hook-form'
import type { BusinessCreditPayload } from '@/types'

interface Props {
  onNext: (data: BusinessCreditPayload) => void
  onBack: () => void
  loading: boolean
}

export default function Step3Credit({ onNext, onBack, loading }: Props) {
  const { register, handleSubmit } = useForm<BusinessCreditPayload>({
    defaultValues: { bankruptcies: 0, liens: 0, judgments: 0 },
  })

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-5">
      <h2 className="text-lg font-semibold text-gray-900">Business Credit Profile</h2>
      <p className="text-sm text-gray-500">All fields are optional. Provide whichever scores are available.</p>

      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Business Credit Scores</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="label">FICO SBSS</label>
            <input className="input" type="number" min="0" max="300" placeholder="160" {...register('fico_sbss', { valueAsNumber: true })} />
            <p className="mt-1 text-xs text-gray-400">0-300</p>
          </div>
          <div>
            <label className="label">Experian Intelliscore</label>
            <input className="input" type="number" min="1" max="100" placeholder="75" {...register('experian_intelliscore', { valueAsNumber: true })} />
            <p className="mt-1 text-xs text-gray-400">1-100</p>
          </div>
          <div>
            <label className="label">D&amp;B PAYDEX</label>
            <input className="input" type="number" min="0" max="100" placeholder="80" {...register('duns_paydex', { valueAsNumber: true })} />
            <p className="mt-1 text-xs text-gray-400">0-100</p>
          </div>
          <div>
            <label className="label">Years in Credit File</label>
            <input className="input" type="number" min="0" step="0.5" placeholder="5" {...register('years_in_file', { valueAsNumber: true })} />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Derogatory Marks</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="label">Bankruptcies</label>
            <input className="input" type="number" min="0" placeholder="0" {...register('bankruptcies', { valueAsNumber: true })} />
          </div>
          <div>
            <label className="label">Liens</label>
            <input className="input" type="number" min="0" placeholder="0" {...register('liens', { valueAsNumber: true })} />
          </div>
          <div>
            <label className="label">Judgments</label>
            <input className="input" type="number" min="0" placeholder="0" {...register('judgments', { valueAsNumber: true })} />
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-2">
        <button type="button" className="btn-secondary" onClick={onBack}>Back</button>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Next: Loan Request'}
        </button>
      </div>
    </form>
  )
}
