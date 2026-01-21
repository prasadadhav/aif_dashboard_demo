import React, { CSSProperties } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Props {
  id: string;
  title?: string;
  color?: string;
  data: any[];
  labelField: string;
  dataField: string;
  options?: Record<string, any>;
  styles?: CSSProperties;
}

type SeriesPoint = { name: string; value: number | string };
type SeriesCfg = {
  name: string;
  color?: string;
  data?: SeriesPoint[]; // optional: can be dummy/demo data
  filter?: string; // optional: expression evaluated against each row in `data`
};

const resolveColor = (
  explicit?: string,
  options?: Record<string, any>,
  styles?: CSSProperties
) => {
  return (
    explicit ||
    options?.lineColor ||
    (styles && (styles as any)["--chart-line-color"]) ||
    "#4a90e2"
  );
};

// Make safe object keys for recharts dataKey
const slug = (s: string) =>
  String(s ?? "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");

const parseSeries = (raw: any): SeriesCfg[] => {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw as SeriesCfg[];
  if (typeof raw === "string") {
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? (parsed as SeriesCfg[]) : [];
    } catch {
      return [];
    }
  }
  return [];
};

// Pivot series points into a single recharts dataset:
// [{[xKey]: 'A', series_1: 10, series_2: 20}, ...]
const pivotSeries = (series: SeriesCfg[], xKey: string) => {
  const rows = new Map<string, any>();

  for (const s of series) {
    const key = slug(s.name);
    for (const p of s.data ?? []) {
      const x = p.name;
      const row = rows.get(x) ?? { [xKey]: x };
      row[key] = Number(p.value);
      rows.set(x, row);
    }
  }

  return {
    data: Array.from(rows.values()),
    keys: series.map((s) => ({
      key: slug(s.name),
      name: s.name,
      color: s.color,
    })),
  };
};

// Builds a function from a string expression like:
// evaluation.observation[0].measure.find(... )?.value
const compileFilter = (expr: string) => {
  try {
    // eslint-disable-next-line no-new-func
    return new Function("evaluation", `return (${expr});`) as (
      evaluation: any
    ) => any;
  } catch (e) {
    // If expression is malformed, don't crash the chart.
    // eslint-disable-next-line no-console
    console.warn("Bad series.filter expression:", expr, e);
    return () => undefined;
  }
};

// Determine x-axis label for a row in `data`
const getXLabel = (
  row: any,
  idx: number,
  options: Record<string, any> | undefined,
  labelField: string
) => {
  const xField = options?.xField || options?.["x-field"];
  if (xField && row?.[xField] != null) return String(row[xField]);
  if (labelField && row?.[labelField] != null) return String(row[labelField]);
  return String(idx + 1);
};

const hasAnyPoints = (series: SeriesCfg[]) =>
  series.some((s) => (s.data?.length ?? 0) > 0);

export const LineChartComponent: React.FC<Props> = ({
  id,
  title,
  color,
  data,
  labelField,
  dataField,
  options,
  styles,
}) => {
  const containerStyle: CSSProperties = {
    width: "100%",
    height: "400px",
    marginBottom: "20px",
    ...styles,
  };

  const strokeWidth = options?.lineWidth ?? 2;
  const resolvedColor = resolveColor(color, options, styles);
  const showGrid = options?.showGrid ?? true;
  const showLegend = options?.showLegend ?? true;
  const showTooltip = options?.showTooltip ?? true;
  const legendPosition = options?.legendPosition || "top";

  // Support both camelCase and kebab-case coming from WME-ish configs
  const curveType = options?.curveType || options?.["curve-type"] || "monotone";
  const animate = options?.animate ?? true;
  const dot = options?.dotSize ? { r: options.dotSize } : true;

  // ---- Multi-series support via options.series ----
  const rawSeries = parseSeries(options?.series);
  const isMulti = rawSeries.length > 0;

  // If series has filters and we have real data, compute points from `data`
  const hasFilter = rawSeries.some(
    (s) => typeof s.filter === "string" && s.filter.trim().length > 0
  );

  const xKey = labelField || "x";

  // 1) Compute series from backend `data` when possible
  let computedSeries: SeriesCfg[] = rawSeries;

  if (isMulti && Array.isArray(data) && data.length > 0 && hasFilter) {
    computedSeries = rawSeries.map((s) => {
      if (!s.filter) return s;

      const fn = compileFilter(s.filter);
      const pts: SeriesPoint[] = data
        .map((row: any, idx: number) => ({
          name: getXLabel(row, idx, options, xKey),
          value: fn(row),
        }))
        .filter((p) => p.value != null);

      return { ...s, data: pts };
    });

    // If filters produced no points (common when filter doesn't match data shape),
    // fall back to whatever series.data exists (dummy/demo).
    if (!hasAnyPoints(computedSeries)) {
      computedSeries = rawSeries;
    }
  }

  // 2) Prepare chart dataset
  let chartData: any[] = data;
  let seriesKeys: Array<{ key: string; name: string; color?: string }> = [];

  if (isMulti) {
    const pivoted = pivotSeries(computedSeries, xKey);
    chartData = pivoted.data;
    seriesKeys = pivoted.keys;

    // If still empty (no computed points AND no dummy points), avoid "everything vanishes"
    // by falling back to single-series over `data`.
    if (!chartData || chartData.length === 0) {
      chartData = data;
      seriesKeys = [];
    }
  }

  return (
    <div id={id} style={containerStyle}>
      {title && (
        <h3 style={{ textAlign: "center", marginBottom: "10px" }}>{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={360}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke={options?.gridColor} />
          )}
          <XAxis dataKey={xKey} />
          <YAxis />
          {showTooltip && <Tooltip />}
          {showLegend && <Legend verticalAlign={legendPosition} />}

          {isMulti && seriesKeys.length > 0 ? (
            seriesKeys.map((s) => (
              <Line
                key={s.key}
                type={curveType}
                dataKey={s.key}
                name={s.name}
                stroke={s.color || resolvedColor}
                strokeWidth={strokeWidth}
                dot={dot}
                isAnimationActive={animate}
              />
            ))
          ) : (
            <Line
              type={curveType}
              dataKey={dataField}
              stroke={resolvedColor}
              strokeWidth={strokeWidth}
              dot={dot}
              isAnimationActive={animate}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
