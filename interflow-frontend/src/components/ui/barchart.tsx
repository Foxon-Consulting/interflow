"use client"

import * as React from "react"
import { TrendingUp, CheckCircle, XCircle, AlertTriangle } from "lucide-react"
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

export const description = "A stacked bar chart with a legend"

// Types pour les props - plus flexibles
interface ChartDataItem {
  [key: string]: string | number  // Accepte n'importe quelle clé
}

interface ChartBarStackedProps {
  data?: ChartDataItem[]
  title?: string
  description?: string
  config?: ChartConfig
  trendText?: string
  trendColor?: string
  trendIcon?: React.ComponentType<{ className?: string }>
  footerText?: string
  xAxisKey?: string
  barKeys?: string[]
  stackId?: string
}

// Données par défaut
const defaultChartData: ChartDataItem[] = [
  { comparaison: "besoin", besoin: 0, stocks_internes: 0, receptions: 0, rappatriements: 0 },
  { comparaison: "stock", besoin: 0, stocks_internes: 0, receptions: 0, rappatriements: 0 },
]

const defaultChartConfig: ChartConfig = {
  besoin: {
    label: "Besoin",
    color: "var(--chart-1)",
  },
  stocks_internes: {
    label: "Stocks Internes",
    color: "var(--chart-2)",
  },
  receptions: {
    label: "Réceptions",
    color: "var(--chart-3)",
  },
  rappatriements: {
    label: "Rappatriements",
    color: "var(--chart-4)",
  },
}


export function ChartBarStacked({
  data = defaultChartData,
  title = "Bar Chart - Stacked + Legend",
  description: chartDescription = "January - June 2024",
  config = defaultChartConfig,
  trendText = "Trending up by 5.2% this month",
  trendColor,
  trendIcon = TrendingUp,
  footerText = "Showing total visitors for the last 6 months",
  xAxisKey = "month",
  barKeys = ["desktop", "mobile"],
  stackId = "a"
}: ChartBarStackedProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{chartDescription}</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config}>
          <BarChart accessibilityLayer data={data}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey={xAxisKey}
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 10)}
            />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <ChartLegend content={<ChartLegendContent />} />
            {barKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                stackId={stackId}
                fill={config[key]?.color || `var(--chart-${index + 1})`}
                radius={index === 0 ? [0, 0, 4, 4] : [4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 leading-none font-medium" style={{ color: trendColor }}>
          {trendText} {React.createElement(trendIcon, { className: "h-4 w-4" })}
        </div>
        <div className="text-muted-foreground leading-none">
          {footerText}
        </div>
      </CardFooter>
    </Card>
  )
}
