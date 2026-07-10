/**Main Layout Component */

import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { ReactNode, useState } from 'react';

export function Layout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-gray-900 text-white transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between border-b border-gray-700 p-4">
            <h1 className="text-xl font-bold">Finance AI</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
            >
              <X size={24} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {[
              { href: '/', label: 'Dashboard', icon: '📊' },
              { href: '/expenses', label: 'Expenses', icon: '💰' },
              { href: '/budgets', label: 'Budgets', icon: '📈' },
              { href: '/marketing', label: 'Marketing', icon: '📢' },
              { href: '/reports', label: 'Reports', icon: '📋' },
              { href: '/settings', label: 'Settings', icon: '⚙️' },
            ].map(({ href, label, icon }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-3 rounded-lg px-4 py-2 hover:bg-gray-800"
              >
                <span>{icon}</span>
                <span>{label}</span>
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="border-t border-gray-700 p-4 text-sm text-gray-400">
            <p>Demo Mode</p>
            <p className="text-xs">Company: demo-company-001</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              <Menu size={24} />
            </button>
            <h2 className="text-2xl font-bold text-gray-900">Finance AI Dashboard</h2>
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-gray-200" />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
