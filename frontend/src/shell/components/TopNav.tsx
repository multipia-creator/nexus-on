/**
 * TopNav Component - NEXUS UI v1.1
 * Global navigation bar with active state highlighting
 */

import React from 'react'
import { Home, BookOpen, User, Package, BarChart3, AppWindow } from 'lucide-react'

interface TopNavProps {
  currentView: 'stage' | 'dashboard' | 'youtube' | 'nodes'
  onViewChange: (view: 'stage' | 'dashboard' | 'youtube') => void
}

export function TopNav({ currentView, onViewChange }: TopNavProps) {
  const navItems = [
    { id: 'stage', label: 'Stage', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'youtube', label: 'YouTube', icon: AppWindow },
  ] as const

  return (
    <nav className="topnav">
      <div className="topnav-brand">NEXUS-ON</div>
      <div className="topnav-items">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.id
          return (
            <button
              key={item.id}
              className={`topnav-link ${isActive ? 'active' : ''}`}
              onClick={() => onViewChange(item.id)}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon size={20} strokeWidth={1.75} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
