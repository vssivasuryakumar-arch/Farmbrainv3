# FARM BRAIN — source-to-code traceability

## Source used

Primary source: `FARM_BRAIN_Claude_Master_Prompt_200K.md` / user-attached `Pasted text.txt`, which captures the controlling project brief and its 128 route specifications. Earlier project conversations were also used for the following retained decisions: FARM BRAIN is the only current brand; four divisions; R&D remains in India; UAE commercial development can progress separately through a partner/farm pilot only when evidence exists; an earlier Flask/SQLite demo existed but was not production; and no fake claims about payments, bookings, vet services or investor/partner status.

This package does **not** claim to have completed a page-by-page audit of the original pitch PDFs, Figma files or private GitHub repository. The route catalogue below is taken from the master brief's named route list. Where source files need visual/page verification, that work remains open.

## Traceability matrix

| Source requirement | Route references | Code artefact | Test / evidence | Status |
|---|---|---|---|---|
| Current brand FARM BRAIN | 001, 013, 029, 043, 064, 074 | `templates/base.html`, `home.html` | Home page test | Implemented |
| Single account with multiple capabilities | 002, 007, 009, 027 | `User`, `CapabilityAssignment`, registration route | `test_user_can_register_with_multiple_capabilities` | Partial; no capability editing or organization roles |
| Free Farmer Basic and public farmer/member profile | 021–024 | `MemberProfile`, registration, profile edit/view routes | `test_farmer_gets_free_public_profile`, `test_profile_edit_and_farm_crop_records` | Implemented for individual accounts; no farm ownership verification |
| Business identity card | 025–026 | `BusinessProfile`, `/business/profile` | Business form route (manual test) | Partial; self-reported, no KYC/verification queue |
| Social follow, like, comment, photo posts and notifications | 013, 016–018 | `ProfileFollow`, `PostLike`, `PostComment`, `PostAttachment`, `Notification` | `test_community_social_like_comment_and_follow`, `test_community_photo_upload_is_sanitised_and_visible` | Implemented for simple text/photo feed |
| India-first, country-aware platform | 006, 116, 126 | User country, listing country, INR/AED/USD | Manual registration/listing checks | Partial; no full language/unit/policy layer |
| Four divisions and taxonomy | 029, 043, 064, 074 | `taxonomy.py`, market filters | Marketplace page test | Partial; core taxonomy present, audit pending |
| Offer and requirement are separate | 032–035 | `Listing.record_type` | Offer workflow test | Implemented for common listing |
| Search and listing detail | 034–035 | `/market`, `/listing/<id>` | `test_home_and_market_render` | Implemented |
| Enquiry is not a sale | 037, 097 | `Enquiry`, detail page | Offer/enquiry/quote lifecycle test | Implemented |
| Quotation distinct from enquiry/trade | 038, 097 | `Quotation`, discussion-only state | Lifecycle test | Implemented for indicative quote |
| Transport load vs vehicle availability | 048–052 | `TransportDetail`, `Listing.transport_kind`, `/transport`, read-only API | `test_transport_load_and_vehicle_records_stay_distinct` | Implemented for discovery records; no booking/GPS/delivery |
| Finance/investor discovery only | 061–062 | Finance board and listing rule | Manual check | Partial |
| Community posting and feed | 013, 016–018 | `CommunityPost`, `/community`, `PostLike`, `PostComment`, `PostAttachment` | Social and photo upload tests | Implemented as simple text/photo social feed |
| Saved listings | 020 | `SavedListing`, detail save route | Manual check | Implemented |
| Career/job discovery | 083, 091–094 | Careers board and common listing type | Manual check | Partial; no applications or employer board |
| Learning/internship discovery | 089–090, 096 | Learning board | Manual check | Partial; no application lifecycle |
| Basic inventory and movements | 101–106 | `InventoryItem`, `StockMovement` | Existing product tests/manual stock checks | Implemented as basic register; no full ERP |
| Crop-cycle diary | Farm operations | `CropCycle`, `/farm-records` | `test_profile_edit_and_farm_crop_records` | Implemented as user-entered records only |
| Report and admin moderation | 112–117 | `ContentReport`, `AdminAudit`, `/admin/moderation` | `test_admin_moderation_requires_role_and_writes_audit` | Implemented for basic hide/resolve/dismiss; no appeals or verification |
| Email verification and password reset | 004–005 | `PendingRegistration`, `PasswordResetOTP`, SMTP mailer and auth routes | OTP registration and password reset tests | Implemented with email OTP; SMTP credentials required for real delivery; SMS OTP not included |
| Community photos and marketplace photos | 016, 032–035 | `PostAttachment`, `ListingAttachment`, Pillow upload validation | Community and marketplace image tests | Implemented for JPG/PNG/WEBP; persistent/Cloudinary storage must be configured for hosted use |
| Private inbox and attachments | Community/business communications | `DirectMessage`, `MessageAttachment`, `/inbox`, private media route | PDF private attachment access test | Implemented for direct messages and PDF/image attachments; no realtime chat/email inbox sync |
| MAGPPLIV aquaponics Phase 1 | Outside the FARM BOOK 128-route catalogue; separate user-provided MAGPPLIV specification | `AquaponicsFarm`, `AquaponicsMembership`, system, readings, fish, crops, experiments, finance, alerts | India/UAE workspace, manual readings/alerts, fish population tests | Implemented as manual-record MVP; no live sensors/AI/SCADA |
| Official agriculture information | Farm intelligence | `/farm-intelligence`, `data_integrations.py` | `test_official_data_sources_are_explicit_and_unconfigured_mandi_is_not_fake_live` | Optional mandi API; IMD/SHC/e-NAM external links only |
| Livestock and vet workflows | 064–073 | Taxonomy + generic listings only | No vet workflow test | Planned / generic discovery only |
| Farm Aid and modern farming | 074–090 | Taxonomy + generic listings | No specialist workflow test | Planned / partial generic listing |
| Billing, full admin dashboard and analytics | 107–122 | No billing/subscription/analytics engine | No automated coverage | Planned; basic content moderation is implemented |
| Account settings, privacy, security, export/deletion | 123–128 | Not implemented beyond password auth/session | No evidence | Planned |

## Evidence discipline

- **Implemented** means code is present; automated tests cover only the test named in the table. Real SMTP/Cloudinary/Render configuration still has to be supplied for hosted operation.
- **Partial** means a shared/generic version exists, but specialist attributes, permission rules or state handling remain incomplete.
- **Planned** means not present in this package.
- Source route titles and route keys are enumerated in `ROUTE_COVERAGE.md`.
- No Figma or private GitHub modification is claimed by this package.
