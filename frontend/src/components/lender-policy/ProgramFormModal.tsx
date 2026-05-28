import { useState } from 'react'
import { useCreateProgram, useUpdateProgram } from '@/hooks/useLenders'
import type { LenderProgram, ProgramCreatePayload } from '@/types'

interface Props {
  lenderId: string
  program?: LenderProgram
  onClose: () => void
}

export default function ProgramFormModal({ lenderId, program, onClose }: Props) {
  const createProgram = useCreateProgram(lenderId)
  const updateProgram = useUpdateProgram(lenderId, program?.id ?? '')

  const [form, setForm] = useState<ProgramCreatePayload>({
    name: program?.name ?? '',
    description: program?.description ?? '',
    min_amount: program?.min_amount ?? undefined,
    max_amount: program?.max_amount ?? undefined,
    is_active: program?.is_active ?? true,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (program) {
      await updateProgram.mutateAsync(form)
    } else {
      await createProgram.mutateAsync(form)
    }
    onClose()
  }

  const isSaving = createProgram.isPending || updateProgram.isPending
  const isError = createProgram.isError || updateProgram.isError

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="card w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {program ? 'Edit Program' : 'Add Program'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Program Name *</label>
            <input
              className="input"
              required
              placeholder="Standard Commercial Program"
              value={form.name}
              onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea
              className="input"
              rows={3}
              placeholder="Brief description of this lending program..."
              value={form.description ?? ''}
              onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Min Amount ($)</label>
              <input
                className="input"
                type="number"
                min="0"
                placeholder="10000"
                value={form.min_amount ?? ''}
                onChange={e => setForm(p => ({ ...p, min_amount: e.target.value ? parseFloat(e.target.value) : undefined }))}
              />
            </div>
            <div>
              <label className="label">Max Amount ($)</label>
              <input
                className="input"
                type="number"
                min="0"
                placeholder="500000"
                value={form.max_amount ?? ''}
                onChange={e => setForm(p => ({ ...p, max_amount: e.target.value ? parseFloat(e.target.value) : undefined }))}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              id="is_active"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-brand-600"
              checked={form.is_active}
              onChange={e => setForm(p => ({ ...p, is_active: e.target.checked }))}
            />
            <label htmlFor="is_active" className="text-sm text-gray-700">Active (included in underwriting)</label>
          </div>

          {isError && <p className="text-sm text-red-600">Failed to save. Please try again.</p>}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={isSaving}>
              {isSaving ? 'Saving...' : program ? 'Update' : 'Add Program'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
