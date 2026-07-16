/**Premium Dashboard Home Page — correctly typed from demo API */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, Hash, TrendingUp, Megaphone, AlertCircle, Calendar } from 'lucide-react';

interface Expense  { id: string; description: string; amount: number; category: string; date: string; merchant: string; source: string; }
interface Budget   { department: string; q1: string; q2: string; q3: string; q4: string; total: string; spent: string; remaining: string; status: string; }
interface Forecast { month: string; forecasted_expense: string; confidence: number; trend: string; }
interface DemoData { expenses: Expense[]; budgets: Budget[]; forecasts: Forecast[]; }
interface LiveMarketing { total_spend: number; by_segment: { name: string; value: number }[]; }

function formatDate(iso: string) {
  try { return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
  catch { return iso; }
}
function fmtINR(val: number) {
  if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)}Cr`;
  if (val >= 100000) return `₹${(val / 100000).toFixed(2)}L`;
  if (val >= 1000) return `₹${(val / 1000).toFixed(1)}K`;
  return `₹${val.toFixed(0)}`;
}

export default function DashboardPage() {
  const [data, setData]       = useState<DemoData | null>(null);
  const [liveMarketing, setLiveMarketing] = useState<LiveMarketing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      dashboardAPI.getDemoData(),
      dashboardAPI.getLiveMarketingSpend()
    ])
      .then(([demoRes, liveRes]) => {
        setData(demoRes.data.data);
        setLiveMarketing(liveRes.data.data);
      })
      .catch(e => setError(e.message || 'Failed to load'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <Layout>
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600" />
          <p className="text-sm font-medium text-slate-500">Loading dashboard…</p>
        </div>
      </div>
    </Layout>
  );

  if (error || !data) return (
    <Layout>
      <div className="glass-card flex items-start gap-4 p-5 !bg-red-50 border border-red-100">
        <AlertCircle className="mt-0.5 shrink-0 text-red-500" size={20} />
        <div>
          <p className="font-semibold text-red-900">Error loading data</p>
          <p className="mt-1 text-sm text-red-700">{error}</p>
        </div>
      </div>
    </Layout>
  );

  // ── Derived metrics (all values correctly typed) ──────────────────────────
  const totalExpenses   = data.expenses.reduce((s, e) => s + (e.amount || 0), 0);
  const totalMarketing  = liveMarketing ? liveMarketing.total_spend : 0;
  const expenseCount    = data.expenses.length;
  const avgExpense      = expenseCount > 0 ? totalExpenses / expenseCount : 0;
  const totalBudget     = data.budgets.reduce((s, b) => s + parseFloat(b.total || '0'), 0);
  const totalSpent      = data.budgets.reduce((s, b) => s + parseFloat(b.spent || '0'), 0);
  const budgetUtilPct   = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

  // ── Chart data ────────────────────────────────────────────────────────────
  const expensesByCategory = data.expenses.reduce((acc: { name: string; value: number }[], e) => {
    const existing = acc.find(i => i.name === e.category);
    if (existing) existing.value += e.amount;
    else acc.push({ name: e.category, value: e.amount });
    return acc;
  }, []);

  const marketingByPlatform = liveMarketing ? liveMarketing.by_segment : [];

  const forecastChartData = data.forecasts.map(f => ({
    name: f.month.split(' ')[0], // "July"
    value: parseFloat(f.forecasted_expense || '0'),
  }));

  return (
    <Layout>
      <div className="space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-400">Welcome back — here&apos;s your financial overview</p>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KPICard title="Total Expenses"    value={fmtINR(totalExpenses)}  trend="up"     trendPercent={12} icon={<DollarSign size={18}/>} colorIndex={0}/>
          <KPICard title="Transactions"      value={expenseCount}            trend="up"     trendPercent={5}  icon={<Hash size={18}/>}        colorIndex={1}/>
          <KPICard title="Marketing Spend"   value={fmtINR(totalMarketing)} trend="up"     trendPercent={8}  icon={<Megaphone size={18}/>}   colorIndex={2}/>
          <KPICard title="Budget Utilized"   value={`${budgetUtilPct.toFixed(1)}%`}
                   unit={`${fmtINR(totalSpent)} of ${fmtINR(totalBudget)}`} icon={<TrendingUp size={18}/>}  colorIndex={3}/>
        </div>

        {/* Charts row 1 */}
        <div className="grid gap-5 lg:grid-cols-2">
          <PieChartComponent  data={expensesByCategory}  title="Expenses by Category" />
          <BarChartComponent  data={marketingByPlatform} title="Live Marketing Spend by Segment (₹)" />
        </div>

        {/* Forecast chart */}
        {forecastChartData.length > 0 && (
          <LineChartComponent data={forecastChartData} title="3-Month Expense Forecast" />
        )}

        {/* Budget Allocation */}
        <div className="glass-card p-6">
          <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">Budget Allocation</h3>
          <div className="space-y-3">
            {data.budgets.map((budget, idx) => {
              const spent   = parseFloat(budget.spent  || '0');
              const total   = parseFloat(budget.total  || '0');
              const remaining = parseFloat(budget.remaining || '0');
              const pct     = total > 0 ? (spent / total) * 100 : 0;
              const status  = pct > 90 ? 'red' : pct > 70 ? 'amber' : 'emerald';
              const bar:    Record<string, string> = { red:'bg-red-500',    amber:'bg-amber-500',    emerald:'bg-emerald-500'    };
              const bg:     Record<string, string> = { red:'bg-red-50 border-red-100', amber:'bg-amber-50 border-amber-100', emerald:'bg-slate-50 border-slate-100' };
              const txt:    Record<string, string> = { red:'text-red-600',  amber:'text-amber-600',  emerald:'text-emerald-600'  };
              return (
                <div key={idx} className={`rounded-xl border p-4 ${bg[status]}`}>
                  <div className="mb-2 flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-slate-800 text-sm">{budget.department}</p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        <span className="font-medium text-slate-700">₹{spent.toLocaleString()}</span> spent · <span className="font-medium text-emerald-600">₹{remaining.toLocaleString()}</span> remaining of <span className="font-medium">₹{total.toLocaleString()}</span>
                      </p>
                    </div>
                    <span className={`text-base font-extrabold ${txt[status]}`}>{pct.toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
                    <div className={`h-full rounded-full transition-all duration-700 ${bar[status]}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  {/* Quarterly mini-grid */}
                  <div className="mt-3 grid grid-cols-4 gap-2">
                    {(['q1','q2','q3','q4'] as const).map(q => (
                      <div key={q} className="rounded-lg bg-white/70 p-2 text-center">
                        <p className="text-xs text-slate-400 font-medium uppercase">{q}</p>
                        <p className="text-sm font-bold text-slate-700">₹{(parseFloat((budget as any)[q]||'0')/1000).toFixed(0)}K</p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Expenses */}
        <div className="glass-card p-6">
          <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">Recent Expenses</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Description','Category','Amount','Date','Merchant'].map(h => (
                    <th key={h} className={`py-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider ${h==='Amount'?'text-right':'text-left'}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.expenses.map((exp, idx) => (
                  <tr key={idx} className="hover:bg-emerald-50/30 transition-colors">
                    <td className="px-3 py-3 font-medium text-slate-800">{exp.description}</td>
                    <td className="px-3 py-3">
                      <span className="inline-flex items-center rounded-full bg-emerald-50 border border-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">{exp.category}</span>
                    </td>
                    <td className="px-3 py-3 text-right font-bold text-slate-900">₹{(exp.amount||0).toLocaleString()}</td>
                    <td className="px-3 py-3 text-slate-400 text-xs whitespace-nowrap">{formatDate(exp.date)}</td>
                    <td className="px-3 py-3 text-slate-500 text-xs">{exp.merchant}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </Layout>
  );
}
