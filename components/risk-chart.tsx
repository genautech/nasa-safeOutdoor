"use client"

import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js"
import { useMemo } from "react"
import { Line } from "react-chartjs-2"

interface RiskChartProps {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor: string
    backgroundColor: string
  }[]
}

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export function RiskChart({ labels, datasets }: RiskChartProps) {
  const data = useMemo(
    () => ({
      labels,
      datasets: datasets.map((dataset) => ({
        ...dataset,
        tension: 0.3,
        fill: true,
        pointRadius: 2.5,
        borderWidth: 2,
      })),
    }),
    [labels, datasets],
  )

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom" as const,
          labels: {
            usePointStyle: true,
            padding: 16,
          },
        },
        tooltip: {
          intersect: false,
          mode: "index" as const,
          callbacks: {
            label: function (context: any) {
              const label = context.dataset.label || ""
              const value = context.parsed.y
              return `${label}: ${(value * 100).toFixed(0)}% risk`
            },
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "nearest" as const,
      },
      scales: {
        y: {
          grace: "5%",
          grid: { color: "rgba(22, 43, 51, 0.08)" },
          ticks: {
            callback: (value: number) => `${Math.round(value * 100)}%`,
          },
          min: 0,
          max: 0.9,
        },
        x: {
          grid: { display: false },
        },
      },
    }),
    [],
  )

  return (
    <div className="h-[320px] w-full">
      <Line data={data} options={options} />
    </div>
  )
}
