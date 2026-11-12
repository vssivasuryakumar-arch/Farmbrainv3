# FARM BRAIN — product blueprint distilled from project history

## Evidence labels

- **Source-derived:** directly stated in the FARM BRAIN master brief and retained project decisions.
- **Current code:** what this repository actually implements and has test coverage for.
- **Recommendation:** a proposed next step, not a completed activity or verified external fact.
- **Open / unverified:** needs source inspection, user decision, partner evidence, legal review or a real integration.

## 1. Product vision (source-derived)

FARM BRAIN is a global agriculture community, discovery, marketplace, business-services and operating platform. It connects farmers, buyers, processors, factories, sellers, suppliers, transporters, land and machinery stakeholders, livestock participants, veterinarians, agricultural professionals, workers, students, employers and finance-seeking businesses.

The current brand is **FARM BRAIN**. FARM BOOK is the historical source concept only and must not appear as a competing brand in new product UI.

## 2. Four divisions and three story pillars

| Division | Source scope | Code status |
|---|---|---|
| Agri Products | Crops, produce, flowers, greens, vegetables, herbs, cereals, pulses, millets, spices, dry fruits, plantation/fibre/forage crops and seeds | Core marketplace records and search are implemented; product-specific quality, media and saved-search flows remain planned |
| Agri Business | Factory, sourcing, transport, land, machinery, electrical components, technical careers, updates, finance discovery and inventory | Generic listings, transport distinction, machinery/finance boards and basic inventory exist; detailed extensions and factory RFQs remain planned |
| Livestock | Animals, livestock products, feeds, meat industry, manure and veterinary directory/request | Taxonomy and generic listing capability exist; livestock-specific workflows and vet directory/consultation are planned |
| Farm Aid | Seeds, saplings, farm-made products, components, fertilizers, machinery, labour, modern farming, learning and internship | Taxonomy and generic listings exist; specialist input, labour, aquaponics/hydroponics/aeroponics and learning workflows remain planned |

FARM / BUSINESS / CAREER are story or marketing pillars, not additional divisions.

## 3. Identity and capability model

One account may carry several capabilities. Example combinations include farmer + buyer; seller + transporter; employer + student; or livestock keeper + farmer. Capability assignment must not create duplicate user accounts. Admin/moderator permissions must remain separate from member capabilities.

**Current code:** one user account, multiple self-declared capability assignments, email-OTP registration, password login/recovery, public member/farmer profile, farm profile fields, one business profile per member and automatic public-profile backfill for earlier accounts. Farmer / Grower accounts receive the `FARMER_BASIC_FREE` plan code. Avatar/cover uploads and community/listing photos are validated and resized. Durable hosted image storage needs Cloudinary or an equivalent configured store.

**Still needed:** organisation/FPO records and memberships, invitations, capability editing, formal role/permission matrix, country/language onboarding, identity/contact verification, business/farm evidence verification, profile privacy controls and account recovery. The profile and farm fields in this release do not prove land ownership, organic status, farm size or any other claim.

## 4. Core marketplace business logic

- **Offer / supply:** what the member can provide.
- **Requirement / demand:** what the member wants to source.
- **Enquiry:** a request for more information or contact.
- **Quotation:** an indicative proposal in response to an enquiry.
- **Accepted for discussion:** continue the conversation only. This is not a binding purchase, payment, delivery or completed trade.

These records must not be collapsed into a single “deal” status. Search may find related supply and demand, but a match does not guarantee a transaction.

**Current code:** separate offer and requirement types; filtered search; listing detail; saved listing; owner-only indicative quotation; buyer decision `accepted_for_discussion` / `declined`; transport is typed separately as a load request or vehicle availability.

**Still needed:** RFQ lifecycle, quote revisions/expiry, dispute evidence, independently agreed contract terms, verified completion and any lawful transaction/payment flow.

## 5. Special domain safeguards

| Area | Correct representation | Current MVP boundary |
|---|---|---|
| Transport | Separate load request from vehicle availability; capture origin, destination(s), cargo, weight/volume, vehicle class/capacity, dates and pricing basis in the specialist workflow | `transport_kind` distinguishes load vs vehicle availability. Discovery/enquiry only; no freight booking/tracking/delivery proof |
| Land | Buy/sell/rent/lease with area/unit, location, tenure and evidence privacy | Generic listing only; no title verification or property transaction |
| Machinery | Buy/sell/rent/lease with make/model, year, condition, capacity, specs and safety information | Generic listing only; no certification or inspection claims |
| Finance | Project/funder discovery and enquiry | Discovery only. No brokerage, lending, guaranteed funding, investment advice or return claims |
| Livestock/vet | Animal and vet directory/request workflows with proper safety controls | Generic directory/listing only; no diagnosis, emergency response, credential or health verification |
| Farm inputs | Seed/nursery/fertilizer discovery with quality and safe-use information | No quality certification or unsafe dosage claims |
| Labour | Fair work and safety safeguards | Generic careers listing only; no background checks, payroll or placement guarantee |
| Inventory | Item, quantity/unit, threshold and movement history | Basic stock register and adjustment ledger; not a full ERP/accounting system |
| Community safety | Reports, reviewer decision and audit record | Member reports and admin-only moderation; no appeals, automated spam system or block/mute tools |

