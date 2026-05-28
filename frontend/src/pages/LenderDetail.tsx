import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeftIcon, PencilIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline'
import { useLender, useUpdateLender } from '@/hooks/useLenders'
import ProgramList from '@/components/lender-policy/ProgramList'
import PdfUploadModal from '@/components/lender-policy/PdfUploadModal'
import type { LenderUpdatePayload } from '@/types'

function EditLenderModal({ lenderId, onClose }: { lenderId: string; onClose: () => void }) {
  const { data: lender } = useLender(lenderId)
  const update = useUpdateLender(lenderId)
  const [form, setForm] = useState<LenderUpdatePayload>({
    name: lender?.name ?? '',
    contact_email: lender?.contact_email ?? '',
    contact_phone: lender?.contact_phone ?? '',
    notes: lender?.notes ?? '',
    is_active: lender?.is_active ?? true,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await update.mutateAsync(form)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="card w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Edit Lender</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Name *</label>
            <input className="input" required value={form.name ?? ''} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
          </div>
          <div>
            <label className="label">Contact Email</label>
            <input className="input" type="email" value={form.contact_email ?? ''} onChange={e => setForm(p => ({ ...p, contact_email: e.target.value }))} />
          </div>
          <div>
            <label className="label">Contact Phone</label>
            <input className="input" value={form.contact_phone ?? ''} onChange={e => setForm(p => ({ ...p, contact_phone: e.target.value }))} />
          </div>
          <div>
            <label className="label">Notes</label>
            <textarea className="input" rows={3} value={form.notes ?? ''} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} />
          </div>
          <div className="flex items-center gap-2">
            <input id="active" type="checkbox" className="h-4 w-4 rounded border-gray-300 text-brand-600"
              checked={form.is_active ?? true}
              onChange={e => setForm(p => ({ ...p, is_active: e.target.checked }))} />
            <label htmlFor="active" className="text-sm text-gray-700">Active</label>
          </div>
          {update.isError && <p className="text-sm text-red-600">Failed to update.</p>}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={update.isPending}>
              {update.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function LenderDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: lender, isLoading } = useLender(id ?? '')
  const [showEdit, setShowEdit] = useState(false)
  const [showPdf, setShowPdf] = useState(false)

  if (isLoading) return <div className="text-sm text-gray-400 animate-pulse">Loading...</div>
  if (!lender) return <div className="text-sm text-red-500">Lender not found.</div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <Link to="/lenders" className="mt-1 text-gray-400 hover:text-gray-600">
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{lender.name}</h1>
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${lender.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
              {lender.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
            {lender.contact_email && <span>{lender.contact_email}</span>}
            {lender.contact_phone && <span>{lender.contact_phone}</span>}
          </div>
          {lender.notes && <p className="mt-2 text-sm text-gray-600 max-w-2xl">{lender.notes}</p>}
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary text-sm" onClick={() => setShowPdf(true)}>
            <DocumentArrowUpIcon className="h-4 w-4" /> Import PDF
          </button>
          <button className="btn-secondary text-sm" onClick={() => setShowEdit(true)}>
            <PencilIcon className="h-4 w-4" /> Edit
          </button>
        </div>
      </div>

      {/* Programs */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Programs
          <span className="ml-2 text-sm font-normal text-gray-400">({lender.programs.length})</span>
        </h2>
        <ProgramList lenderId={lender.id} programs={lender.programs} />
      </div>

      {showEdit && <EditLenderModal lenderId={lender.id} onClose={() => setShowEdit(false)} />}
      {showPdf && <PdfUploadModal lenderId={lender.id} onClose={() => setShowPdf(false)} />}
    </div>
  )
}
