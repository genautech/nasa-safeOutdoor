"use client"

import { useMemo, useState } from "react"
import {
  Activity,
  AlertTriangle,
  BellRing,
  CalendarCheck,
  CheckCircle2,
  CloudSun,
  Compass,
  Cpu,
  MapPin,
  ShieldCheck,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { RiskChart } from "@/components/risk-chart"
import {
  accuracyTarget,
  activityHistory,
  autoDetectedRoutines,
  heroImageUrl,
  nasaDatasets,
  notificationMessages,
  recommendedWindows,
  riskSeriesLabels,
  riskSeriesValues,
  wizardBackgroundUrl,
  historyBackgroundUrl,
} from "@/lib/safeoutdoor-data"
import { useOfflineStatus } from "@/hooks/use-offline-status"
import { useServiceWorkerRegistration } from "@/hooks/use-service-worker"

const wizardSteps = [
  {
    id: 1,
    title: "Log in or sync",
    description: "Connect Fitbit, Google Calendar, or use a one-tap magic link.",
    detail: "We auto-pull heart rate, VO₂ max trends, and your upcoming adventures.",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/1177/1177568.png",
  },
  {
    id: 2,
    title: "Get condition alerts",
    description: "NASA TEMPO, OMI, MERRA-2 & GPM power real-time risk insights.",
    detail: "Respiratory, UV, heat stress, and rain alerts land before you head out.",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/869/869636.png",
  },
  {
    id: 3,
    title: "View activity history",
    description: "See what worked, what was avoided, and how conditions evolved.",
    detail: "Each adventure is logged with air, UV, and hydration notes for debriefs.",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/747/747310.png",
  },
]

const routineSourceColors = {
  Fitbit: "bg-emerald-500/10 text-emerald-300",
  Calendar: "bg-sky-500/10 text-sky-300",
  Manual: "bg-amber-500/10 text-amber-300",
}

type RoutineSourceKey = keyof typeof routineSourceColors

export default function Home() {
  const [selectedRoutineId, setSelectedRoutineId] = useState(autoDetectedRoutines[0]?.id)
  const [selectedDatasetId, setSelectedDatasetId] = useState(nasaDatasets[0]?.id)
  const [customRoutineInput, setCustomRoutineInput] = useState("")
  const [customRoutinePreview, setCustomRoutinePreview] = useState<string | null>(null)
  const isOffline = useOfflineStatus()
  const swStatus = useServiceWorkerRegistration()

  const selectedRoutine = useMemo(
    () =>
      autoDetectedRoutines.find((routine) => routine.id === selectedRoutineId) ||
      autoDetectedRoutines[0],
    [selectedRoutineId],
  )

  const selectedDataset = useMemo(
    () => nasaDatasets.find((dataset) => dataset.id === selectedDatasetId) || nasaDatasets[0],
    [selectedDatasetId],
  )

  const aggregatedAccuracy = useMemo(
    () =>
      Number(
        (
          nasaDatasets.reduce((acc, dataset) => acc + dataset.accuracy, 0) / nasaDatasets.length
        ).toFixed(2),
      ),
    [],
  )

  const chartDatasets = useMemo(
    () => [
      {
        label: "Respiratory (NO₂ / PM2.5)",
        data: riskSeriesValues.respiratory,
        borderColor: "rgba(14, 165, 233, 1)",
        backgroundColor: "rgba(14, 165, 233, 0.18)",
      },
      {
        label: "UV Exposure",
        data: riskSeriesValues.uv,
        borderColor: "rgba(244, 114, 182, 1)",
        backgroundColor: "rgba(244, 114, 182, 0.15)",
      },
      {
        label: "Heat Stress",
        data: riskSeriesValues.heat,
        borderColor: "rgba(248, 250, 109, 1)",
        backgroundColor: "rgba(248, 250, 109, 0.18)",
      },
      {
        label: "Precipitation",
        data: riskSeriesValues.precipitation,
        borderColor: "rgba(34, 197, 94, 1)",
        backgroundColor: "rgba(34, 197, 94, 0.15)",
      },
    ],
    [],
  )

  const handleManualRoutineSave = () => {
    if (!customRoutineInput.trim()) return
    setCustomRoutinePreview(customRoutineInput.trim())
    setSelectedRoutineId("manual-hike")
    setCustomRoutineInput("")
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      {isOffline && (
        <div className="bg-amber-500/10 text-amber-200 border border-amber-500/40 text-center py-2">
          You are viewing cached insights offline. NASA data will refresh when you reconnect.
        </div>
      )}

      <main className="relative overflow-hidden">
        <section
          className="relative isolate"
          style={{
            backgroundImage: `linear-gradient(120deg, rgba(15,23,42,0.75), rgba(2,132,199,0.55)), url(${heroImageUrl})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 pb-24 pt-28 sm:pb-36 sm:pt-32">
            <div className="flex flex-col gap-6 max-w-3xl">
              <Badge className="w-fit bg-sky-400/20 text-sky-200 border border-sky-300/30">
                NASA Space Apps Challenge 2025 · From EarthData to Action
              </Badge>
              <h1 className="text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                Safe Outdoor v3.0
                <span className="block text-sky-100">
                  AI-guided adventure planning with NASA TEMPO, OMI, MERRA-2 & GPM
                </span>
              </h1>
              <p className="text-lg text-slate-200 sm:text-xl">
                Sync your wearables, calendars, and manual plans. We fuse NASA Earth observation data with
                personal context to send the right outdoor recommendation before you lace up.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button size="lg" className="bg-sky-500 hover:bg-sky-400">
                  Start with Fitbit Sync
                </Button>
                <Button size="lg" variant="outline" className="border-slate-200/50 text-slate-100 hover:bg-slate-900/40">
                  Try Demo Mode
                </Button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-sky-300/20 bg-slate-900/40 p-4">
                  <div className="flex items-center gap-3">
                    <ShieldCheck className="h-10 w-10 text-sky-300" />
                    <div>
                      <p className="text-sm uppercase tracking-wide text-slate-300">Data accuracy</p>
                      <p className="text-2xl font-semibold">{Math.round(aggregatedAccuracy * 100)}%</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-300">
                    Weighted blend of TEMPO, OMI, MERRA-2, and GPM sources. Target ≥ {Math.round(accuracyTarget * 100)}% accuracy.
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200/20 bg-slate-900/40 p-4">
                  <div className="flex items-center gap-3">
                    <BellRing className="h-10 w-10 text-amber-300" />
                    <div>
                      <p className="text-sm uppercase tracking-wide text-slate-300">Proactive alerts</p>
                      <p className="text-2xl font-semibold">2 hrs lead</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-300">
                    Push notifications adjust your plans before your first step — sunrise, lunch break, or sunset.
                  </p>
                </div>
                <div className="rounded-2xl border border-emerald-300/20 bg-slate-900/40 p-4">
                  <div className="flex items-center gap-3">
                    <Cpu className="h-10 w-10 text-emerald-300" />
                    <div>
                      <p className="text-sm uppercase tracking-wide text-slate-300">Offline ready</p>
                      <p className="text-2xl font-semibold">{swStatus === "registered" ? "Active" : "Syncing"}</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-300">
                    Cached itineraries & risk windows stay available even without cell coverage.
                  </p>
                </div>
              </div>
            </div>

            <section className="rounded-3xl border border-slate-200/20 bg-slate-950/70 p-6 backdrop-blur">
              <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-2xl font-semibold">Auto-detected routines</h2>
                  <p className="text-sm text-slate-300">
                    Pick the activity we should optimize today. We scored each routine with NASA risk data.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <CalendarCheck className="h-5 w-5 text-sky-300" />
                  <span className="text-sm text-slate-300">Sync sources: Fitbit, Google Calendar, manual entries</span>
                </div>
              </header>
              <div className="mt-6 grid gap-4 md:grid-cols-3">
                {autoDetectedRoutines.map((routine) => (
                  <button
                    key={routine.id}
                    onClick={() => setSelectedRoutineId(routine.id)}
                    className={`rounded-2xl border transition-all ${
                      selectedRoutineId === routine.id
                        ? "border-sky-400 bg-sky-500/10 shadow-lg shadow-sky-900/30"
                        : "border-slate-700/60 bg-slate-900/60 hover:border-slate-400/40"
                    } p-5 text-left`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-lg font-semibold text-slate-100">{routine.label}</p>
                      <Badge className={`${routineSourceColors[routine.source as RoutineSourceKey]} border-none`}>{routine.source}</Badge>
                    </div>
                    <p className="mt-3 text-sm text-slate-300">{routine.nextOccurrence}</p>
                    <div className="mt-4 flex items-center gap-2 text-sm text-slate-300">
                      <MapPin className="h-4 w-4 text-sky-300" />
                      {routine.location}
                    </div>
                    <p className="mt-3 text-xs uppercase tracking-wide text-emerald-300/80">{routine.healthFocus}</p>
                  </button>
                ))}
              </div>
              <div className="mt-6 flex flex-col gap-3 rounded-2xl border border-dashed border-slate-600/60 bg-slate-900/40 p-4 sm:flex-row sm:items-center">
                <div className="flex flex-1 flex-col gap-1">
                  <p className="text-sm font-medium text-slate-200">Manual routine</p>
                  <p className="text-xs text-slate-400">Type "Hike tomorrow" or "Soccer Sat 8 AM" and we will build a NASA-backed plan.</p>
                </div>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <Input
                    value={customRoutineInput}
                    onChange={(event) => setCustomRoutineInput(event.target.value)}
                    className="border-slate-500/40 bg-slate-950/70 text-slate-100"
                    placeholder="e.g. Hike tomorrow"
                  />
                  <Button onClick={handleManualRoutineSave} className="bg-emerald-500 hover:bg-emerald-400">
                    Save routine
                  </Button>
                </div>
              </div>
              {customRoutinePreview && (
                <div className="mt-3 flex items-center gap-3 text-sm text-emerald-300">
                  <CheckCircle2 className="h-5 w-5" />
                  <span>Added routine: “{customRoutinePreview}”. NASA alerts will follow in your feed.</span>
                </div>
              )}
            </section>
          </div>
        </section>

        <section className="relative py-20">
          <div
            className="absolute inset-0 opacity-40"
            style={{
              backgroundImage: `linear-gradient(180deg, rgba(15,23,42,0.85), rgba(15,23,42,0.95)), url(${wizardBackgroundUrl})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          />
          <div className="relative mx-auto max-w-6xl px-6">
            <header className="mb-10 flex flex-col gap-2">
              <Badge className="w-fit bg-emerald-500/20 text-emerald-200 border border-emerald-300/30">
                How it works
              </Badge>
              <h2 className="text-3xl font-semibold">3 steps from NASA EarthData to action</h2>
              <p className="text-slate-300">
                Land the right plan with a responsive grid UI that keeps phone and desktop users aligned.
              </p>
            </header>
            <div className="grid gap-6 md:grid-cols-3">
              {wizardSteps.map((step) => (
                <div key={step.id} className="rounded-3xl border border-slate-200/10 bg-slate-950/80 p-6 backdrop-blur">
                  <div className="flex items-start justify-between gap-4">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-500/30 font-semibold">
                      {step.id}
                    </span>
                    <img src={step.iconUrl} alt="Step icon" className="h-10 w-10" />
                  </div>
                  <h3 className="mt-6 text-xl font-semibold text-slate-100">{step.title}</h3>
                  <p className="mt-2 text-sm text-slate-300">{step.description}</p>
                  <p className="mt-4 text-xs uppercase tracking-wide text-slate-400">{step.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-6 pb-20">
          <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-3xl font-semibold">NASA sensing dashboard</h2>
              <p className="text-sm text-slate-300">Swipe through satellite data cards for the full air, UV, heat, and rain story.</p>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <ShieldCheck className="h-5 w-5 text-emerald-300" />
              <span>Confidence weighted by coverage & retrieval reliability</span>
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
            <div className="grid gap-4 md:grid-cols-2">
              {nasaDatasets.map((dataset) => (
                <Card
                  key={dataset.id}
                  onMouseEnter={() => setSelectedDatasetId(dataset.id)}
                  className={`h-full border transition-all ${
                    selectedDatasetId === dataset.id
                      ? "border-sky-400/70 bg-slate-900/80 shadow-lg shadow-sky-900/30"
                      : "border-slate-800/80 bg-slate-950/40"
                  }`}
                >
                  <CardHeader className="flex flex-row items-start justify-between gap-3 pb-3">
                    <div>
                      <CardTitle className="text-lg text-slate-100">{dataset.name}</CardTitle>
                      <p className="text-sm text-slate-400">{dataset.primaryMetric}</p>
                    </div>
                    <img src={dataset.iconUrl} alt={`${dataset.short} icon`} className="h-9 w-9" />
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-semibold text-slate-100">{dataset.currentValue}</span>
                      <span className="text-sm text-slate-400">{dataset.unit}</span>
                    </div>
                    <Badge className={`border-none ${dataset.change < 0 ? "bg-emerald-500/20 text-emerald-200" : "bg-amber-500/20 text-amber-200"}`}>
                      {dataset.change > 0 ? "+" : ""}
                      {dataset.change}% · {dataset.changeLabel}
                    </Badge>
                    <p className="text-sm text-slate-300">{dataset.description}</p>
                    <ul className="space-y-2 text-xs text-slate-400">
                      {dataset.insights.map((insight) => (
                        <li key={insight} className="flex items-start gap-2">
                          <span className="mt-1 h-1.5 w-1.5 rounded-full bg-sky-300" />
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter className="pt-0 text-xs text-slate-400">
                    Accuracy: {(dataset.accuracy * 100).toFixed(0)}%
                  </CardFooter>
                </Card>
              ))}
            </div>

            <div className="flex flex-col gap-5 rounded-3xl border border-slate-200/10 bg-slate-950/60 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-semibold text-slate-100">Risk outlook</h3>
                  <p className="text-sm text-slate-400">{selectedRoutine?.label} · {selectedRoutine?.nextOccurrence}</p>
                </div>
                <Activity className="h-9 w-9 text-sky-300" />
              </div>
              <RiskChart labels={riskSeriesLabels} datasets={chartDatasets} />
              <div className="space-y-3 text-sm text-slate-300">
                <p>
                  {selectedDataset?.name} anchors your alerts. We watch for spikes above thresholds and
                  recalculate every 60 minutes.
                </p>
                <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-4 text-xs sm:text-sm">
                  <p className="font-semibold text-slate-100">Suggested activity windows</p>
                  <ul className="mt-3 space-y-2">
                    {recommendedWindows.map((window) => (
                      <li key={window.id} className="flex items-start gap-2 text-slate-300">
                        <CloudSun className="mt-0.5 h-4 w-4 text-sky-300" />
                        <span className="font-medium text-slate-100">{window.title}</span>
                        <span className="text-slate-400">• {window.window}</span>
                        <span className="block text-slate-400 md:inline"> — {window.detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="relative py-20">
          <div
            className="absolute inset-0 opacity-40"
            style={{
              backgroundImage: `linear-gradient(180deg, rgba(15,23,42,0.92), rgba(15,23,42,0.94)), url(${historyBackgroundUrl})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          />
          <div className="relative mx-auto max-w-6xl px-6">
            <div className="grid gap-8 lg:grid-cols-[0.9fr,1.1fr]">
              <div className="rounded-3xl border border-slate-200/10 bg-slate-950/70 p-6 backdrop-blur">
                <div className="flex items-center gap-3">
                  <BellRing className="h-6 w-6 text-amber-300" />
                  <h3 className="text-xl font-semibold text-slate-100">Live notifications</h3>
                </div>
                <p className="mt-2 text-sm text-slate-300">Push, SMS, and email alerts tuned to your risk tolerances.</p>
                <div className="mt-6 space-y-4">
                  {notificationMessages.map((notification) => (
                    <div
                      key={notification.id}
                      className={`rounded-2xl border p-4 text-sm transition-all ${
                        notification.emphasis === "warning"
                          ? "border-amber-500/40 bg-amber-500/10 text-amber-100"
                          : "border-slate-700/40 bg-slate-900/50 text-slate-200"
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs uppercase tracking-wide">
                        <span>{notification.timestamp}</span>
                        <span>{notification.channel.toUpperCase()}</span>
                      </div>
                      <p className="mt-2">{notification.message}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-3xl border border-slate-200/10 bg-slate-950/70 p-6 backdrop-blur">
                <div className="flex items-center gap-3">
                  <Compass className="h-6 w-6 text-emerald-300" />
                  <h3 className="text-xl font-semibold text-slate-100">Activity history</h3>
                </div>
                <p className="mt-2 text-sm text-slate-300">
                  Review past adventures, their safety score, and how conditions changed along the way.
                </p>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  {activityHistory.map((item) => (
                    <div key={item.id} className="rounded-2xl border border-slate-700/50 bg-slate-900/60 p-4">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-lg font-semibold text-slate-100">{item.activity}</p>
                        <Badge
                          className={`border-none ${
                            item.status === "completed"
                              ? "bg-emerald-500/20 text-emerald-200"
                              : item.status === "adjusted"
                                ? "bg-amber-500/20 text-amber-200"
                                : "bg-slate-500/20 text-slate-200"
                          }`}
                        >
                          {item.status}
                        </Badge>
                      </div>
                      <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{item.date}</p>
                      <div className="mt-2 flex items-center gap-2 text-sm text-slate-300">
                        <MapPin className="h-4 w-4 text-sky-300" />
                        {item.location}
                      </div>
                      <p className="mt-3 text-xs text-slate-400">{item.conditions}</p>
                      <p className="mt-4 text-sm font-semibold text-slate-100">Safety score: {item.score}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <footer className="border-t border-slate-800/80 bg-slate-950/90">
          <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-10 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold text-slate-200">Safe Outdoor v3.0</p>
              <p>Built for NASA Space Apps Challenge 2025 · From EarthData to Action</p>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-sky-300" /> Accuracy target ≥ {Math.round(accuracyTarget * 100)}%
              </span>
              <span className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-300" />
                Push notifications adjust plans automatically
              </span>
              <span className="flex items-center gap-2">
                <CloudSun className="h-4 w-4 text-emerald-300" /> NASA TEMPO · OMI · MERRA-2 · GPM
              </span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}
