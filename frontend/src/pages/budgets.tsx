/**Budgets Page */

import { useEffect, useState } from 'react';
import { Layout } from '@/components/Layout';
import { dashboardAPI } from '@/lib/api';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const response = await dashboardAPI.getDemoBudgets();
        setBudgets(response.data.data);
      } catch (err) {
        console.error('Error fetching budgets:', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const getStatusIcon = (percentage: number) => {
    if (percentage > 90) {
      return <AlertCircle className="text-red-600" size={24} />;
    }
    if (percentage > 70) {
      return <AlertTriangle className="text-yellow-600" size={24} />;
    }
    return <CheckCircle className="text-green-600" size={24} />;
  };

  const getStatusColor = (percentage: number) => {
    if (percentage > 90) return 'bg-red-50 border-red-200';
    if (percentage > 70) return 'bg-yellow-50 border-yellow-200';
    return 'bg-green-50 border-green-200';
  };

  const getBarColor = (percentage: number) => {
    if (percentage > 90) return 'bg-red-500';
    if (percentage > 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budget Management</h1>
          <p className="mt-2 text-gray-600">Track and monitor departmental budget allocations</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-primary-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {budgets.map((budget, idx) => {
              const percentage = budget.total > 0 ? (budget.spent / budget.total) * 100 : 0;
              const remaining = budget.total - budget.spent;

              return (
                <div
                  key={idx}
                  className={`rounded-lg border ${getStatusColor(percentage)} p-6`}
                >
                  <div className="mb-4 flex items-start justify-between">
                    <div className="flex gap-4">
                      {getStatusIcon(percentage)}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{budget.department}</h3>
                        <p className="text-sm text-gray-600">
                          ${budget.spent.toFixed(0)} / ${budget.total.toFixed(0)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">{percentage.toFixed(1)}%</p>
                      <p className="text-sm text-gray-600">{percentage > 100 ? 'Over budget' : 'Remaining'}</p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4 h-3 w-full overflow-hidden rounded-full bg-gray-200">
                    <div
                      className={`h-full ${getBarColor(percentage)} transition-all duration-300`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>

                  {/* Quarterly Breakdown */}
                  <div className="grid gap-4 md:grid-cols-4">
                    {[
                      { quarter: 'Q1', amount: budget.q1 },
                      { quarter: 'Q2', amount: budget.q2 },
                      { quarter: 'Q3', amount: budget.q3 },
                      { quarter: 'Q4', amount: budget.q4 },
                    ].map(({ quarter, amount }) => (
                      <div key={quarter} className="rounded bg-white p-3">
                        <p className="text-xs font-medium text-gray-600">{quarter}</p>
                        <p className="mt-1 text-lg font-semibold text-gray-900">
                          ${amount.toFixed(0)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Budget Alerts */}
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Budget Alerts</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 rounded bg-red-50 p-4">
              <AlertCircle className="mt-0.5 text-red-600" size={20} />
              <div>
                <p className="font-medium text-red-900">Over Budget Alert</p>
                <p className="text-sm text-red-800">One or more departments exceeded their quarterly budget</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
