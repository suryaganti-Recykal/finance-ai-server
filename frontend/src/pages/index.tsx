/**Dashboard Home Page */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { KPICard } from '@/components/KPICard';
import { BarChartComponent, PieChartComponent, LineChartComponent } from '@/components/Chart';
import { dashboardAPI } from '@/lib/api';
import { DollarSign, TrendingUp, BarChart3, AlertCircle } from 'lucide-react';

interface DemoData {
  expenses: Array<any>;
  marketing: Array<any>;
  budgets: Array<any>;
  forecasts: Array<any>;
}

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
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-primary-600"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex gap-3">
            <AlertCircle className="text-red-600" size={24} />
            <div>
              <h3 className="font-semibold text-red-900">Error loading data</h3>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!data) {
    return <Layout><div>No data available</div></Layout>;
  }

  // Calculate metrics
  const totalExpenses = data.expenses.reduce((sum, exp) => sum + parseFloat(exp.amount || 0), 0);
  const totalMarketing = data.marketing.reduce((sum, camp) => sum + parseFloat(camp.spend || 0), 0);
  const expenseCount = data.expenses.length;
  const avgExpense = expenseCount > 0 ? totalExpenses / expenseCount : 0;

  // Prepare chart data
  const expensesByCategory = data.expenses.reduce(
    (acc, exp) => {
      const existing = acc.find((item) => item.name === exp.category);
      if (existing) {
        existing.value += parseFloat(exp.amount || 0);
      } else {
        acc.push({ name: exp.category, value: parseFloat(exp.amount || 0) });
      }
      return acc;
    },
    [] as Array<{ name: string; value: number }>
  );

  const marketingByPlatform = data.marketing.map((camp) => ({
    name: camp.platform,
    value: parseFloat(camp.spend || 0),
  }));

  const budgetData = data.budgets.map((budget) => ({
    name: budget.department,
    allocated: parseFloat(budget.total || 0),
    spent: parseFloat(budget.spent || 0),
  }));

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome to Finance AI - Expense & Budget Management</p>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KPICard
            title="Total Expenses"
            value={`$${totalExpenses.toFixed(2)}`}
            trend="up"
            trendPercent={12}
            icon={<DollarSign size={32} />}
          />
          <KPICard
            title="Transactions"
            value={expenseCount}
            trend="up"
            trendPercent={5}
            icon={<BarChart3 size={32} />}
          />
          <KPICard
            title="Avg Transaction"
            value={`$${avgExpense.toFixed(2)}`}
            trend="stable"
            icon={<TrendingUp size={32} />}
          />
          <KPICard
            title="Marketing Spend"
            value={`$${totalMarketing.toFixed(2)}`}
            trend="up"
            trendPercent={8}
            icon={<TrendingUp size={32} />}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          <PieChartComponent data={expensesByCategory} title="Expenses by Category" />
          <BarChartComponent data={marketingByPlatform} title="Marketing Spend by Platform" />
        </div>

        {/* Budget Overview */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold text-gray-900">Budget Allocation</h3>
          <div className="space-y-4">
            {budgetData.map((budget) => {
              const utilization =
                budget.allocated > 0 ? (budget.spent / budget.allocated) * 100 : 0;
              const statusColor =
                utilization > 90 ? 'bg-red-100' : utilization > 70 ? 'bg-yellow-100' : 'bg-green-100';
              const barColor =
                utilization > 90 ? 'bg-red-500' : utilization > 70 ? 'bg-yellow-500' : 'bg-green-500';

              return (
                <div key={budget.name} className={`rounded-lg p-4 ${statusColor}`}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium text-gray-900">{budget.name}</span>
                    <span className="text-sm text-gray-600">
                      ${budget.spent.toFixed(0)} / ${budget.allocated.toFixed(0)}
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                    <div
                      className={`h-full ${barColor}`}
                      style={{ width: `${Math.min(utilization, 100)}%` }}
                    />
                  </div>
                  <div className="mt-1 text-sm text-gray-600">{utilization.toFixed(1)}% utilized</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Expenses Table */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold text-gray-900">Recent Expenses</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left font-medium text-gray-600">Description</th>
                  <th className="text-left font-medium text-gray-600">Category</th>
                  <th className="text-left font-medium text-gray-600">Amount</th>
                  <th className="text-left font-medium text-gray-600">Date</th>
                </tr>
              </thead>
              <tbody>
                {data.expenses.slice(0, 5).map((expense, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3">{expense.description}</td>
                    <td className="py-3">
                      <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
                        {expense.category}
                      </span>
                    </td>
                    <td className="py-3 font-medium">${parseFloat(expense.amount || 0).toFixed(2)}</td>
                    <td className="py-3 text-gray-600">{expense.date}</td>
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
