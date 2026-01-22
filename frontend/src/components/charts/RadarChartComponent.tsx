import React, { CSSProperties } from "react";
import {
  Legend,
  PolarAngleAxis as RPolarAngleAxis,
  PolarRadiusAxis as RPolarRadiusAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

// Cast the components to fix TypeScript issue
const PolarAngleAxis = RPolarAngleAxis as any;
const PolarRadiusAxis = RPolarRadiusAxis as any;


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

const pickColor = (
  explicit?: string,
  options?: Record<string, any>,
  styles?: CSSProperties
) =>
  explicit ||
  options?.lineColor ||
  (styles && (styles as any)["--chart-line-color"]) ||
  "#0EA5E9";

export const RadarChartComponent: React.FC<Props> = ({
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

  const showGrid = options?.showGrid ?? true;
  const showTooltip = options?.showTooltip ?? true;
  const showLegend = options?.showLegend ?? true;
  const showRadiusAxis = options?.showRadiusAxis ?? true;
  const legendPosition = options?.legendPosition || "bottom";
  const resolvedColor = resolveColor(color, options, styles);

  // Extract all metric columns (excluding the labelField column)
  const metricKeys = data && data.length > 0 ? Object.keys(data[0]).filter((key) => key !== labelField) : [];


  // Parse series configuration for colors
  const colorMap: { [key: string]: string } = {};
  if (options?.series) {
    try {
      const parsedSeries = JSON.parse(options.series);
      parsedSeries.forEach((s: any) => {
        if (s.name && s.color) {
          colorMap[s.name] = s.color;
        }
      });
    } catch (e) {
      console.error('Failed to parse series config:', e);
    }
  }

  return (
    <div id={id} style={containerStyle}>
      {title && <h3 style={{ textAlign: "center", marginBottom: "10px" }}>{title}</h3>}
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
          <PolarGrid />
          <PolarAngleAxis dataKey="metric" />
          <PolarRadiusAxis />
          <Tooltip />
          <Legend verticalAlign={legendPosition} />

          {metricKeys.map((metricKey) => (
            <Radar
              key={metricKey}
              name={metricKey}
              dataKey={metricKey}
              stroke={colorMap[metricKey] || resolveColor(color, options, styles)}
              fill={colorMap[metricKey] || "#8884d8"}
              fillOpacity={0.6}
              isAnimationActive={options?.animate ?? true}
            />
          ))}
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};