## 6. Geography and operating strategy

**Source-derived strategy:** R&D remains in India; India is the first validation market. UAE commercial development may progress in parallel through an existing-farm/partner pilot approach. Do not describe any UAE partner, permit, pilot, funding or operation as signed/live unless independent evidence confirms it. Global profiles and discovery should be designed for country-aware configuration.

**Current code:** India default; India/UAE/US/UK/Other country codes as starter selections; INR/AED/USD/GBP currency options. No country-specific tax, payment, legal or import/export configuration is implemented.

**Next recommendation:** validate India-first workflows and user behavior, while investigating UAE partner/farm requirements separately. Activate payment, tax, logistics and regulated workflows only after the necessary providers and legal reviews are in place.

## 7. Product design direction from project history

- Deep forest `#142D23`; forest `#24523C`; harvest lime `#C7D97A`; warm ivory `#F5F3EA`; ink `#17211B`; secondary `#68756C`; border `#E4E8DF`; white `#FFFFFF`.
- Restrained premium bronze `#A77B3E`, champagne `#D9BD83`, soft gold `#F0E4C8` only for premium contexts; premium styling is not enabled as billing in this build.
- Responsive 12-column desktop / 8-column tablet / 4-column mobile design intent; content max width ~1,280px; spacing increments 4/8/12/16/24/32/40/48/64/80px.
- UI typography direction: Manrope / DM Sans; system fallback ensures the site remains usable if remote fonts fail.
- Accessible form labels, keyboard focus, readable mobile stacking and reduced-motion support are in the stylesheet. A formal WCAG audit has not been performed.

## 8. Five reusable master templates from the brief

1. Dynamic dashboard
2. Master-detail list
3. Multi-step wizard
4. Settings/profile
5. Analytics/reporting

The web MVP currently uses responsive page shells, cards, filters, listing/detail views, community/photos, a private inbox and workspace sections. It does not yet implement all five complete reusable templates as a configurable route engine.

## 9. Strategic product stages

1. Identity, capabilities, taxonomy, listing, search, detail and enquiry.
2. RFQ/quotation, factory, transport, land, machinery, inventory and careers.
3. Livestock, Farm Aid, modern farming, learning/internship and community safety.
4. Entitlements, payment only after legal/provider readiness; UAE country configuration and pilot evidence.
5. Mobile apps, scale, analytics and evaluated AI-assisted discovery/recommendations.

The Engineering Specification v1.0 states a ₹25–30 lakh software-development planning envelope and 16–20 week / 8–9 sprint target. Earlier project chats discussed a ₹50 lakh–₹2 crore raise and the master brief mentions an older ₹75–86.5 lakh planning estimate. These are not the same measure and are not reconciled here; no current budget, raise, customer traction, revenue, team size, partner agreement or regulator approval is asserted by this codebase. See `SOURCE_DECISIONS_AND_GAPS.md`.

## 9.5 Agriculture data services (web research, 12 November 2026)

- **AGMARKNET / Open Government Data:** official daily wholesale market data includes minimum, maximum and modal price observations. The app has an optional API connector that remains disabled until the exact official resource ID and API key are configured and the endpoint succeeds. These observations must not be displayed as a guaranteed farm-gate price.
- **IMD Agromet:** the app links users to official block/district agriculture bulletins. It does not claim a direct IMD API connection or generate location-specific warnings itself.
- **Soil Health Card:** official integration guidance requires an API consumer registration and access token. The app links the official portal and guide but does not yet call the Soil Health Card API.
- **e-NAM:** the official portal is linked as an external service. FARM BRAIN does not claim empanelment or direct integration; any provider integration must follow the official process.

See `AGRICULTURE_DATA_SOURCES.md` for the source notes, direct official links and configuration checklist.

## 10. AI / model layer

A separate user-provided MAGPPLIV specification has a Phase 1 aquaponics workspace for India R&D and the UAE commercial pilot, including manual records and farm-defined threshold alerts. It is integrated as an additional FARM BRAIN module, not as a replacement for the FARM AID route taxonomy. IoT, automated control and AI aquaponics remain future phases. See `MAGPPLIV_AQUAPONICS_PHASE1.md`.

The Engineering Specification v1.0 lists a grounded AI knowledge assistant as a P2 capability / release 1.3, using approved sources, citations and uncertainty cues. The master brief also describes future evaluated AI-assisted discovery/recommendations. The documents do not provide a deployed AI model, API key, model provider or permissioned chat dataset. **No AI assistant is connected in this repository.**

Recommended future AI uses: listing/category assistance, natural-language search, crop and input knowledge retrieval from reviewed sources, matching explanation and user-support triage. For any model feature, use scoped retrieval, citations/source timestamps where appropriate, consent and privacy filters; never make the model the authority for veterinary diagnosis, chemical dosage, financial advice, land title, identity verification or guaranteed price/quality. Do not train on private messages without an explicit lawful basis and user permission.
