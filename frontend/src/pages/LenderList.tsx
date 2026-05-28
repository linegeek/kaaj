import { useState } from 'react'
import { Link } from 'react-router-dom'
import { PlusIcon, BuildingLibraryIcon } from '@heroicons/react/24/outline'
import { useLenders, useCreateLender, useDeleteLender } from '@/hooks/useLenders'
import type { LenderCreatePayload } from '@/types'

function AddLenderModal({ onClose }: { onClose: () => void }) {
  const create = useCreateLender()
  const [form, setForm] = useState<LenderCreatePayload>({ name: '' })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await create.mutateAsync(form)
    onClose()
  }

  const f = (field: keyof LenderCreatePayload) => ({
    value: (form[field] as string) ?? '',
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(p => ({ ...p, [field]: e.target.value })),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="card w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Add Lender</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Lender Name *</label>
            <input className="input" required placeholder="Apex Equipment Finance" {...f('name')} />
          </div>
          <div>
            <label className="label">Contact Email</label>
            <input className="input" type="email" placeholder="deals@lender.com" {...f('contact_email')} />
          </div>
          <div>
            <label className="label">Contact Phone</label>
            <input className="input" placeholder="800-555-0100" {...f('contact_phone')} />
          </div>
          <div>
            <label className="label">Notes</label>
            <textarea className="input" rows={3} placeholder="Brief description of lender..." {...f('notes')} />
          </div>
          {create.isError && <p className="text-sm text-red-600">Failed to create. Please try again.</p>}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={create.isPending}>
              {create.isPending ? 'Adding...' : 'Add Lender'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function LenderList() {
  const { data: lenders = [], isLoading } = useLenders()
  const deleteLender = useDeleteLender()
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lenders</h1>
          <p className="mt-1 text-sm text-gray-500">Manage lenders, programs, and eligibility rules.</p>
        </div>
        <button className="btn-primary" onClick={() => setShowAdd(true)}>
          <PlusIcon className="h-4 w-4" /> Add Lender
        </button>
      </div>

      {isLoading && <p className="text-sm text-gray-400 animate-pulse">Loading...</p>}

      {!isLoading && lenders.length === 0 && (
        <div className="card p-10 text-center">
          <BuildingLibraryIcon className="mx-auto h-10 w-10 text-gray-300 mb-3" />
          <p className="text-sm font-medium text-gray-600">No lenders yet</p>
          <p className="text-xs text-gray-400 mt-1">Add a lender to get started.</p>
        </div>
      )}

      <div className="space-y-3">
        {lenders.map(lender => (
          <div key={lender.id} className="card flex items-center gap-4 p-4 hover:border-brand-200 transition-colors">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50">
              <BuildingLibraryIcon className="h-5 w-5 text-brand-600" />
            </div>
            <div className="flex-1 min-w-0">
              <Link to={`/lenders/${lender.id}`} className="font-medium text-gray-900 hover:text-brand-600">
                {lender.name}
              </Link>
              {lender.contact_email && (
                <p className="text-xs text-gray-500 mt-0.5">{lender.contact_email}</p>
              )}
            </div>
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${lender.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
              {lender.is_active ? 'Active' : 'Inactive'}
            </span>
            <Link to={`/lenders/${lender.id}`} className="btn-secondary text-xs px-3 py-1.5">
              Manage
            </Link>
            <button
              className="text-red-400 hover:text-red-600 text-xs"
              onClick={() => {
                if (confirm(`Delete ${lender.name}? This cannot be undone.`)) {
                  deleteLender.mutate(lender.id)
                }
              }}
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {showAdd && <AddLenderModal onClose={() => setShowAdd(false)} />}
    </div>
  )
}
