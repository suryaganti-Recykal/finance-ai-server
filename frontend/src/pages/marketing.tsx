/**Marketing Spend Page — live data from Recykal Google Sheet (values in INR ₹) */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { IndianRupee, Layers, TrendingUp, Building2, AlertCircle, ExternalLink } from 'lucide-react';

interface NameValue  { name: string; value: number; [key: string]: string | number | undefined; }
interface LineItem   { team: string; sub_team: string; segment: string; type: string; month: string; total: number; }
interface LiveSpend  {
  total_spend: number; record_count: number;
  by_team: NameValue[]; by_segment: NameValue[]; by_type: NameValue[];
  by_business_unit: NameValue[]; monthly_trend: { month: string; spend: number }[];
  top_line_items: LineItem[];
}

/** Format Indian Rupee — crore / lakh / plain */
function fmtINR(val: number, short = false): string {
  if (short) {
    if (val >= 10_000_000) return `₹${(val / 10_000_000).toFixed(2)}Cr`;
    if (val >= 100_000)    return `₹${(val / 100_000).toFixed(2)}L`;
    if (val >= 1_000)      return `₹${(val / 1_000).toFixed(1)}K`;
    return `₹${val.toFixed(0)}`;
  }
  return `₹${val.toLocaleString('en-IN')}`;
}

const SEGMENT_COLORS: Record<string, string> = {
  'Ads':             'bg-teal-50 text-teal-700 border-teal-100',
  'IP':              'bg-emerald-50 text-emerald-700 border-emerald-100',
  'Sponsorship':     'bg-amber-50 text-amber-700 border-amber-100',
  'Travel':          'bg-sky-50 text-sky-700 border-sky-100',
  'Hotels':          'bg-cyan-50 text-cyan-700 border-cyan-100',
  'Tools':           'bg-emerald-50 text-emerald-700 border-emerald-100',
  'Offline Activity':'bg-rose-50 text-rose-700 border-rose-100',
  'Membership':      'bg-teal-50 text-teal-700 border-teal-100',
};
const defaultBadge = 'bg-slate-50 text-slate-600 border-slate-200';

const MONTH_ORDER = ['April','May','June','July','August','September','October','November','December','January','February','March'];

