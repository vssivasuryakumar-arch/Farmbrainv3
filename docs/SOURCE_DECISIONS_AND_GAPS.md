# FARM BRAIN — source comparison, decisions and open gaps

## Material compared

1. `FARM_BRAIN_Claude_Master_Prompt_200K.md` (the long controlling master brief, including 128 named route specifications).
2. `FARM_BRAIN_Engineering_Specification_v1.0.docx`, dated **3 November 2026** (engineering proposal, architecture, data model, P0/P1/P2 requirements, budget and sprint plan).
3. Earlier FARM BRAIN project conversations summarized in the current project context, including India R&D / UAE commercial pilot strategy, the existing Flask demo, the previous Render URL and earlier funding discussions.

The original FARM BOOK / pitch PDFs and Figma designs are referenced by the project materials. This code handoff does not claim that every page/frame of those source files was independently re-audited in this pass.

## Decisions retained consistently

- FARM BRAIN is the only active product brand; FARM BOOK is the source concept.
- One identity supports multiple capabilities.
- Four product divisions are retained: Agri Products, Agri Business, Livestock and Farm Aid.
- Offer/supply and requirement/demand are different records.
- Enquiry, quotation, completed trade, payment and delivery must remain distinct.
- Transport needs separate load-request and vehicle-availability workflows.
- India is the first validation market and R&D base. UAE commercial development may progress in parallel through an existing-farm/partner pilot approach, but no pilot/partner is represented as signed or live without evidence.
- Finance/investor, veterinary, livestock, labour, farm input, land and payment features need appropriate safety, privacy and legal boundaries.
- The platform should be globally configurable, not hard-coded as India-only.
- AI knowledge services are a future capability requiring approved knowledge sources and evaluation, not a claim about the currently running website.

## Differences that must remain visible

| Topic | Engineering Specification v1.0 (03 Nov 2026) | Master brief / earlier chat context | Treatment in this code handoff |
|---|---|---|---|
| Initial budget | ₹25–30 lakh software-development planning envelope; excludes major post-launch operating costs unless contracted | Earlier chats included a ₹50 lakh–₹2 crore fundraising target; the master brief also retains an older ₹75–86.5 lakh raise estimate and says to rebuild it from evidence | Not combined. These are different planning contexts, not a confirmed current budget or fundraise |
| Delivery timeline | Approximately 16–20 weeks / 8–9 sprints as a planning target | Master brief says historical week estimates are rough and should be recalculated from actual scope/team | No delivery timeline promise in code |
| Mobile app | Engineering spec's platforms field says Web + Android + iOS, and its MVP table includes responsive web and mobile apps with shared APIs | Master brief's roadmap places native mobile in a later phase after web validation | Keep responsive web first in this founder MVP; mobile apps remain a product-owner decision |
| MVP contents | P0 includes verification, profiles/businesses, categories, listing lifecycle, search, enquiries, saved, reporting, moderation, admin, notifications, localization and audit | Master brief expands to 128 routes and phased scope, and says do not imply unavailable tools are complete | This package intentionally implements only a subset; missing P0 items are clearly listed below |
| AI | Engineering spec includes a grounded AI knowledge assistant as P2 / release 1.3 with curated sources and citations | Master brief does not supply a deployed model, model provider, API key or reviewed knowledge base | No AI model connected. AI stays in the future roadmap |

## Important gap: this package is not the full release-1.0 engineering MVP

The Engineering Specification's MVP acceptance criteria include contact verification and password recovery, listing edit/pause/archive, report and moderation workflows, admin category/user/listing tools, notifications, localization, audit records and farm/business profiles. These are not in the current GitHub package. The package is a local-first functional foundation for the listing/enquiry journey, not a production-ready or complete MVP under that specification.

## Scope of the next source audit

Before contracting a development team or public launch:

1. Compare the original FARM BOOK PDF and project pitch deck, page by page, with the normalized category taxonomy.
2. Review the `fb` and `af_1` Figma files and the Interactive Prototype page against actual routes and responsive breakpoints.
3. Review the existing private `farm-brain-demo` GitHub repository and Render deployment without overwriting it.
4. Confirm MVP priority, budget inclusions, business ownership/IP, technical lead, repository organization, cloud account ownership and pilot geography.
5. Choose contact policy (in-app enquiry, phone reveal or both) and listing moderation policy.
6. Approve the first category/unit taxonomy and user roles.
7. Confirm whether mobile apps belong in the initial paid delivery or a later phase.
8. Define the AI assistant's approved knowledge sources, scope, refusal boundaries, evaluation and privacy model before any AI API is connected.
