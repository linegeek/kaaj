import { useState } from 'react'
import { PencilIcon, TrashIcon, PlusIcon } from '@heroicons/react/24/outline'
import { useDeleteRule } from '@/hooks/useLenders'
import RuleFormModal from './RuleFormModal'
import type { EligibilityRule } from '@/types'

interface Props {
  lenderId: string
  programId: string
  rules: EligibilityRule[]
}

const CATEGORY_COLOR: Record<string, string> = {
  MIN_CREDIT_SCORE: 'text-blue-600', MAX_BANKRUPTCIES: 'text-blue-600',
  MIN_FICO_SBSS: 'text-blue-600', MIN_EXPERIAN_INTELLISCORE: 'text-blue-600',
  MIN_DUNS_PAYDEX: 'text-blue-600', MAX_DEROGATORY_MARKS: 'text-blue-600',
  MIN_YEARS_IN_BUSINESS: 'text-green-600', MIN_ANNUAL_REVENUE: 'text-green-600',
  ALLOWED_BUSINESS_TYPES: 'text-green-600', MIN_EMPLOYEE_COUNT: 'text-green-600',
  MAX_EMPLOYEE_COUNT: 'text-green-600', MIN_OWNERSHIP_PCT: 'text-green-600',
  NAICS_CODE_ALLOWLIST: 'text-green-600',
  ALLOWED_EQUIPMENT_TYPES: 'text-orange-600', MAX_EQUIPMENT_AGE_YRS: 'text-orange-600',
  MIN_LOAN_AMOUNT: 'text-orange-600', MAX_LOAN_AMOUNT: 'text-orange-600',
  MAX_TERM_MONTHS: 'text-orange-600', MIN_DOWN_PAYMENT_PCT: 'text-orange-600',
  ALLOWED_EQUIPMENT_CONDITIONS: 'text-orange-600',
  ALLOWED_STATES: 'text-purple-600', EXCLUDED_STATES: 'text-purple-600',
  MIN_CREDIT_SCORE_BY_STATE: 'text-purple-600', MAX_LOAN_AMOUNT_BY_STATE: 'text-purple-600',
  MIN_YEARS_IN_BUSINESS_BY_STATE: 'text-purple-600', ALLOWED_STATES_FOR_EQUIPMENT: 'text-purple-600',
}

export default function RulesTable({ lenderId, programId, rules }: Props) {
  const deleteRule = useDeleteRule(lenderId, programId)
  const [editRule, setEditRule] = useState<EligibilityRule | null>(null)
  const [showAdd, setShowAdd] = useState(false)

  return (
    <div>
      <div className="overflow-x-auto">
        {rules.length === 0 ? (
          <p className="py-4 text-center text-sm text-gray-400">No rules yet. Add your first rule below.</p>
        ) : (
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-100">
                {['Rule', 'Type', 'Weight', 'Parameters', ''].map(h => (
                  <th key={h} className="pb-2 pt-1 pr-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rules.map(rule => (
                <tr key={rule.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 pr-4 text-sm font-medium text-gray-900">
                    {rule.label || rule.rule_type.replace(/_/g, ' ')}
                  </td>
                  <td className={`py-2.5 pr-4 text-xs font-mono ${CATEGORY_COLOR[rule.rule_type] ?? 'text-gray-500'}`}>
                    {rule.rule_type}
                  </td>
                  <td className="py-2.5 pr-4 text-sm text-gray-600">{rule.weight.toFixed(1)}</td>
                  <td className="py-2.5 pr-4 text-xs text-gray-500 font-mono max-w-xs truncate">
                    {JSON.stringify(rule.parameters)}
                  </td>
                  <td className="py-2.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => setEditRule(rule)} className="text-gray-400 hover:text-brand-600">
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => { if (confirm('Delete this rule?')) deleteRule.mutate(rule.id) }}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="mt-3">
        <button className="btn-secondary text-xs px-3 py-1.5" onClick={() => setShowAdd(true)}>
          <PlusIcon className="h-3.5 w-3.5" /> Add Rule
        </button>
      </div>

      {showAdd && (
        <RuleFormModal lenderId={lenderId} programId={programId} onClose={() => setShowAdd(false)} />
      )}
      {editRule && (
        <RuleFormModal lenderId={lenderId} programId={programId} rule={editRule} onClose={() => setEditRule(null)} />
      )}
    </div>
  )
}
