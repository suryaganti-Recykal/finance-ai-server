/**Premium KPI Card Component */

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { ReactNode } from 'react';

const iconGradients = ['kpi-icon-indigo', 'kpi-icon-emerald', 'kpi-icon-amber', 'kpi-icon-rose', 'kpi-icon-cyan'];
let cardIndex = 0;

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendPercent?: number;
  icon?: ReactNode;
  colorIndex?: number;
}

export function KPICard({
  title,
  value,
  unit = '',
  trend,
  trendPercent = 0,
  icon,
  colorIndex = 0,
}: KPICardProps) {
  const trendConfig = {
    up:     { color: 'text-emerald-600', bg: 'bg-emerald-50', Icon: TrendingUp,   label: 'increase' },
    down:   { color: 'text-red-500',     bg: 'bg-red-50',     Icon: TrendingDown, label: 'decrease' },
    stable: { color: 'text-slate-500',   bg: 'bg-slate-50',   Icon: Minus,        label: 'stable'   },
  };
  const tc = trend ? trendConfig[trend] : null;

  return (
    <div className="glass-card p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</p>
        {icon && (
          <div className={`${iconGradients[colorIndex % iconGradients.length]} flex h-9 w-9 items-center justify-center rounded-xl text-white shadow-md`}>
            {icon}
          </div>
        )}
      </div>

      <div>
        <p className="text-3xl font-extrabold text-slate-900 leading-none tracking-tight">{value}</p>
        {unit && <p className="mt-1 text-sm font-medium text-slate-500">{unit}</p>}
      </div>

      {tc && trendPercent !== 0 && (
        <div className={`inline-flex w-fit items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${tc.bg} ${tc.color}`}>
          <tc.Icon size={12} />
          {Math.abs(trendPercent)}% {tc.label}
        </div>
      )}
    </div>
  );
}
