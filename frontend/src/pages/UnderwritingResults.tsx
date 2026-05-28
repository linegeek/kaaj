import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useUnderwritingRun } from '@/hooks/useUnderwriting'
import { CheckCircleIcon, XCircleIcon, MinusCircleIcon, ArrowLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'
import type { ProgramResult, CriteriaCheck } from '@/types'

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 80 ? 'bg-green-100 text-green-800' : score >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
  return (
    <div className={clsx('flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-full text-lg font-bold', color)}>
      {score.toFixed(0)}
    </div>
  )
}

function CriteriaRow({ c }: { c: CriteriaCheck }) {
  return (
    <tr className="border-t border-gray-100">
      <td className="py-2 pr-4 text-sm text-gray-900">{c.rule_name}</td>
      <td className="py-2 pr-4 text-xs text-gray-500">{c.rule_type.replace(/_/g, ' ')}</td>
      <td className="py-2 pr-4 text-sm text-gray-600">{c.weight.toFixed(1)}</td>
      <td className="py-2 pr-4">
        {c.skipped
          ? <span className="badge-skip">Skip</span>
          : c.passed
            ? <span className="badge-pass">Pass</span>
            : <span className="badge-fail">Fail</span>}
      </td>
      <td className="py-2 pr-4 text-xs text-gray-500">{c.actual_value ?? '-'}</td>
      <td className="py-2 text-xs text-gray-500">{c.reason}</td>
    </tr>
  )
}

function ProgramCard({ result }: { result: ProgramResult }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-4 p-5">
        <ScoreBadge score={result.fit_score} />
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 truncate">{result.lender_name}</p>
          <p className="text-sm text-gray-500 truncate">{result.program_name}</p>
          <div className="mt-2 flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1 text-green-700">
              <CheckCircleIcon className="h-3.5 w-3.5" />{result.passed_count} passed
            </span>
            <span className="flex items-center gap-1 text-red-700">
              <XCircleIcon className="h-3.5 w-3.5" />{result.failed_count} failed
            </span>
            <span className="flex items-center gap-1 text-gray-500">
              <MinusCircleIcon className="h-3.5 w-3.5" />{result.skipped_count} skipped
            </span>
          </div>
        </div>
        <button
          onClick={() => setOpen(o => !o)}
          className="ml-auto flex items-center gap-1 text-xs text-brand-600 hover:text-brand-800"
        >
          {open ? 'Hide' : 'Details'}
          {open ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
        </button>
      </div>
      {open && result.criteria.length > 0 && (
        <div className="border-t border-gray-100 px-5 pb-4 overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                {['Rule', 'Type', 'Weight', 'Result', 'Actual', 'Reason'].map(h => (
                  <th key={h} className="pb-2 pt-3 pr-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.criteria.map((c, i) => <CriteriaRow key={i} c={c} />)}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function UnderwritingResults() {
  const { runId } = useParams<{ runId: string }>()
  const { data: run, isLoading } = useUnderwritingRun(runId ?? '')

  if (isLoading || !run) {
    return <div className="text-sm text-gray-400 animate-pulse">Loading...</div>
  }

  const isPending = run.status === 'pending' || run.status === 'running'

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-gray-400 hover:text-gray-600">
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Underwriting Results</h1>
          <p className="text-sm text-gray-500">Application {run.application_id.slice(0, 8)}...</p>
        </div>
        <span className={clsx(
          'ml-auto rounded-full px-3 py-1 text-xs font-semibold',
          run.status === 'completed' && 'bg-green-100 text-green-800',
          run.status === 'running' && 'bg-blue-100 text-blue-800 animate-pulse',
          run.status === 'pending' && 'bg-gray-100 text-gray-600 animate-pulse',
          run.status === 'failed' && 'bg-red-100 text-red-800',
        )}>
          {run.status.toUpperCase()}
        </span>
      </div>

      {isPending && (
        <div className="card p-8 text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600 mb-4" />
          <p className="text-sm font-medium text-gray-700">Evaluating against all lender programs...</p>
          <p className="text-xs text-gray-400 mt-1">This usually takes a few seconds.</p>
        </div>
      )}

      {run.status === 'failed' && (
        <div className="card border-red-200 bg-red-50 p-5">
          <p className="text-sm font-medium text-red-800">Underwriting failed</p>
          <p className="text-xs text-red-600 mt-1">{run.error_message}</p>
        </div>
      )}

      {run.status === 'completed' && run.results && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              <span className="font-semibold text-gray-900">{run.results.length}</span> program{run.results.length !== 1 ? 's' : ''} evaluated, ranked by fit score
            </p>
            {run.completed_at && (
              <p className="text-xs text-gray-400">
                Completed {new Date(run.completed_at).toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="space-y-3">
            {(run.results as ProgramResult[]).map(r => (
              <ProgramCard key={r.program_id} result={r} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
