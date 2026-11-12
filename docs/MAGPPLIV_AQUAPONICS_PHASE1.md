# MAGPPLIV Smart Aquaponics — Phase 1 prototype scope

MAGPPLIV is a FARM BRAIN module, not a separate application. Phase 1 records India R&D and UAE commercial-pilot workspaces in one application while keeping each farm, country, currency, access list and operating data separate.

## Workspace split

| Workspace mode | Country | Currency | Purpose |
|---|---|---|---|
| India R&D and prototype | IN | INR | Prototype design, experiments, fish/crop performance and research records |
| UAE commercial pilot | AE | AED | Existing partner-farm pilot planning, operating costs, production and commercial records |

Creating a workspace does not imply a university agreement, UAE farm agreement, installation or pilot launch. Those statuses must be updated only when evidenced.

## Navigation in the application

`Smart Aquaponics` → `Projects` → select/create a farm → `Overview` / `System` / `Water` / `Fish` / `Crops` / `Research` / `Finance` / `Alerts` / `Members`.

## Phase-1 functions

- Farm creation with country/mode enforcement and local currency.
- System configuration stored as farm-owned JSON, allowing the actual tank/filter/pump/grow-bed/sump/return-loop layout to be recorded without forcing one fixed physical design.
- Optional farm-specific pH, temperature, dissolved-oxygen, ammonia and nitrite limits. Thresholds are blank by default. The system generates a warning only when a farm has configured a limit and a manually entered value crosses it.
- Manual water measurements: temperature, pH, DO, TAN/ammonia, nitrite, nitrate, EC, level, flow and alkalinity.
- Tank registration and fish logs for feed, mortality, growth sampling and harvest. Estimated biomass is current count × last recorded average weight.
- Crop cycles with DWC/NFT/media-bed/ebb-and-flow/other method, population, planting/harvest dates and actual harvest quantity.
- Experiment registration with title, objective, hypothesis, test/control groups and observations.
- Finance entries in INR or AED according to workspace country. Reports do not convert currency or present accounting/audited financial results.
- CSV exports for water records and finance entries.
- Membership roles including owner, R&D manager, aquaculture/horticulture specialist, operator, research collaborator, partner-farm manager and read-only investor.

## Data reliability rules

- Every reading in Phase 1 is stored with `source=manual` and a user/time record.
- No reading is called live, connected or sensor-derived until a real device has authenticated and sent telemetry through a verified integration.
- Thresholds must be set for the specific fish species, crop, system and measured units by a qualified specialist. No universal values are pre-filled.
- Alerts suggest inspection, repeat measurement and specialist review; they do not automatically prescribe chemical dosing, medication, feeding changes or pump operations.
- Finance shows recorded totals only, not break-even, ROI or investment returns.

## Later phases — not included in Phase 1

- Device registry, ESP32/Raspberry Pi/Arduino authentication, MQTT, real sensor ingestion, time-series monitoring and calibration history.
- Power/pump/feeder control, with fail-safe controls and manual override after engineering risk review.
- More complete resource consumption and equipment maintenance logs.
- Verified research attachment management and prototype version history.
- AI-assisted trend explanations and forecasting with explicit source/assumption visibility and expert review.
- PDF/Excel investor reports, cross-currency reporting with dated FX rate source and multi-farm benchmarking.

## Suggested acceptance checks

1. A member can create separate India R&D (INR) and UAE pilot (AED) workspaces.
2. A workspace member cannot read another farm without membership.
3. An investor/read-only member cannot submit a system, fish, crop, research or finance change.
4. A manual water reading remains labelled manual.
5. No alert is created when no matching farm threshold exists.
6. An alert is created when a manually recorded value crosses a configured threshold.
7. Mortality/harvest count cannot reduce fish population below zero.
8. CSV reports include timestamps, source and units.
9. Workspace currency cannot be changed by selecting a different currency in a form; it is determined by the workspace country/mode.
