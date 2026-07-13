/**Premium Budgets Page — all string values safely parsed */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { dashboardAPI } from '@/lib/api';
import { AlertCircle, CheckCircle, AlertTriangle, PieChart } from 'lucide-react';

interface Budget {
  department: string; q1: string; q2: string; q3: string; q4: string;
  total: string; spent: string; remaining: string; status: string;
}

const DEPT_COLORS: Record<string, string> = {
  Marketing:   'from-teal-500 to-emerald-500',
  Operations:  'from-sky-500 to-cyan-500',
  Engineering: 'from-emerald-500 to-teal-500',
  Sales:       'from-amber-500 to-orange-500',
};

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.getDemoBudgets()
      .then(r => setBudgets(r.data.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalBudget    = budgets.reduce((s, b) => s + parseFloat(b.total || '0'), 0);
  const totalSpent     = budgets.reduce((s, b) => s + parseFloat(b.spent || '0'), 0);
  const totalRemaining = budgets.reduce((s, b) => s + parseFloat(b.remaining || '0'), 0);
  const overallPct     = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

  const getIcon = (pct: number) => {
    if (pct > 90) return <AlertCircle className="text-red-500" size={20}/>;
    if (pct > 70) return <AlertTriangle className="text-amber-500" size={20}/>;
    return <CheckCircle className="text-emerald-500" size={20}/>;
  };

  return (
    <Layout>
      <div className="space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Budget Management</h1>
          <p className="mt-1 text-sm text-slate-400">Track departmental allocations and spending</p>
        </div>

        {/* Overall summary */}
        <div className="glass-card p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Overall Budget Utilization</p>
              <p className="mt-2 text-4xl font-extrabold text-slate-900">{overallPct.toFixed(1)}<span className="text-2xl text-slate-400">%</span></p>
              <div className="mt-1 flex gap-4 text-sm">
                <span className="text-slate-500">Spent: <span className="font-bold text-slate-800">₹{totalSpent.toLocaleString()}</span></span>
                <span className="text-slate-500">Remaining: <span className="font-bold text-emerald-600">₹{totalRemaining.toLocaleString()}</span></span>
                <span className="text-slate-500">Total: <span className="font-bold text-slate-800">₹{totalBudget.toLocaleString()}</span></span>
              </div>
            </div>
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full" style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
              <PieChart className="text-white" size={36}/>
            </div>
          </div>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(overallPct, 100)}%`, background: 'linear-gradient(90deg, #6366f1, #8b5cf6)' }}
            />
          </div>
        </div>

        {/* Department cards */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600"/>
          </div>
        ) : (
          <div className="grid gap-5 lg:grid-cols-2">
            {budgets.map((budget, idx) => {
              const spent     = parseFloat(budget.spent     || '0');
              const total     = parseFloat(budget.total     || '0');
              const remaining = parseFloat(budget.remaining || '0');
              const pct       = total > 0 ? (spent / total) * 100 : 0;
              const status    = pct > 90 ? 'red' : pct > 70 ? 'amber' : 'emerald';
              const barColor: Record<string,string> = { red: '#ef4444', amber: '#f59e0b', emerald: '#10b981' };
              const gradient  = DEPT_COLORS[budget.department] || 'from-slate-500 to-slate-600';

              return (
                <div key={idx} className="glass-card p-6">
                  {/* Dept header */}
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} text-white text-sm font-bold shadow-md`}>
                        {budget.department.slice(0,2).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-bold text-slate-900">{budget.department}</p>
                        <p className="text-xs text-slate-400">FY 2026 Budget</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getIcon(pct)}
                      <span className={`text-xl font-extrabold ${
                        status==='red' ? 'text-red-600' : status==='amber' ? 'text-amber-600' : 'text-emerald-600'
                      }`}>{pct.toFixed(1)}%</span>
                    </div>
                  </div>

                  {/* Spend vs total */}
                  <div className="mb-3 flex items-center justify-between text-sm">
                    <span className="text-slate-500">
                      Spent: <span className="font-bold text-slate-800">₹{spent.toLocaleString()}</span>
                    </span>
                    <span className="text-slate-500">
                      Remaining: <span className="font-bold text-emerald-600">₹{remaining.toLocaleString()}</span>
                    </span>
                    <span className="text-slate-500">
                      Total: <span className="font-bold text-slate-700">₹{total.toLocaleString()}</span>
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="mb-4 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${Math.min(pct, 100)}%`, background: barColor[status] }}
                    />
                  </div>

                  {/* Quarterly breakdown */}
                  <div className="grid grid-cols-4 gap-2">
                    {(['q1','q2','q3','q4'] as const).map(q => {
                      const qval = parseFloat((budget as any)[q] || '0');
                      return (
                        <div key={q} className="rounded-lg bg-slate-50 border border-slate-100 p-2.5 text-center">
                          <p className="text-xs font-semibold uppercase text-slate-400">{q}</p>
                          <p className="mt-0.5 text-sm font-extrabold text-slate-700">
                            ${qval >= 1000 ? `${(qval/1000).toFixed(0)}K` : qval}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Legend */}
        <div className="glass-card p-5">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Status Legend</p>
          <div className="flex flex-wrap gap-4">
            {[
              { icon: <CheckCircle size={16} className="text-emerald-500"/>, label: 'On Track', sub: '< 70% utilized' },
              { icon: <AlertTriangle size={16} className="text-amber-500"/>, label: 'Warning',  sub: '70–90% utilized' },
              { icon: <AlertCircle  size={16} className="text-red-500"/>,   label: 'Critical', sub: '> 90% utilized' },
            ].map(({ icon, label, sub }) => (
              <div key={label} className="flex items-center gap-2">
                {icon}
                <div>
                  <p className="text-sm font-semibold text-slate-700">{label}</p>
                  <p className="text-xs text-slate-400">{sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </Layout>
  );
}
