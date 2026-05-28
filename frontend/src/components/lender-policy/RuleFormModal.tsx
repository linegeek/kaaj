import { useState, useEffect } from 'react'
import { useRuleTypes } from '@/hooks/useReference'
import { useCreateRule, useUpdateRule } from '@/hooks/useLenders'
import type { EligibilityRule, RuleCreatePayload } from '@/types'

interface Props {
  lenderId: string
  programId: string
  rule?: EligibilityRule
  onClose: () => void
}

function ParamField({
  paramKey, schema, value, onChange,
}: {
  paramKey: string
  schema: string
  value: unknown
  onChange: (v: unknown) => void
}) {
  const label = paramKey.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

  if (schema === 'integer' || schema === 'number') {
    return (
      <div>
        <label className="label">{label}</label>
        <input
          className="input"
          type="number"
          step={schema === 'number' ? '0.5' : '1'}
          value={(value as number) ?? ''}
          onChange={e => onChange(schema === 'number' ? parseFloat(e.target.value) : parseInt(e.target.value, 10))}
        />
      </div>
    )
  }

  if (schema === 'array[string]') {
    const arrVal = Array.isArray(value) ? (value as string[]).join(', ') : ''
    return (
      <div>
        <label className="label">{label}</label>
        <input
          className="input"
          placeholder="Comma-separated values, e.g. TX, CA, FL"
          value={arrVal}
          onChange={e => onChange(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
        />
        <p className="mt-1 text-xs text-gray-400">Enter comma-separated values</p>
      </div>
    )
  }

  // object or complex — use JSON textarea
  return (
    <div>
      <label className="label">{label}</label>
      <textarea
        className="input font-mono text-xs"
        rows={4}
        placeholder={`{"TX": 620, "CA": 650}`}
        value={typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value ?? '')}
        onChange={e => {
          try { onChange(JSON.parse(e.target.value)) } catch { onChange(e.target.value) }
        }}
      />
      <p className="mt-1 text-xs text-gray-400">Schema: {schema}</p>
    </div>
  )
}

export default function RuleFormModal({ lenderId, programId, rule, onClose }: Props) {
  const { data: ruleTypes = [] } = useRuleTypes()
  const createRule = useCreateRule(lenderId, programId)
  const updateRule = useUpdateRule(lenderId, programId, rule?.id ?? '')

  const [ruleType, setRuleType] = useState(rule?.rule_type ?? '')
  const [label, setLabel] = useState(rule?.label ?? '')
  const [weight, setWeight] = useState(rule?.weight ?? 1.0)
  const [params, setParams] = useState<Record<string, unknown>>(
    (rule?.parameters as Record<string, unknown>) ?? {}
  )

  const meta = ruleTypes.find(rt => rt.rule_type === ruleType)

  useEffect(() => {
    if (ruleType && !rule) setParams({})
  }, [ruleType, rule])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload: RuleCreatePayload = { rule_type: ruleType, label: label || undefined, weight, parameters: params }
    if (rule) {
      await updateRule.mutateAsync(payload)
    } else {
      await createRule.mutateAsync(payload)
    }
    onClose()
  }

  const isSaving = createRule.isPending || updateRule.isPending
  const isError = createRule.isError || updateRule.isError

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{rule ? 'Edit Rule' : 'Add Rule'}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Rule Type *</label>
            <select className="input" required value={ruleType} onChange={e => setRuleType(e.target.value)} disabled={!!rule}>
              <option value="">Select rule type...</option>
              {['credit', 'business', 'equipment', 'geographic'].map(cat => (
                <optgroup key={cat} label={cat.toUpperCase()}>
                  {ruleTypes.filter(rt => rt.category === cat).map(rt => (
                    <option key={rt.rule_type} value={rt.rule_type}>{rt.label}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Label (optional override)</label>
            <input className="input" placeholder={meta?.label ?? 'Display name...'} value={label} onChange={e => setLabel(e.target.value)} />
          </div>

          <div>
            <label className="label">Weight</label>
            <input className="input" type="number" min="0.1" max="5" step="0.5" value={weight} onChange={e => setWeight(parseFloat(e.target.value))} />
            <p className="mt-1 text-xs text-gray-400">Higher weight = more impact on fit score (typical: 1.0-3.0)</p>
          </div>

          {meta && Object.entries(meta.param_schema).map(([key, schema]) => (
            <ParamField
              key={key}
              paramKey={key}
              schema={schema}
              value={params[key]}
              onChange={v => setParams(p => ({ ...p, [key]: v }))}
            />
          ))}

          {isError && <p className="text-sm text-red-600">Failed to save. Please check your inputs.</p>}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={isSaving || !ruleType}>
              {isSaving ? 'Saving...' : rule ? 'Update Rule' : 'Add Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
