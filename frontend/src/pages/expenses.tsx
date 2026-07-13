/**Premium Expenses Page — correctly typed data */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, Receipt, TrendingUp, Download } from 'lucide-react';

interface Expense {
  id: string; description: string; amount: number;
  category: string; date: string; merchant: string; source: string; currency?: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  Operations: 'bg-sky-50 text-sky-700 border-sky-100',
  Marketing:  'bg-teal-50 text-teal-700 border-teal-100',
  Engineering:'bg-emerald-50 text-emerald-700 border-emerald-100',
  Sales:      'bg-amber-50 text-amber-700 border-amber-100',
};
const defaultBadge = 'bg-slate-50 text-slate-700 border-slate-200';

function formatDate(iso: string) {
  try { return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
  catch { return iso; }
}

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState('');
  const [filterCat, setFilter]  = useState('All');

  useEffect(() => {
    dashboardAPI.getDemoExpenses()
      .then(r => setExpenses(r.data.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const categories = ['All', ...Array.from(new Set(expenses.map(e => e.category)))];
  const filtered   = expenses.filter(e =>
    (filterCat === 'All' || e.category === filterCat) &&
    (search === '' || e.description.toLowerCase().includes(search.toLowerCase()) || e.merchant?.toLowerCase().includes(search.toLowerCase()))
  );

  const total    = filtered.reduce((s, e) => s + (e.amount || 0), 0);
  const average  = filtered.length > 0 ? total / filtered.length : 0;
  const highest  = filtered.reduce((max, e) => (e.amount || 0) > max ? (e.amount || 0) : max, 0);

  return (
    <Layout>
      <div className="space-y-6">

        {/* Header */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Expenses</h1>
            <p className="mt-1 text-sm text-slate-400">{expenses.length} transactions recorded</p>
          </div>
          <button className="inline-flex w-fit items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-emerald-200 hover:bg-emerald-700 transition-colors">
            <Download size={16} /> Export CSV
          </button>
        </div>

        {/* KPI mini-cards */}
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="glass-card p-4 flex items-center gap-4">
            <div className="kpi-icon-emerald flex h-10 w-10 items-center justify-center rounded-xl text-white"><DollarSign size={18}/></div>
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide">Total</p>
              <p className="text-xl font-extrabold text-slate-900">${total.toLocaleString()}</p>
            </div>
          </div>
          <div className="glass-card p-4 flex items-center gap-4">
            <div className="kpi-icon-emerald flex h-10 w-10 items-center justify-center rounded-xl text-white"><TrendingUp size={18}/></div>
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide">Average</p>
              <p className="text-xl font-extrabold text-slate-900">${average.toFixed(0)}</p>
            </div>
          </div>
          <div className="glass-card p-4 flex items-center gap-4">
            <div className="kpi-icon-amber flex h-10 w-10 items-center justify-center rounded-xl text-white"><Receipt size={18}/></div>
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide">Largest</p>
              <p className="text-xl font-extrabold text-slate-900">${highest.toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="text"
            placeholder="Search expenses…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 shadow-sm outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 sm:max-w-xs"
          />
          <div className="flex gap-2 flex-wrap">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-all ${
                  filterCat === cat
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-200'
                    : 'bg-white text-slate-500 border border-slate-200 hover:border-emerald-300 hover:text-emerald-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="glass-card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/60">
                  {['Description','Category','Amount','Date','Merchant','Source'].map(h => (
                    <th key={h} className={`px-5 py-3 text-xs font-semibold uppercase tracking-wider text-slate-400 ${h==='Amount'?'text-right':'text-left'}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {loading ? (
                  <tr><td colSpan={6} className="py-12 text-center"><div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600"/></td></tr>
                ) : filtered.length === 0 ? (
                  <tr><td colSpan={6} className="py-12 text-center text-slate-400">No expenses found</td></tr>
                ) : filtered.map((exp, idx) => (
                  <tr key={idx} className="hover:bg-emerald-50/20 transition-colors">
                    <td className="px-5 py-3.5 font-medium text-slate-800">{exp.description}</td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${CATEGORY_COLORS[exp.category] || defaultBadge}`}>
                        {exp.category}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right font-bold text-slate-900">${(exp.amount||0).toLocaleString()}</td>
                    <td className="px-5 py-3.5 text-xs text-slate-400 whitespace-nowrap">{formatDate(exp.date)}</td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">{exp.merchant || '—'}</td>
                    <td className="px-5 py-3.5 text-xs text-slate-400">{exp.source?.replace(/_/g,' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!loading && (
            <div className="border-t border-slate-100 bg-slate-50/60 px-5 py-3 flex items-center justify-between">
              <p className="text-xs text-slate-400">{filtered.length} of {expenses.length} expenses</p>
              <p className="text-xs font-semibold text-slate-600">Total: <span className="text-emerald-600">${total.toLocaleString()}</span></p>
            </div>
          )}
        </div>

      </div>
    </Layout>
  );
}
