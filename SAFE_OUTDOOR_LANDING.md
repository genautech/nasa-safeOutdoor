# Safe Outdoor v3.0 – Landing Experience

## Vision
A mobile-first, responsive web app crafted for the NASA Space Apps Challenge 2025 “From EarthData to Action.” Safe Outdoor v3.0 translates NASA’s TEMPO, OMI, MERRA-2, and GPM observations into timely guidance for everyday adventurers and outdoor professionals.

## Hero & Value Proposition
- **NASA Space Apps banner** announcing the challenge participation and data accuracy goal (≥90%).
- **Dual CTA buttons**: primary Fitbit sync and secondary demo mode.
- **Accuracy / Alerts / Offline cards** summarising Earth observation fidelity, proactive notifications, and cached readiness.
- **Contextual copy** linking personal data streams (wearables, calendars, manual plans) with NASA datasets.

## Auto-Detected Routine Selector
- Responsive grid of routines sourced from **Fitbit**, **Google Calendar**, and **manual inputs**.
- Each card surfaces location, timing, and personalised health focus.
- Manual entry bar encourages natural-language commands such as “Hike tomorrow,” instantly acknowledging the saved routine.

## Three-Step Wizard (Landing Education)
1. **Log in or sync** via wearable, calendar, or passwordless link.
2. **Receive condition alerts** driven by NASA TEMPO/OMI/MERRA-2/GPM fusion.
3. **Review activity history** capturing dates, locations, and environmental deltas.
- Visual inspiration drawn from responsive-grid layouts with vivid iconography sourced from Flaticon.

## NASA Sensing Dashboard
- Four dataset cards (TEMPO, OMI, MERRA-2, GPM) highlighting current metrics, trend deltas, insight bullets, and per-source accuracy.
- Hover/selection updates the adjacent **Chart.js multi-series risk graph** (respiratory, UV, heat stress, precipitation).
- Suggested activity windows blend NASA telemetry with personal routines.

## Notifications & History Strip
- Left column streams **push/SMS/email** alerts with emphasis colours for positive nudges vs. warnings.
- Right column displays adventure memories with safety scores, conditions, and statuses (completed/adjusted/skipped).
- Background gradients draw from Unsplash/Pexels imagery to reinforce outdoor storytelling.

## Offline & Reliability Messaging
- Top-of-page banner appears when offline, noting cached data usage.
- Service worker status presented in hero KPI card; manifests and cached assets keep guidance accessible without connectivity.

## Footer Highlights
- Reaffirms NASA data sources and push-adjusted itineraries.
- Reinforces the 90%+ accuracy mission and Space Apps context.

## Implementation Notes
- Built with **Next.js 15**, **React**, and **Tailwind CSS** for rapid responsive design.
- **Chart.js + react-chartjs-2** power the risk visualisation.
- Service worker (`public/sw.js`) handles offline caching; `useServiceWorkerRegistration` and `useOfflineStatus` keep UI stateful.
- All imagery references Unsplash/Pexels; icons sourced from Flaticon per challenge brief.
