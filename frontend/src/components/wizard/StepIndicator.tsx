import clsx from 'clsx'
import { CheckIcon } from '@heroicons/react/24/solid'

const STEPS = [
  'Business Info',
  'Guarantor',
  'Credit Data',
  'Loan Request',
  'Review',
]

interface Props {
  current: number // 1-indexed
}

export default function StepIndicator({ current }: Props) {
  return (
    <nav aria-label="Progress" className="mb-8">
      <ol className="flex items-center">
        {STEPS.map((label, idx) => {
          const step = idx + 1
          const done = step < current
          const active = step === current

          return (
            <li key={label} className={clsx('flex items-center', idx < STEPS.length - 1 && 'flex-1')}>
              <div className="flex flex-col items-center">
                <div
                  className={clsx(
                    'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors',
                    done && 'bg-brand-600 text-white',
                    active && 'border-2 border-brand-600 bg-white text-brand-600',
                    !done && !active && 'border-2 border-gray-300 bg-white text-gray-400',
                  )}
                >
                  {done ? <CheckIcon className="h-4 w-4" /> : step}
                </div>
                <span
                  className={clsx(
                    'mt-1 hidden text-xs font-medium sm:block whitespace-nowrap',
                    active ? 'text-brand-600' : done ? 'text-gray-600' : 'text-gray-400',
                  )}
                >
                  {label}
                </span>
              </div>
              {idx < STEPS.length - 1 && (
                <div className={clsx('h-0.5 flex-1 mx-2 mb-5', done ? 'bg-brand-600' : 'bg-gray-200')} />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
