# FARM BRAIN — technical architecture and data rules

## Current implementation

A beginner-friendly modular Flask monolith is used for this first runnable website. It keeps HTML rendering, domain rules and database access in a small codebase that can be installed on Windows with Python. SQLAlchemy is used rather than hand-built SQL strings. SQLite is the local development database; PostgreSQL URLs are supported for a hosted deployment.

This is a pragmatic first implementation based on the earlier Flask demo in the project history. Render's Blueprint provides a hosted PostgreSQL database; local SQLite remains for developer setup and tests. The database tables added in this release are additive to the earlier model. `db.create_all()` creates missing tables and the startup backfill adds missing member profiles; future changes to existing columns require an explicit migration before deployment. It does not supersede the longer-term architecture candidate in the master brief.

## Future architecture candidate (source-derived recommendation)

When the team and product maturity justify it, evaluate a modular API-first architecture:

- Web: Next.js + React + TypeScript
- Backend: FastAPI + Pydantic + SQLAlchemy 2 + Alembic
- Database: PostgreSQL; add PostGIS only for suitable, privacy-reviewed location features
- Mobile later: React Native + Expo reusing the API and domain logic
- Object storage: S3-compatible private storage for media/documents
- Redis/background workers only when the actual workload requires them
- Managed authentication or a proven security-tested identity design
- Docker, automated tests, structured logs, monitoring and backups

Do not migrate purely for fashion. Validate the team's skill, hosting, operations and integration needs before locking this in.

## Conceptual entity model

| Entity | Ownership / relationship | Purpose | Current implementation |
|---|---|---|---|
| User | Account identity | Sign-in, personal contact basics and country | `User` |
| CapabilityAssignment | Many per user | A single account can hold multiple capabilities | `CapabilityAssignment` |
| MemberProfile | One per user | Public member/farm details, profile visibility and farmer-free plan code | `MemberProfile` |
| BusinessProfile | One per user in this release | Business profile and self-reported attributes; verification status remains not verified | `BusinessProfile` |
| Organization | Separate from personal identity | Shared business/farm context | Planned |
| OrganizationMembership | User + organization + permission | Multi-member organization access | Planned |
| Listing | One owner; division/category; type and status | Common offer/requirement discovery record | `Listing` |
| Enquiry | Sender + listing | A request for contact/details | `Enquiry` |
| Quotation | Enquiry + sender | Indicative terms; not a confirmed transaction | `Quotation` |
| SavedListing | User + listing, unique pair | Save an item for later | `SavedListing` |
| CommunityPost | User | Community updates and questions | `CommunityPost` |
| InventoryItem | User or future organization | Item quantity/unit and threshold | `InventoryItem` |
| StockMovement | Inventory item + user | Auditable quantity adjustment | `StockMovement` |
| TransportDetail | One-to-one typed extension to a listing | Load request or vehicle-availability detail fields | `TransportDetail` plus `Listing.transport_kind` |
| JobPosting / JobApplication | Employer + applicant | Recruitment lifecycle | Planned |
| InternshipOpportunity | Host + candidate | Learning opportunity lifecycle | Planned |
| VetProfile / VetServiceAvailability | Professional + provider | Directory and service availability | Planned |
| VerificationCase | Subject + reviewer | Evidence review and status | Planned |
| ContentReport | Reporter + target + reviewer | Content safety and moderation queue | `ContentReport` |
| AdminAudit | Admin + action + target | Reasoned moderation decision history | `AdminAudit` |
| Notification | Recipient | In-app profile follow and comment notifications | `Notification` |
| CropCycle | User | Personal crop/season record book | `CropCycle` |
| Subscription / Invoice / PaymentAttempt | User/org + provider | Billing after legal/provider readiness | Planned; Farmer Basic free code only |
| CountryConfiguration | Country code | Country-specific settings, policies and feature flags | Starter country/currency allow-list only |

## Core relationship sketch

