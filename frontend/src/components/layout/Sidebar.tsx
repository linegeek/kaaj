import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  PlusCircleIcon,
  BuildingLibraryIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

const nav = [
  { to: '/', label: 'Dashboard', icon: HomeIcon, end: true },
  { to: '/applications/new', label: 'New Application', icon: PlusCircleIcon, end: false },
  { to: '/lenders', label: 'Lenders', icon: BuildingLibraryIcon, end: false },
]

export default function Sidebar() {
  return (
    <aside className="flex w-60 flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <span className="text-sm font-bold text-white">K</span>
        </div>
        <span className="text-lg font-semibold text-gray-900">Kaaj</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {nav.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
              )
            }
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 px-5 py-4">
        <p className="text-xs text-gray-400">Equipment Finance Platform</p>
      </div>
    </aside>
  )
}