export default function MarketingPage() {
  const [data, setData]       = useState<LiveSpend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    dashboardAPI.getLiveMarketingSpend()
      .then(r => setData(r.data.data))
      .catch(e => setError(e.message || 'Failed to load'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <Layout>
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600"/>
          <p className="text-sm font-medium text-slate-500">Fetching live data from Google Sheets…</p>
        </div>
      </div>
    </Layout>
  );

  if (error || !data) return (
    <Layout>
      <div className="glass-card flex items-start gap-4 p-5 !bg-red-50 border border-red-100">
        <AlertCircle className="mt-0.5 shrink-0 text-red-500" size={20}/>
        <div>
          <p className="font-semibold text-red-900">Could not load live spend data</p>
          <p className="mt-1 text-sm text-red-700">{error || 'No data returned'}</p>
        </div>
      </div>
    </Layout>
  );

  // Only include months that have data, in fiscal order
  const monthlyChartData = MONTH_ORDER
    .map(m => data.monthly_trend.find(t => t.month === m))
    .filter(Boolean)
    .map(t => ({ name: t!.month.slice(0, 3), value: t!.spend }));

  // Filter out BUs with 0 spend
  const buData = data.by_business_unit.filter(b => b.value > 0);

  return (
    <Layout>
      <div className="space-y-6">

        {/* Page header */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Marketing Spend</h1>
            <p className="mt-1 text-sm text-slate-400">
              {data.record_count} line items · All values in{' '}
              <span className="font-semibold text-slate-600">Indian Rupees (₹)</span> ·{' '}
              <a
                href="https://docs.google.com/spreadsheets/d/1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc/edit?usp=sharing"
                target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1 text-emerald-500 hover:text-emerald-700 font-medium transition-colors"
              >
                Open source sheet <ExternalLink size={12}/>
              </a>
            </p>
          </div>
          <span className="inline-flex w-fit items-center gap-2 rounded-full bg-emerald-50 border border-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700">
            <span className="animate-pulse-dot h-2 w-2 rounded-full bg-emerald-500"/>
            Live · April – June 2026
          </span>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KPICard
            title="Total Spend"
            value={fmtINR(data.total_spend, true)}
            unit={fmtINR(data.total_spend)}
            icon={<IndianRupee size={18}/>} colorIndex={0}
          />
          <KPICard
            title="Line Items"
            value={data.record_count}
            unit="across 3 months"
            icon={<Layers size={18}/>} colorIndex={1}
          />
          <KPICard
            title="Top Team"
            value={data.by_team[0]?.name || '—'}
            unit={fmtINR(data.by_team[0]?.value || 0, true)}
            icon={<TrendingUp size={18}/>} colorIndex={2}
          />
          <KPICard
            title="Top Business Unit"
            value={buData[0]?.name || '—'}
            unit={fmtINR(buData[0]?.value || 0, true)}
            icon={<Building2 size={18}/>} colorIndex={3}
          />
        </div>

        {/* Monthly trend — full width */}
        <LineChartComponent data={monthlyChartData} title="Monthly Spend Trend (₹)" />

        {/* Pie charts row */}
        <div className="grid gap-5 lg:grid-cols-2">
          <PieChartComponent data={data.by_segment}      title="Spend by Segment (₹)" />
          <PieChartComponent data={buData}               title="Spend by Business Unit (₹)" />
        </div>

        {/* Team vs Type bars */}
        <div className="grid gap-5 lg:grid-cols-2">
          <BarChartComponent data={data.by_team}         title="Spend by Team (₹)" />
          <BarChartComponent data={data.by_type.slice(0,8)} title="Top Spend Types (₹)" />
        </div>

        {/* Line items table */}
        <div className="glass-card p-6">
          <div className="mb-5 flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">All Line Items — {data.top_line_items.length} Shown</h3>
            <span className="text-xs text-slate-400">Sorted by highest spend</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/60">
                  {['#','Team','Sub-Team','Segment','Type','Month','Amount'].map(h => (
                    <th key={h} className={`px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-400 ${h==='Amount'?'text-right':'text-left'}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.top_line_items.map((item, idx) => (
                  <tr key={idx} className="hover:bg-emerald-50/20 transition-colors">
                    <td className="px-4 py-3 text-xs font-bold text-slate-300">#{idx + 1}</td>
                    <td className="px-4 py-3 font-semibold text-slate-800">{item.team}</td>
                    <td className="px-4 py-3 text-slate-500">{item.sub_team}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${SEGMENT_COLORS[item.segment] || defaultBadge}`}>
                        {item.segment}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">{item.type}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                        {item.month}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-extrabold text-slate-900">
                      {fmtINR(item.total, true)}
                      <p className="text-xs font-normal text-slate-400">{fmtINR(item.total)}</p>
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-200 bg-slate-50/80">
                  <td colSpan={6} className="px-4 py-3 text-sm font-semibold text-slate-600">Total</td>
                  <td className="px-4 py-3 text-right font-extrabold text-emerald-600 text-base">
                    {fmtINR(data.total_spend, true)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        {/* Summary stats strip */}
        <div className="grid gap-3 sm:grid-cols-3">
          {data.monthly_trend.map(m => (
            <div key={m.month} className="glass-card p-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{m.month} 2026</p>
                <p className="mt-1 text-xl font-extrabold text-slate-900">{fmtINR(m.spend, true)}</p>
                <p className="text-xs text-slate-400">{fmtINR(m.spend)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400">% of total</p>
                <p className="text-lg font-bold text-emerald-600">{((m.spend / data.total_spend) * 100).toFixed(1)}%</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </Layout>
  );
}
