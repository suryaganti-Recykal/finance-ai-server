/**Premium Sidebar Layout */

import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode, useState } from 'react';
import { Menu, X, LayoutDashboard, Receipt, PieChart, Megaphone, FileText, Settings, TrendingUp } from 'lucide-react';

const navItems = [
  { href: '/',          label: 'Dashboard', icon: LayoutDashboard },
  { href: '/expenses',  label: 'Expenses',  icon: Receipt },
  { href: '/budgets',   label: 'Budgets',   icon: PieChart },
  { href: '/marketing', label: 'Marketing', icon: Megaphone },
  { href: '/reports',   label: 'Reports',   icon: FileText },
  { href: '/settings',  label: 'Settings',  icon: Settings },
];

export function Layout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const router = useRouter();

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--page-bg)' }}>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ background: 'var(--sidebar-bg)' }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-6 py-5" style={{ borderBottom: '1px solid var(--sidebar-border)' }}>
          <div className="flex items-center">
            <img src="/recykal-logo.svg" alt="Recykal" className="h-8 brightness-0 invert opacity-90" />
          </div>
          <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-white lg:hidden transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = router.pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setSidebarOpen(false)}
                className={`nav-item flex items-center gap-3 px-4 py-2.5 text-sm font-medium ${
                  isActive ? 'nav-item-active' : 'text-slate-400'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-emerald-400' : ''} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4" style={{ borderTop: '1px solid var(--sidebar-border)' }}>
          <div className="flex items-center gap-2 mb-1">
            <span className="animate-pulse-dot inline-block h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-xs font-semibold text-slate-300">Live Data · Recykal</span>
          </div>
          <p className="text-xs text-slate-500 pl-4">Marketing: Google Sheets</p>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">

        {/* Top header */}
        <header className="flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-md border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-slate-500 hover:text-slate-900 transition-colors lg:hidden"
            >
              <Menu size={22} />
            </button>
            <div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">Recykal Financial Dashboard</h2>
              <p className="text-xs text-slate-400 hidden sm:block">Real-time intelligence · Sustainable Circularity</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 border border-emerald-100">
              <span className="animate-pulse-dot inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Live
            </div>
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-bold shadow-md">
              SG
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
