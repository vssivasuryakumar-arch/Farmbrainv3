# FARM BRAIN — agriculture data-source register

Research checked: **12 November 2026**. This register distinguishes sources the current code can call from official information pages that are only linked. Availability and terms can change; re-check them before public launch.

## Market prices

### OGD Platform India / AGMARKNET

- Official catalog: https://data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi
- Resource page: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
- Variety-wise resource: https://data.gov.in/resource/variety-wise-daily-market-prices-data-commodity
- What it provides: daily wholesale minimum, maximum and modal prices reported from markets through AGMARKNET. The catalog displayed an update date of **31 October 2026** when researched; the resource pages showed updates on **28 October 2026** and **24 October 2026** respectively.
- Current code: `farm_brain/data_integrations.py` contains an optional API connector, and the interface reports `not_configured` until both `OGD_API_KEY` and `OGD_MANDI_RESOURCE_ID` are supplied.
- To activate: create/obtain an authorised OGD API key, identify the exact resource ID in the catalog's API details, set both secrets in hosting, test the returned JSON fields, and verify timestamps, market names, units, and missing-value handling. Never infer a price from a demonstration value.
- User display: show commodity, variety, market, date, price type (minimum / maximum / modal), currency and source. Explain that a mandi modal price is a reported wholesale reference, not a guaranteed farmgate selling price.

## Weather and crop advisories

### India Meteorological Department (IMD) — Agromet

- Agriculture meteorological services: https://mausam.imd.gov.in/responsive/servicesMetAgriculture.php
- Agromet advisory services: https://mausam.imd.gov.in/responsive/agromet_adv_ser_national_past_en.php
- Block-level bulletin index: https://mausam.imd.gov.in/responsive/agromet_adv_ser_block_past_en.php
- What it provides: IMD describes Gramin Krishi Mausam Seva, dissemination of agromet advisories, feedback and awareness, and training. Its advisory pages list district and block bulletins, including current local-language options.
- Current code: links to official IMD services are surfaced in Farm Intelligence. There is no direct live IMD API integration in this release.
- To activate a direct feed: identify an official data service and permitted access method with IMD; document scope, attribution, update cadence, geography, language, uptime and redistribution permissions; then add a source adapter and tests. Until then, link users to the current official bulletin, rather than copying stale forecasts into FARM BRAIN.
- Safety: display the issuing IMD office, bulletin issue date, district/block and language. Do not convert a general bulletin into personalised pesticide, irrigation or planting instructions.

## Soil information

### Soil Health Card

- Official portal: https://soilhealth.dac.gov.in/
- API integration guide: https://soilhealth.dac.gov.in/files/SHC_API_Integration_Guidelines.pdf
- What it provides: the portal and its API guide describe soil-health workflows and API integration, including API-consumer registration and authentication.
- Current code: the official portal and integration guide are linked. No Soil Health Card API calls are made by this release. `SOIL_HEALTH_API_TOKEN` is a configuration placeholder only; a token by itself does not confer approval or access.
- To activate: contact the responsible programme authority, complete the current API-consumer onboarding and authorisation, obtain the approved credentials and technical specifications, agree farmer consent and data-access rules, then implement and security-test the adapter. Until approved, farmers can maintain their own farm records but should retrieve official cards directly from the portal.

## Market participation and logistics

### e-NAM

- Official portal: https://www.enam.gov.in/web/
- Registration guidance: https://enam.gov.in/resources/registration-guideline
- What it provides: e-NAM describes a national electronic market linking participating APMC mandis. Its logistics module supports inbound and outbound supply-chain requirements, and its onboarding guidance describes stakeholder-specific registration and requirements.
- Current code: FARM BRAIN links to e-NAM as an external service. It does not log users into e-NAM, submit bids, create e-NAM trades, arrange payments, or claim e-NAM provider/empanelment status.
- To integrate: approach e-NAM/SFAC through the current official provider or integration process, confirm eligibility, contract, APIs, security review, data-sharing and operational obligations. Do not scrape authenticated pages or represent FARM BRAIN transport enquiries as e-NAM logistics bookings.

## Integration rules for developers

1. Store source, source URL, retrieval time, issue date, geography, unit and raw/normalised values with every external observation.
2. Cache external data with a stated freshness period and show the retrieval/issue date. If stale or unavailable, say so instead of silently presenting it as current.
3. Never combine prices from different markets, grades, varieties or units without an explicit conversion and provenance record.
4. Obtain consent before associating a farmer's account, land or crop records with external government services.
5. Keep tokens server-side in hosting secrets. Never include them in HTML, mobile APK resources, logs or the repository.
6. Add contract tests with provider-approved sample payloads and failure-mode tests before enabling a live adapter.

## Research basis

The official OGD catalog describes daily minimum, maximum and modal wholesale prices and its update history; the variety-wise resource lists state, district, market, commodity and variety fields. IMD documents its agricultural meteorological services and current/local district and block bulletin pathways. The Soil Health Card API guide documents API-consumer registration and integration. e-NAM's official pages describe its logistics module and registration process. These sources establish the external service pathways, not FARM BRAIN's entitlement to access them.
