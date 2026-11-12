# FARM BRAIN — functional pilot prototype

FARM BRAIN is the current brand and product. This repository carries forward the earlier FARM BOOK concept and the decisions captured in the FARM BRAIN master brief. It is a **functional pilot foundation**, not a claim that every item in the 128-route catalogue or every part of the global AgriTech vision is complete.

The prototype is designed to help validate the first agricultural network in India and the UAE: farmer identities and community activity, supply and demand listings, business enquiries, local transport discovery, simple farm records, and the first MAGPPLIV aquaponics operating workspace.

## What is implemented in this prototype

| Area | Implemented behaviour | Important boundary |
|---|---|---|
| Registration | Account registration is pending until the six-digit email code is verified; code expires and attempts are limited | Real delivery needs SMTP credentials; development mode can display a test code locally only |
| Login and recovery | Password login, email-code password reset, logout | No SMS OTP or social login in this release |
| Farmer / member profiles | Member profile, farm fields, avatar and cover image upload, capability tags, follow/unfollow | Identity and farm details are self-reported unless explicitly reviewed |
| Community | Post text, post photo, likes, comments, report content | No public short-video hosting or live group chat |
| Photos | Public community photo gallery, validated and resized image uploads | Public image storage should use Cloudinary or persistent server storage |
| Private inbox | User-to-user conversations, read markers, PDF and image attachments | Attachments are available only to conversation participants; production hosting needs persistent storage |
| Marketplace | Offers and requirements, division/category filters, listing details, enquiries, quotations, saved listings | Enquiry or quote is not a confirmed sale, payment or delivery |
| Agri Business | Business profile, machinery/land/service discovery and finance discovery | Finance is not lending, brokerage or investment advice |
| Transport | Separate load requests and vehicle availability, route/cargo/capacity fields | Discovery/enquiry only; no live GPS or freight booking |
| Inventory | Basic stock records and stock movements | Not an accounting package or full ERP |
| Farm records | Crop-cycle diary | Not an agronomy recommendation engine |
| Livestock / Farm Aid | Category and discovery foundations | Specialist clinical, animal-health and regulated workflows are not complete |
| Farm intelligence | Optional official mandi data connector and official advisory links | Requires an API key/resource ID; the app does not invent live data |
| MAGPPLIV aquaponics | India R&D and UAE pilot workspaces, configurable system record, manual water readings, farm-defined threshold alerts, fish tank/feeding/mortality/sample/harvest records, crop cycles, experiments, INR/AED finance records, CSV reports, member roles | No IoT device is connected; manual readings are labelled manual; this is not an automated control/SCADA system |
| Admin | Moderation queue, hide/resolve/dismiss and audit log | Set `ADMIN_EMAIL` on the server before the founder account is registered |
| Android | Android WebView app that opens the deployed FARM BRAIN website, supports back navigation, link handling and image/PDF file picker | Not a separate native offline app; it requires the website deployment |

## Run locally on Windows

1. Install Python 3.12.
2. Extract the repository ZIP.
3. Double-click `RUN_FARM_BRAIN.bat`.
4. The script creates a virtual environment and installs `requirements.txt` on first run.
5. Open `http://127.0.0.1:5000`.