```text
User 1 ─── * CapabilityAssignment
User 1 ─── * Listing
User 1 ─── * CommunityPost
User 1 ─── 1 MemberProfile
User 1 ─── * InventoryItem
User 1 ─── * CropCycle
User 1 ─── * Notification
User * ─── * User (through ProfileFollow)
CommunityPost * ─── * User (through PostLike)
User * ─── * Listing (through SavedListing)
Listing 1 ─── * Enquiry
Enquiry 1 ─── * Quotation
InventoryItem 1 ─── * StockMovement
```

Organizations, farm/business profiles and memberships will be added without merging multiple people's identity records into one shared login.

## State machines and domain boundaries

### Listing lifecycle

```text
active → paused → active
active → closed
paused → closed
```

The current UI creates active records. Owner edit/pause/close management screens are future work.

### Enquiry lifecycle

```text
new → responded → closed
```

The current UI creates `new` enquiries and moves to `responded` when a quotation is sent. Close/decline and spam controls are future work.

### Quotation lifecycle

```text
sent → accepted_for_discussion
sent → declined
```

`accepted_for_discussion` must never be presented as an accepted purchase order, payment, freight booking, confirmed supply or delivery evidence.

### Transport

- `load_request` is a requirement: a load needs a vehicle.
- `vehicle_availability` is an offer: a vehicle is available.
- They are stored as distinct typed listing records in this MVP. A full implementation should promote them to separate domain entities with stops, cargo, dates, vehicle class/capacity and pricing basis.
- No booking, tracking or delivery confirmation exists.

### Finance / investor discovery

Agri Business → Banks & Investors is forced to `discovery`. It must not be extended into brokerage, investment advice, credit decisioning, return promises or guaranteed funding without appropriate legal/provider review.

### Veterinary discovery

Listings are directory/enquiry records only. They do not mean credentials have been verified or that diagnosis, treatment, emergency care or telemedicine is available.

## Data rules

- Use UTC timestamps in storage; format for the user's local timezone at the interface layer.
- Store currency as an ISO 4217 code (for example INR, AED, USD), and amounts as decimal values, not floating point.
- Store quantity as decimal plus an explicit unit. Do not silently convert units without recording the source and normalized unit.
- Country is a code, not an unvalidated free-text string. Country activation and feature rules require a configuration layer.
- Exact farm coordinates and identity/verification documents must remain private by default.
- Never trust user-submitted owner IDs, organization IDs or permissions; derive them from the authenticated session and check ownership on the server.
- Add migrations before changing production database schema after real user data exists.

## API starter

`GET /api/v1/listings` is read-only and returns up to 50 active listings, optionally filtered by a valid division. `GET /api/v1/transport` returns public transport discovery records. `GET /api/v1/system/modules` reports module availability and integration status. `GET /api/v1/markets/mandi` calls the optional data.gov.in API connector when credentials and resource ID are configured; otherwise it returns an explicit not-configured response. A complete API should add versioned schemas, pagination, sorting, consistent error responses, authentication, authorization, rate limits, request IDs, idempotency where needed and audit events.

Future resource groups: `/auth`, `/users`, `/profiles`, `/organizations`, `/capabilities`, `/countries`, `/categories`, `/listings`, `/requirements`, `/rfqs`, `/quotations`, `/enquiries`, `/transport/loads`, `/transport/vehicles`, `/land`, `/machinery`, `/livestock`, `/veterinary`, `/careers/jobs`, `/internships`, `/community/posts`, `/inventory/items`, `/inventory/movements`, `/notifications`, `/subscriptions`, `/reports`, `/moderation`, `/verification`, `/audit`.

## Security checklist before a public launch

- Secret management; no `.env` or credentials in GitHub.
- HTTPS and secure session cookies.
- Email/phone verification, password reset and recovery rate limits.
- CSRF enabled for every form (enabled in current web build).
- Login and enquiry rate limits, spam controls, moderation appeals and user blocking.
- Formal permission tests for users, organizations and staff.
- Safe image/document upload, malware scanning and private storage.
- PostgreSQL backups, restore tests, migrations and monitoring.
- Privacy/consent, export/deletion, retention and country-specific legal review.
- Security dependency updates, audit logs and incident response.
