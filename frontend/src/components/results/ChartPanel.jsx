import { Component } from "react";
import {
  AreaChart, Area,
  BarChart, Bar,
  LineChart, Line,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { useThemeStore } from "../../store/themeStore";

const BRAND = "#1D9E75";
const PIE_COLORS = ["#1D9E75", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

class ChartErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() { return this.state.hasError ? null : this.props.children; }
}

function ChartInner({ chartConfig, isDark }) {
  const { chart_type, chart_data, x_key, y_key, title } = chartConfig;
  const type = (chart_type || "bar").toLowerCase();

  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
  const tickColor = isDark ? "#64748B" : "#94A3B8";
  const tooltipStyle = isDark
    ? { background: "#122338", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#E2E8F0" }
    : { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 8, color: "#0F172A" };

  const sharedAxis = {
    tick: { fill: tickColor, fontSize: 11 },
    axisLine: { stroke: gridColor },
    tickLine: false,
  };

  let chart;
  switch (type) {
    case "line":
      chart = (
        <LineChart data={chart_data}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey={x_key} {...sharedAxis} />
          <YAxis {...sharedAxis} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 12, color: tickColor }} />
          <Line type="monotone" dataKey={y_key} stroke={BRAND} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
        </LineChart>
      );
      break;

    case "area":
      chart = (
        <AreaChart data={chart_data}>
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={BRAND} stopOpacity={0.3} />
              <stop offset="95%" stopColor={BRAND} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey={x_key} {...sharedAxis} />
          <YAxis {...sharedAxis} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 12, color: tickColor }} />
          <Area type="monotone" dataKey={y_key} stroke={BRAND} strokeWidth={2} fill="url(#areaGrad)" />
        </AreaChart>
      );
      break;

    case "pie":
      chart = (
        <PieChart>
          <Pie data={chart_data} dataKey={y_key} nameKey={x_key} cx="50%" cy="50%" outerRadius={90} label>
            {chart_data.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 12, color: tickColor }} />
        </PieChart>
      );
      break;

    default:
      chart = (
        <BarChart data={chart_data}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis dataKey={x_key} {...sharedAxis} />
          <YAxis {...sharedAxis} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 12, color: tickColor }} />
          <Bar dataKey={y_key} fill={BRAND} radius={[5, 5, 0, 0]} />
        </BarChart>
      );
  }

  return (
    <div
      className="mt-3 rounded-xl p-4"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        boxShadow: "var(--shadow-card)",
      }}
    >
      {title && (
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
          {title}
        </p>
      )}
      <ResponsiveContainer width="100%" height={280}>
        {chart}
      </ResponsiveContainer>
    </div>
  );
}

export default function ChartPanel({ chartConfig }) {
  const theme = useThemeStore((s) => s.theme);
  if (!chartConfig || Object.keys(chartConfig).length === 0) return null;
  const { chart_data, x_key, y_key } = chartConfig;
  if (!chart_data?.length || !x_key || !y_key) return null;

  return (
    <ChartErrorBoundary>
      <ChartInner chartConfig={chartConfig} isDark={theme === "dark"} />
    </ChartErrorBoundary>
  );
}