Manual alternative from PowerShell in the repository folder:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python run.py
```

For local testing without SMTP, leave `APP_ENV=development` and `OTP_DEV_MODE=true`. The test OTP appears in the registration flash message / development log. This is **not** email delivery and must never be enabled in production.

## Configure real Gmail email OTP

FARM BRAIN sends registration and password-reset codes using SMTP. For Gmail SMTP:

- Set `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USE_TLS=true`.
- Set `SMTP_USERNAME` to the sending Gmail address.
- Set `MAIL_FROM` to that Gmail address (or a verified sender address).
- Use a Google App Password if Google requires it for the account; it is not the normal Gmail password. Enable Google 2-Step Verification first and keep the App Password secret.
- Set `SMTP_PASSWORD` only in Render Environment or another secret manager. Never commit it in `.env`, GitHub, screenshots, or source code.
- In production set `APP_ENV=production` and `OTP_DEV_MODE=false`. Missing SMTP credentials cause email operations to fail safely rather than exposing OTP values on the page.

See [`docs/EMAIL_AND_MEDIA_SETUP.md`](docs/EMAIL_AND_MEDIA_SETUP.md).

## Photo sharing and private attachments

- Community/profile images accept JPG/JPEG, PNG and WEBP. Images are validated by decoding, resized and re-encoded as JPEG. Limit: 6 MB each.
- Direct messages accept PDF or image attachments. Limit: 8 MB each.
- Private message files are served only after checking that the signed-in user is the sender or recipient of the message.
- If all Cloudinary credentials are set, public profile/community images go to Cloudinary. Private message files stay on the configured server disk.
- For Render, use a persistent disk for private attachments (the included Blueprint mounts it at `/var/data`). Without persistent storage, local files can disappear on restart/redeploy. Cloudinary is recommended for public photos.

## Deploy to Render

The root `render.yaml` defines a Render web service and PostgreSQL database in Singapore. Review plan and pricing before applying the Blueprint. The included web service and persistent disk use a paid service plan; Render persistent disks are not available on Free web services.

Required production environment settings include:

- `SECRET_KEY` (Render Blueprint generates it)
- `DATABASE_URL` (wired from the Blueprint database)
- `UPLOAD_FOLDER=/var/data/uploads`
- `APP_ENV=production`
- `OTP_DEV_MODE=false`
- `ADMIN_EMAIL`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `MAIL_FROM`

Optional Cloudinary values: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.

Optional data.gov.in values: `OGD_API_KEY`, `OGD_MANDI_RESOURCE_ID`.

Do not deploy the Android APK against the old demo URL unless that is where your current application is deployed. Update `android/app/src/main/res/values/strings.xml` (`default_website_url`) to the actual HTTPS Render service URL, then rebuild the APK through GitHub Actions.

## Tests and validation

Run locally after installing dependencies:

```powershell
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the backend tests and builds a debug APK. Static checks in the authoring environment confirmed Python compilation, Jinja parsing and XML parsing. The complete Flask test suite still needs to run in GitHub Actions because Flask packages could not be installed in the authoring environment. Do not describe the prototype as fully tested until that workflow is green.

## MAGPPLIV Smart Aquaponics — Phase 1

The aquaponics workspace is part of FARM BRAIN and has separate country/mode workspaces:

- India: `India R&D and prototype` (INR).
- UAE: `UAE commercial pilot` (AED).

The phase-1 workspace supports a farm-specific system configuration JSON, manually entered water-quality readings, optional site-defined thresholds, fish tanks and activity logs, crop cycles and harvest quantities, research experiments, operating expense/revenue entries and CSV reports. No default water-quality thresholds are supplied. A qualified aquaculture specialist must set and verify each farm's operating parameters. No dosing, medication or automated pump action is triggered.

The following are future phases, not implemented integrations: ESP32/Arduino/Raspberry Pi telemetry, MQTT, automatic feeders and pumps, device calibration, AI aquaponics recommendations, PDF investor reports and cross-currency financial consolidation.

See [`docs/MAGPPLIV_AQUAPONICS_PHASE1.md`](docs/MAGPPLIV_AQUAPONICS_PHASE1.md).

## Product guardrails

- Offer/supply and requirement/demand are separate listings.
- Enquiry is not an order. A quotation is indicative until parties contract independently.
- Transport posts are not freight bookings or proof of delivery.
- Finance listings are discovery/enquiry only.
- Vet discovery is not diagnosis or emergency response.
- No government farmer registry data is accessed without approval and consent.
- Manual water readings are not sensor telemetry.
- No biological, chemical or aquaculture safety thresholds are assumed universal.

## Licence and production readiness

This is a prototype codebase for product validation. Before public production use, arrange security review, privacy/terms/legal review, backups, monitoring, file retention/deletion policy, email deliverability and incident response; migrate schema changes with Alembic; test backup restoration; and conduct an Android device test matrix. Do not load real sensitive research/farm data until access and retention policies are agreed.
