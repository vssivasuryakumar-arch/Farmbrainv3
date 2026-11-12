# Prototype boundaries and release checklist

## Working foundations in this package

- Registration with email OTP workflow, login, logout and email-code password reset.
- Profiles, avatar/cover photos, community posts, comments, likes, follows and reports.
- Public image uploads in community, profile and marketplace listings.
- Private user-to-user inbox with image/PDF attachment access restricted to sender/recipient.
- Agri marketplace offers/requirements, enquiries, quotations, saved listings, transport request vs vehicle availability, basic inventory and crop record book.
- Business discovery/profile, notifications and admin moderation.
- MAGPPLIV aquaponics Phase 1 records for separate India R&D and UAE pilot farms, manual readings, farm-set threshold alerts, fish/crop/research/finance, role-limited access and CSV output.
- Responsive website/PWA and Android WebView wrapper.

## Credentials / infrastructure required before real-world testing

| Capability | Required setup |
|---|---|
| Real email OTP / password reset | SMTP host, sender account, username and App Password/API credential stored as server secrets |
| Public photo persistence | Cloudinary credentials or a persistent object-storage service |
| Private message attachment persistence | Persistent server disk or private object storage with authenticated delivery |
| Production data | Managed PostgreSQL, backups and tested restore procedure |
| Founder admin role | Set `ADMIN_EMAIL` before account registration |
| Mandi prices | Official data.gov.in API key and exact dataset resource ID |
| Android app | Correct live HTTPS URL; GitHub Actions build; physical-device test |

## Not in this prototype

- SMS OTP, phone number verification and social login.
- Audio/video calls, push notification delivery, message read receipts beyond basic read-at timestamp, typing indicators, message search and abuse automation.
- Video upload/transcoding, private multi-file mail service or virus scanning.
- Payment gateway, escrow, GST invoices, e-signature, confirmed transport booking, GPS, dispatch and proof of delivery.
- Full accounting/ERP, advanced FPO management, warehouse WMS, cold-chain monitoring and complete career/job application workflow.
- Medical diagnosis, vet emergency triage, pesticide/chemical prescriptions or guaranteed finance/funding matching.
- Real IoT device registry, telemetry, calibration, MQTT, controls or automated pump/feeder operation.
- AI agronomy/aquaponics model with validated knowledge base, safety approval and audit controls.
- Cross-currency conversion, audited statements, break-even/ROI forecasting or investor-grade financial assurance.
- Native offline-first Android screens; current APK loads the hosted website.

## Before inviting external pilot users

- Run all backend tests in CI and resolve failures.
- Configure production SMTP and test inbox delivery, expired codes, resend cooldown and password reset.
- Configure image/private file storage; test upload limits, file type validation and access control.
- Enable database backups and restore test; document the data retention period.
- Configure admin access, moderation, reporting and a support/complaint contact.
- Add privacy policy, terms, community standards, consent and account deletion/export flow after legal review.
- Confirm local legal and licence requirements for agricultural trading, finance referrals, veterinary listings, employment, food safety and cross-border operations.
- For MAGPPLIV, have qualified aquaculture/horticulture specialists approve species/crop operating limits before enabling threshold alerts for a live farm. Keep sensor source, calibration and time-stamp provenance.
- Conduct device testing on low-end Android phones and weak 3G/4G connections.
