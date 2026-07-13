/**Premium Chart Components — fixed pie labels, rich tooltips, gradient bars */

import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Area, AreaChart,
} from 'recharts';

const COLORS = ['#10b981','#14b8a6','#f59e0b','#f43f5e','#06b6d4','#64748b','#ec4899','#059669'];

interface ChartData {
  name: string;
  value: number;
  [key: string]: string | number | undefined;
}

// Custom tooltip shared style
const TooltipStyle = {
  background: '#0f172a',
  border: 'none',
  borderRadius: '10px',
  color: '#f1f5f9',
  fontSize: 13,
  boxShadow: '0 8px 32px rgba(0,0,0,0.24)',
  padding: '10px 14px',
};

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="glass-card p-6">
      <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">{title}</h3>
      {children}
    </div>
  );
}

export function BarChartComponent({ data, title, dataKey = 'value' }: { data: ChartData[]; title: string; dataKey?: string }) {
  return (
    <ChartCard title={title}>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} barSize={32} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={v => v >= 1000 ? `$${(v/1000).toFixed(0)}K` : `$${v}`} />
          <Tooltip contentStyle={TooltipStyle} cursor={{ fill: 'rgba(16,185,129,0.06)' }} formatter={(v: number) => [`$${v.toLocaleString()}`, 'Value']} />
          <Bar dataKey={dataKey} fill="url(#barGrad)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function LineChartComponent({ data, title, dataKey = 'value' }: { data: ChartData[]; title: string; dataKey?: string }) {
  return (
    <ChartCard title={title}>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="lineArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={v => v >= 1000 ? `$${(v/1000).toFixed(0)}K` : `$${v}`} />
          <Tooltip contentStyle={TooltipStyle} formatter={(v: number) => [`$${v.toLocaleString()}`, 'Spend']} />
          <Area type="monotone" dataKey={dataKey} stroke="#10b981" strokeWidth={2.5} fill="url(#lineArea)" dot={{ fill: '#10b981', r: 4 }} activeDot={{ r: 6, fill: '#10b981' }} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

// Custom label renders only for slices > 5% to avoid clutter
const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) => {
  if (percent < 0.05) return null;
  const RADIAN = Math.PI / 180;
  const radius = outerRadius + 28;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#475569" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize={11} fontWeight={500}>
      {name} {(percent * 100).toFixed(0)}%
    </text>
  );
};

export function PieChartComponent({ data, title }: { data: ChartData[]; title: string }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  return (
    <ChartCard title={title}>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            cx="42%"
            cy="50%"
            labelLine={{ stroke: '#cbd5e1', strokeWidth: 1 }}
            label={renderLabel}
            outerRadius={95}
            innerRadius={50}
            dataKey="value"
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="white" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={TooltipStyle}
            formatter={(v: number, name: string) => [`$${v.toLocaleString()} (${((v/total)*100).toFixed(1)}%)`, name]}
          />
        </PieChart>
      </ResponsiveContainer>
      {/* Legend */}
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1.5 justify-center">
        {data.map((d, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs text-slate-500">
            <span className="inline-block h-2.5 w-2.5 rounded-sm flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
            {d.name}
          </div>
        ))}
      </div>
    </ChartCard>
  );
}
