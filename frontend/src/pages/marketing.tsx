/**Marketing Spend Page — live data from Recykal's Google Sheet */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, Layers, TrendingUp, AlertCircle, ExternalLink, ArrowUpRight } from 'lucide-react';

interface LiveSpendSummary {
  total_spend: number;
  record_count: number;
  by_team: Array<{ name: string; value: number }>;
  by_segment: Array<{ name: string; value: number }>;
  by_type: Array<{ name: string; value: number }>;
  by_business_unit: Array<{ name: string; value: number }>;
  monthly_trend: Array<{ month: string; spend: number }>;
  top_line_items: Array<{ team: string; sub_team: string; segment: string; type: string; month: string; total: number }>;
}

export default function MarketingPage() {
  const [data, setData] = useState<LiveSpendSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getLiveMarketingSpend();
        setData(response.data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load live marketing spend');
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
            <p className="text-sm font-medium text-slate-500">Fetching live data from Google Sheets…</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout>
        <div className="glass-card flex items-start gap-4 p-5 border border-red-100 !bg-red-50">
          <AlertCircle className="mt-0.5 text-red-500 shrink-0" size={20} />
          <div>
            <p className="font-semibold text-red-900">Could not load live spend data</p>
            <p className="mt-1 text-sm text-red-700">{error || 'No data returned'}</p>
          </div>
        </div>
      </Layout>
    );
  }

  const monthlyChartData = data.monthly_trend.map(m => ({ name: m.month, value: m.spend }));

  return (
    <Layout>
      <div className="space-y-6">

        {/* Page header */}
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Marketing Spend</h1>
            <p className="mt-1 text-sm text-slate-400">
              {data.record_count} line items ·{' '}
              <a
                href="https://docs.google.com/spreadsheets/d/1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc"
                target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1 text-indigo-500 hover:text-indigo-700 font-medium transition-colors"
              >
                source sheet <ExternalLink size={12} />
              </a>
            </p>
          </div>
          <span className="inline-flex w-fit items-center gap-2 rounded-full bg-emerald-50 border border-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700">
            <span className="animate-pulse-dot h-2 w-2 rounded-full bg-emerald-500" />
            Live · Updates on reload
          </span>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KPICard title="Total Spend" value={`$${(data.total_spend / 1000).toFixed(1)}K`} icon={<DollarSign size={18} />} colorIndex={0} />
          <KPICard title="Line Items"  value={data.record_count}                              icon={<Layers size={18} />}    colorIndex={1} />
          <KPICard
            title="Top Team"
            value={data.by_team[0]?.name || '—'}
            unit={`$${((data.by_team[0]?.value || 0) / 1000).toFixed(1)}K spend`}
            icon={<TrendingUp size={18} />} colorIndex={2}
          />
          <KPICard
            title="Top Business Unit"
            value={data.by_business_unit[0]?.name || '—'}
            unit={`$${((data.by_business_unit[0]?.value || 0) / 1000).toFixed(1)}K spend`}
            icon={<ArrowUpRight size={18} />} colorIndex={3}
          />
        </div>

        {/* Charts row 1 */}
        <div className="grid gap-5 lg:grid-cols-2">
          <PieChartComponent data={data.by_segment}      title="Spend by Segment" />
          <PieChartComponent data={data.by_business_unit} title="Spend by Business Unit" />
        </div>

        {/* Charts row 2 */}
        <div className="grid gap-5 lg:grid-cols-2">
          <BarChartComponent data={data.by_team}    title="Spend by Team" />
          <LineChartComponent data={monthlyChartData} title="Monthly Spend Trend" />
        </div>

        {/* Top Line Items table */}
        <div className="glass-card p-6">
          <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">Top 10 Line Items</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Team','Sub-Team','Segment','Type','Month','Total'].map(h => (
                    <th key={h} className={`py-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider ${h === 'Total' ? 'text-right' : 'text-left'}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.top_line_items.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-3 py-3 font-semibold text-slate-800">{item.team}</td>
                    <td className="px-3 py-3 text-slate-500">{item.sub_team}</td>
                    <td className="px-3 py-3">
                      <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-100">
                        {item.segment}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-slate-500">{item.type}</td>
                    <td className="px-3 py-3 text-slate-500">{item.month}</td>
                    <td className="px-3 py-3 text-right font-bold text-slate-900">
                      ${item.total.toLocaleString('en-US')}
                    </td>
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
