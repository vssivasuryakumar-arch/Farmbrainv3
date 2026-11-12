# FARM BRAIN — build roadmap

This roadmap keeps the source brief's ambition but delivers it in testable stages. Route status is in `ROUTE_COVERAGE.md`.

## Phase 0 — evidence and architecture

- Preserve all existing source files and repositories.
- Audit the original pitch/specification PDFs and Figma files page by page when source access is available.
- Confirm the category taxonomy and resolve the source's category-count inconsistency.
- Validate India-first user segments, buyer/seller workflows and one pilot use case.
- Confirm product/legal scope for UAE commercial exploration separately.
- Agree on permissions, privacy, country configuration, support and moderation rules.

**Exit evidence:** source inventory, requirement traceability, approved taxonomy, data model, MVP acceptance checklist and decision log.

## Phase 1 — marketplace foundation (this code package)

- Single user identity with multiple capabilities.
- Four division taxonomy.
- Offer/requirement listing creation and search.
- Listing detail, save and enquiry.
- Indicative quotation and discussion-only acceptance.
- Responsive website shell and core error/empty states.
- Social-style community feed, member/farmer profiles, follow, likes, comments and in-app notifications.
- Free Farmer Basic plan code, business profile, crop-cycle diary and basic inventory movement history.
- Transport discovery board that distinguishes load requests from vehicle availability.
- Report queue, admin-only content moderation and moderation audit log.
- Optional official mandi-data connector and official IMD/Soil Health/e-NAM information links.
- Test suite, GitHub backend CI, Android APK workflow, Render Blueprint and local Windows runbook.

**Exit evidence:** automated tests pass; founder can register two roles, create an offer, create a requirement, enquire, quote and view both sides in their workspaces; mobile browser check complete.

## Phase 2 — deeper business operations

- Organization/FPO/farm entities, memberships and scoped permissions; make the current individual profile model organization-aware.
- Factory directory and structured RFQ lifecycle.
- Quotation revisions, expiry, decline, close and conversation thread.
- Specialist transport loads and vehicle availability entities.
- Land and machinery extensions with structured attributes and privacy.
- Job posts, applications and internship lifecycle.
- Inventory movement history, low-stock notifications and organization scope.

## Phase 3 — Livestock and Farm Aid

- Livestock-specific listing attributes and safer categorization.
- Vet directory and consultation request with explicit limitations and emergency guidance.
- Seed/nursery/fertilizer product-specific attributes and reviewed information.
- Farm labour fair-work and safety controls.
- Hydroponics, aquaponics and aeroponics project/service/learning discovery.
- Moderated learning and internship workflows.

## Phase 4 — governance, monetization and country operations

- Extend current moderation into verification cases, block/appeal flows, category/taxonomy administration and admin analytics.
- Country configuration for enabled features, language, units, currency and policy notices.
- Legal/provider review for payment, billing and any eligible transaction fee.
- Entitlement matrix and transparent subscription UX only after prices/benefits are validated.
- India pilot metrics and UAE partner/farm pilot evidence; do not imply a signed partnership before documentation.

## Phase 5 — scale and evaluated AI

- Native mobile clients when web workflows are validated.
- Notification delivery, analytics, observability and performance work.
- AI-assisted search, category help and knowledge retrieval using reviewed sources and privacy controls.
- Relevance ranking and recommendations only after sufficient clean data and evaluation.

## MVP acceptance walkthrough

1. Register one user as farmer + buyer.
2. Create an Agri Products offer.
3. Sign out and register a buyer account.
4. Create a buyer requirement.
5. Send an enquiry to the offer owner.
6. Sign in as the offer owner and send an indicative quotation.
7. Sign in as the buyer and accept it for discussion.
8. Confirm the UI explains that no trade, payment or delivery is confirmed.
9. Check the mobile layout, empty search and invalid form behavior.
10. Run `pytest -q` and retain the output with the release.

## Known risks / open decisions

- Category taxonomy should be checked against the original FARM BOOK source assets; a historic count inconsistency is mentioned in the master brief.
- The current MVP is one-user/one-listing scope; real farms/businesses need organization records and scoped permissions.
- Current country and currency choices are starter values, not complete localization.
- Basic report/moderation exists, but business verification, appeals, block/mute tools, automated spam prevention and full dispute handling do not; public commercial launch still needs governance and staffing.
- Finance, property, veterinary, labour, food, seed/fertilizer/input, privacy and payments need jurisdiction-specific review.
- Hosting must use a persistent PostgreSQL database and backups. Do not rely on an ephemeral SQLite file.
