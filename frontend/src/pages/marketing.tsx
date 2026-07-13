/**Marketing Spend Page — live data from Recykal's Google Sheet */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, Layers, TrendingUp, AlertCircle } from 'lucide-react';

interface LiveSpendSummary {
  total_spend: number;
  record_count: number;
  by_team: Array<{ name: string; value: number }>;
  by_segment: Array<{ name: string; value: number }>;
  by_type: Array<{ name: string; value: number }>;
  by_business_unit: Array<{ name: string; value: number }>;
  monthly_trend: Array<{ month: string; spend: number }>;
  top_line_items: Array<{
    team: string;
    sub_team: string;
    segment: string;
    type: string;
    month: string;
    total: number;
  }>;
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
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-primary-600"></div>
            <p className="text-gray-600">Loading live data from Google Sheets...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex gap-3">
            <AlertCircle className="text-red-600" size={24} />
            <div>
              <h3 className="font-semibold text-red-900">Error loading live spend data</h3>
              <p className="text-sm text-red-800">{error || 'No data returned'}</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const monthlyChartData = data.monthly_trend.map((m) => ({ name: m.month, value: m.spend }));

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Marketing Spend</h1>
            <p className="mt-2 text-gray-600">
              Live data · {data.record_count} line items ·{' '}
              <a
                href="https://docs.google.com/spreadsheets/d/1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc"
                target="_blank"
                rel="noreferrer"
                className="text-primary-600 hover:underline"
              >
                source sheet
              </a>
            </p>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            Live
          </span>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KPICard
            title="Total Spend"
            value={`₹${(data.total_spend / 100000).toFixed(1)}L`}
            icon={<DollarSign size={32} />}
          />
          <KPICard
            title="Line Items"
            value={data.record_count}
            icon={<Layers size={32} />}
          />
          <KPICard
            title="Top Team"
            value={data.by_team[0]?.name || '-'}
            unit={`₹${((data.by_team[0]?.value || 0) / 100000).toFixed(1)}L`}
            icon={<TrendingUp size={32} />}
          />
          <KPICard
            title="Top Business Unit"
            value={data.by_business_unit[0]?.name || '-'}
            unit={`₹${((data.by_business_unit[0]?.value || 0) / 100000).toFixed(1)}L`}
            icon={<TrendingUp size={32} />}
          />
        </div>

        {/* Charts */}
        <div className="grid gap-6 lg:grid-cols-2">
          <PieChartComponent data={data.by_segment} title="Spend by Segment" />
          <PieChartComponent data={data.by_business_unit} title="Spend by Business Unit" />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <BarChartComponent data={data.by_team} title="Spend by Team" />
          <LineChartComponent data={monthlyChartData} title="Monthly Spend Trend" />
        </div>

        {/* Top Line Items Table */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold text-gray-900">Top 10 Line Items</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-2 py-2 text-left font-medium text-gray-600">Team</th>
                  <th className="px-2 py-2 text-left font-medium text-gray-600">Sub-Team</th>
                  <th className="px-2 py-2 text-left font-medium text-gray-600">Segment</th>
                  <th className="px-2 py-2 text-left font-medium text-gray-600">Type</th>
                  <th className="px-2 py-2 text-left font-medium text-gray-600">Month</th>
                  <th className="px-2 py-2 text-right font-medium text-gray-600">Total</th>
                </tr>
              </thead>
              <tbody>
                {data.top_line_items.map((item, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-2 py-3">{item.team}</td>
                    <td className="px-2 py-3 text-gray-600">{item.sub_team}</td>
                    <td className="px-2 py-3">
                      <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
                        {item.segment}
                      </span>
                    </td>
                    <td className="px-2 py-3 text-gray-600">{item.type}</td>
                    <td className="px-2 py-3 text-gray-600">{item.month}</td>
                    <td className="px-2 py-3 text-right font-medium">
                      ₹{item.total.toLocaleString('en-IN')}
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
