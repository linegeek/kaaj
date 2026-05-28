import { useState } from 'react'
import { ChevronDownIcon, ChevronUpIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'
import { useProgram, useDeleteProgram } from '@/hooks/useLenders'
import RulesTable from './RulesTable'
import ProgramFormModal from './ProgramFormModal'
import type { LenderProgram } from '@/types'
import clsx from 'clsx'

interface ProgramRowProps {
  lenderId: string
  program: LenderProgram
}

function ProgramRow({ lenderId, program }: ProgramRowProps) {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(false)
  const deleteProgram = useDeleteProgram(lenderId)
  const { data: detail } = useProgram(lenderId, program.id)

  return (
    <div className="rounded-lg border border-gray-200 overflow-hidden">
      <div className="flex items-center gap-3 bg-gray-50 px-4 py-3">
        <button onClick={() => setOpen(o => !o)} className="flex-1 flex items-center gap-2 text-left">
          {open ? <ChevronUpIcon className="h-4 w-4 text-gray-400" /> : <ChevronDownIcon className="h-4 w-4 text-gray-400" />}
          <span className="font-medium text-gray-900 text-sm">{program.name}</span>
          <span className={clsx('ml-2 rounded-full px-2 py-0.5 text-xs font-medium', program.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500')}>
            {program.is_active ? 'Active' : 'Inactive'}
          </span>
          {program.min_amount && program.max_amount && (
            <span className="text-xs text-gray-400 ml-2">
              ${program.min_amount.toLocaleString()} - ${program.max_amount.toLocaleString()}
            </span>
          )}
        </button>
        <button onClick={() => setEditing(true)} className="text-gray-400 hover:text-brand-600 p-1">
          <PencilIcon className="h-4 w-4" />
        </button>
        <button
          onClick={() => { if (confirm(`Delete program "${program.name}"?`)) deleteProgram.mutate(program.id) }}
          className="text-gray-400 hover:text-red-600 p-1"
        >
          <TrashIcon className="h-4 w-4" />
        </button>
      </div>

      {open && (
        <div className="px-4 pb-4 pt-3">
          {program.description && (
            <p className="text-sm text-gray-500 mb-3">{program.description}</p>
          )}
          <RulesTable
            lenderId={lenderId}
            programId={program.id}
            rules={detail?.rules ?? []}
          />
        </div>
      )}

      {editing && (
        <ProgramFormModal lenderId={lenderId} program={program} onClose={() => setEditing(false)} />
      )}
    </div>
  )
}

interface Props {
  lenderId: string
  programs: LenderProgram[]
}

export default function ProgramList({ lenderId, programs }: Props) {
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div className="space-y-3">
      {programs.length === 0 && (
        <p className="text-sm text-gray-400 py-4 text-center">No programs yet.</p>
      )}
      {programs.map(p => (
        <ProgramRow key={p.id} lenderId={lenderId} program={p} />
      ))}
      <button className="btn-secondary text-sm" onClick={() => setShowAdd(true)}>
        <PlusIcon className="h-4 w-4" /> Add Program
      </button>
      {showAdd && <ProgramFormModal lenderId={lenderId} onClose={() => setShowAdd(false)} />}
    </div>
  )
}
