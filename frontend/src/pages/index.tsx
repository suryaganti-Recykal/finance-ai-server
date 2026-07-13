/**Premium Dashboard Home Page */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, Hash, TrendingUp, Megaphone, AlertCircle } from 'lucide-react';

interface DemoData {
  expenses: Array<any>;
  marketing: Array<any>;
  budgets: Array<any>;
  forecasts: Array<any>;
}

const BAR_COLORS: Record<number, string> = { 0: 'bg-indigo-500', 1: 'bg-emerald-500', 2: 'bg-amber-500', 3: 'bg-rose-500' };

export default function DashboardPage() {
  const [data, setData] = useState<DemoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getDemoData();
        setData(response.data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout>
        <div className="flex h-64 items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-indigo-100 border-t-indigo-600" />
            <p className="text-sm font-medium text-slate-500">Loading dashboard…</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="glass-card flex items-start gap-4 p-5 border border-red-100 !bg-red-50">
          <AlertCircle className="mt-0.5 text-red-500 shrink-0" size={20} />
          <div>
            <p className="font-semibold text-red-900">Error loading data</p>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!data) return <Layout><div className="text-slate-500">No data available</div></Layout>;

  const totalExpenses = data.expenses.reduce((s, e) => s + parseFloat(e.amount || 0), 0);
  const totalMarketing = data.marketing.reduce((s, c) => s + parseFloat(c.spend || 0), 0);
  const expenseCount = data.expenses.length;
  const avgExpense = expenseCount > 0 ? totalExpenses / expenseCount : 0;

  const expensesByCategory = data.expenses.reduce((acc, exp) => {
    const existing = acc.find((i: any) => i.name === exp.category);
    if (existing) existing.value += parseFloat(exp.amount || 0);
    else acc.push({ name: exp.category, value: parseFloat(exp.amount || 0) });
    return acc;
  }, [] as Array<{ name: string; value: number }>);

  const marketingByPlatform = data.marketing.map((c: any) => ({ name: c.platform, value: parseFloat(c.spend || 0) }));

  return (
    <Layout>
      <div className="space-y-6">

        {/* Page header */}
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-400">Expense &amp; budget overview at a glance</p>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KPICard title="Total Expenses"    value={`$${totalExpenses.toFixed(2)}`}    trend="up" trendPercent={12} icon={<DollarSign size={18} />} colorIndex={0} />
          <KPICard title="Transactions"      value={expenseCount}                       trend="up" trendPercent={5}  icon={<Hash size={18} />}        colorIndex={1} />
          <KPICard title="Avg Transaction"   value={`$${avgExpense.toFixed(2)}`}        trend="stable"               icon={<TrendingUp size={18} />}  colorIndex={2} />
          <KPICard title="Marketing Spend"   value={`$${totalMarketing.toFixed(2)}`}    trend="up" trendPercent={8}  icon={<Megaphone size={18} />}   colorIndex={3} />
        </div>

        {/* Charts */}
        <div className="grid gap-5 lg:grid-cols-2">
          <PieChartComponent data={expensesByCategory}  title="Expenses by Category" />
          <BarChartComponent data={marketingByPlatform} title="Marketing Spend by Platform" />
        </div>

        {/* Budget Overview */}
        <div className="glass-card p-6">
          <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">Budget Allocation</h3>
          <div className="space-y-4">
            {data.budgets.map((budget: any, idx: number) => {
              const utilization = budget.total > 0 ? (budget.spent / budget.total) * 100 : 0;
              const status = utilization > 90 ? 'red' : utilization > 70 ? 'amber' : 'emerald';
              const barColors: Record<string, string> = { red: 'bg-red-500', amber: 'bg-amber-500', emerald: 'bg-emerald-500' };
              const bgColors: Record<string, string> = { red: 'bg-red-50 border-red-100', amber: 'bg-amber-50 border-amber-100', emerald: 'bg-emerald-50 border-emerald-100' };
              const textColors: Record<string, string> = { red: 'text-red-700', amber: 'text-amber-700', emerald: 'text-emerald-700' };
              return (
                <div key={idx} className={`rounded-xl border p-4 ${bgColors[status]}`}>
                  <div className="mb-3 flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-slate-800">{budget.department}</p>
                      <p className="text-xs text-slate-500 mt-0.5">${budget.spent.toFixed(0)} spent of ${budget.total.toFixed(0)}</p>
                    </div>
                    <span className={`text-lg font-extrabold ${textColors[status]}`}>{utilization.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-white/70">
                    <div className={`h-full rounded-full transition-all duration-700 ${barColors[status]}`} style={{ width: `${Math.min(utilization, 100)}%` }} />
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
                  {['Description','Category','Amount','Date'].map(h => (
                    <th key={h} className={`py-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider ${h === 'Amount' ? 'text-right' : 'text-left'}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.expenses.slice(0, 6).map((exp, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-3 py-3 font-medium text-slate-800">{exp.description}</td>
                    <td className="px-3 py-3">
                      <span className="inline-flex items-center rounded-full bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
                        {exp.category}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right font-bold text-slate-900">${parseFloat(exp.amount || 0).toFixed(2)}</td>
                    <td className="px-3 py-3 text-slate-400 text-xs">{exp.date}</td>
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
