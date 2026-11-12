# FARM BRAIN — 128-route coverage catalogue

This catalogue preserves the 128 named routes in the controlling master brief. It is a coverage inventory, not a claim that all routes exist in the current website. Status is judged against the code in this repository. Since the latest prototype update, email OTP/password recovery, community and marketplace photo uploads, a private inbox with PDF/image attachments, and the separate MAGPPLIV Phase 1 aquaponics module have been added. See `TRACEABILITY.md` for implementation evidence and `ROADMAP.md` for sequencing. The MAGPPLIV module is an additional capability from the separate aquaponics specification, not a claim that the original FARM AID aquaponics-discovery route is fully implemented.

| Route | Module | Route title | Key | Current code status |
|---:|---|---|---|---|
| 001 | Identity | Welcome / landing | `welcome-landing` | Implemented — core flow |
| 002 | Identity | Sign up | `sign-up` | Implemented — core flow |
| 003 | Identity | Sign in | `sign-in` | Implemented — core flow |
| 004 | Identity | Contact verification | `contact-verification` | Partial — email OTP implemented; SMS/phone OTP planned |
| 005 | Identity | Password recovery | `password-recovery` | Implemented — email OTP password reset |
| 006 | Identity | Choose country and language | `choose-country-and-language` | Partial — generic/shared flow |
| 007 | Identity | Select capabilities | `select-capabilities` | Partial — generic/shared flow |
| 008 | Identity | Select divisions and interests | `select-divisions-and-interests` | Partial — generic/shared flow |
| 009 | Identity | Profile setup | `profile-setup` | Partial — generic/shared flow |
| 010 | Identity | Welcome / dashboard assembly | `welcome-dashboard-assembly` | Partial — generic/shared flow |
| 011 | Identity | Verification application | `verification-application` | Planned — not implemented |
| 012 | Identity | Organization invitation and join | `organization-invitation-and-join` | Planned — not implemented |
| 013 | Global Community | Home feed | `home-feed` | Partial — generic/shared flow |
| 014 | Global Community | Global explore | `global-explore` | Planned — not implemented |
| 015 | Global Community | Global search results | `global-search-results` | Planned — not implemented |
| 016 | Global Community | Community post composer | `community-post-composer` | Partial — generic/shared flow |
| 017 | Global Community | Community post detail | `community-post-detail` | Partial — generic/shared flow |
| 018 | Global Community | Questions and knowledge sharing | `questions-and-knowledge-sharing` | Partial — generic/shared flow |
| 019 | Global Community | User and organization directory | `user-and-organization-directory` | Planned — not implemented |
| 020 | Global Community | Saved items | `saved-items` | Partial — generic/shared flow |
| 021 | Profile And Organizations | Personal profile overview | `personal-profile-overview` | Partial — generic/shared flow |
| 022 | Profile And Organizations | Edit personal profile | `edit-personal-profile` | Implemented — member profile editor |
| 023 | Profile And Organizations | Farm profile overview | `farm-profile-overview` | Partial — farm fields appear in member profile |
| 024 | Profile And Organizations | Edit farm profile | `edit-farm-profile` | Implemented — farm fields in profile editor |
| 025 | Profile And Organizations | Business profile overview | `business-profile-overview` | Partial — business summary on member profile |
| 026 | Profile And Organizations | Edit business profile | `edit-business-profile` | Implemented — self-managed business editor |
| 027 | Profile And Organizations | Capability and role management | `capability-and-role-management` | Partial — generic/shared flow |
| 028 | Profile And Organizations | Organization members | `organization-members` | Planned — not implemented |
| 029 | Agri Products | Agri Products home | `agri-products-home` | Partial — generic/shared flow |
| 030 | Agri Products | Category browse | `category-browse` | Partial — generic/shared flow |
| 031 | Agri Products | Subcategory browse | `subcategory-browse` | Planned — not implemented |
| 032 | Agri Products | Offer listing form | `offer-listing-form` | Implemented — core flow |
| 033 | Agri Products | Buyer requirement form | `buyer-requirement-form` | Implemented — core flow |
| 034 | Agri Products | Product results | `product-results` | Implemented — core flow |
| 035 | Agri Products | Product listing detail | `product-listing-detail` | Implemented — core flow |
| 036 | Agri Products | Product edit/manage | `product-edit-manage` | Planned — not implemented |
| 037 | Agri Products | Product enquiry composer | `product-enquiry-composer` | Implemented — core flow |
| 038 | Agri Products | Product quotation response | `product-quotation-response` | Partial — generic/shared flow |
| 039 | Agri Products | Product category administration | `product-category-administration` | Planned — not implemented |
| 040 | Agri Products | Product quality and grade guidance | `product-quality-and-grade-guidance` | Planned — not implemented |
| 041 | Agri Products | Product media gallery | `product-media-gallery` | Planned — not implemented |
| 042 | Agri Products | Product saved search | `product-saved-search` | Planned — not implemented |
| 043 | Agri Business | Agri Business home | `agri-business-home` | Partial — generic/shared flow |
| 044 | Agri Business | Factory directory | `factory-directory` | Partial — generic/shared flow |
| 045 | Agri Business | Factory requirement form | `factory-requirement-form` | Partial — generic/shared flow |
| 046 | Agri Business | Factory supplier offers | `factory-supplier-offers` | Partial — generic/shared flow |
| 047 | Agri Business | Factory requirement detail | `factory-requirement-detail` | Partial — generic/shared flow |
| 048 | Agri Business | Transport home | `transport-home` | Partial — generic/shared flow |
| 049 | Agri Business | Need a truck / load request | `need-a-truck-load-request` | Implemented — core flow |
| 050 | Agri Business | Vehicle available form | `vehicle-available-form` | Implemented — core flow |
| 051 | Agri Business | Transport search results | `transport-search-results` | Partial — generic/shared flow |
| 052 | Agri Business | Transport detail | `transport-detail` | Partial — generic/shared flow |
| 053 | Agri Business | Land marketplace | `land-marketplace` | Partial — generic/shared flow |
| 054 | Agri Business | Land listing form/detail | `land-listing-form-detail` | Partial — generic/shared flow |
| 055 | Agri Business | Machinery marketplace | `machinery-marketplace` | Partial — generic/shared flow |
| 056 | Agri Business | Machinery listing form | `machinery-listing-form` | Partial — generic/shared flow |
| 057 | Agri Business | Machinery detail and safety info | `machinery-detail-and-safety-info` | Partial — generic/shared flow |
| 058 | Agri Business | Electrical components marketplace | `electrical-components-marketplace` | Partial — generic/shared flow |
| 059 | Agri Business | Component detail and request | `component-detail-and-request` | Partial — generic/shared flow |
| 060 | Agri Business | Agriculture business updates | `agriculture-business-updates` | Planned — not implemented |
| 061 | Agri Business | Finance/investor discovery | `finance-investor-discovery` | Partial — generic/shared flow |
| 062 | Agri Business | Project presentation form | `project-presentation-form` | Partial — generic/shared flow |
| 063 | Agri Business | Business service directory | `business-service-directory` | Partial — generic/shared flow |
| 064 | Livestock | Livestock home | `livestock-home` | Partial — generic/shared flow |
| 065 | Livestock | Animal marketplace | `animal-marketplace` | Partial — generic/shared flow |
| 066 | Livestock | Animal listing form | `animal-listing-form` | Partial — generic/shared flow |
| 067 | Livestock | Livestock products | `livestock-products` | Partial — generic/shared flow |
| 068 | Livestock | Animal feed marketplace | `animal-feed-marketplace` | Partial — generic/shared flow |
| 069 | Livestock | Meat industry directory | `meat-industry-directory` | Partial — generic/shared flow |
| 070 | Livestock | Manure marketplace | `manure-marketplace` | Partial — generic/shared flow |
| 071 | Livestock | Veterinarian directory | `veterinarian-directory` | Partial — generic/shared flow |
| 072 | Livestock | Veterinary profile | `veterinary-profile` | Partial — generic/shared flow |
| 073 | Livestock | Veterinary consultation request | `veterinary-consultation-request` | Partial — generic/shared flow |
| 074 | Farm Aid | Farm Aid home | `farm-aid-home` | Partial — generic/shared flow |
| 075 | Farm Aid | Seed marketplace | `seed-marketplace` | Partial — generic/shared flow |
| 076 | Farm Aid | Seed offer/requirement form | `seed-offer-requirement-form` | Partial — generic/shared flow |
| 077 | Farm Aid | Nursery and saplings | `nursery-and-saplings` | Partial — generic/shared flow |
| 078 | Farm Aid | Farm-made products | `farm-made-products` | Partial — generic/shared flow |
| 079 | Farm Aid | Components and tools | `components-and-tools` | Partial — generic/shared flow |
| 080 | Farm Aid | Fertilizer marketplace | `fertilizer-marketplace` | Partial — generic/shared flow |
| 081 | Farm Aid | Crop/input question | `crop-input-question` | Planned — not implemented |
| 082 | Farm Aid | Farm machinery aid | `farm-machinery-aid` | Partial — generic/shared flow |
| 083 | Farm Aid | Farm labour jobs | `farm-labour-jobs` | Partial — generic/shared flow |
| 084 | Farm Aid | Farm labour posting/application | `farm-labour-posting-application` | Partial — generic/shared flow |
| 085 | Farm Aid | Modern farming hub | `modern-farming-hub` | Planned — not implemented |
| 086 | Farm Aid | Hydroponics discovery | `hydroponics-discovery` | Planned — not implemented |
| 087 | Farm Aid | Aquaponics discovery | `aquaponics-discovery` | Planned — not implemented |
| 088 | Farm Aid | Aeroponics discovery | `aeroponics-discovery` | Planned — not implemented |
| 089 | Farm Aid | Learning centre | `learning-centre` | Partial — generic/shared flow |
| 090 | Farm Aid | Internship opportunities | `internship-opportunities` | Partial — generic/shared flow |
| 091 | Careers And Operations | Job directory | `job-directory` | Partial — generic/shared flow |
| 092 | Careers And Operations | Job posting form | `job-posting-form` | Partial — generic/shared flow |
| 093 | Careers And Operations | Job detail | `job-detail` | Partial — generic/shared flow |
| 094 | Careers And Operations | Job application | `job-application` | Planned — not implemented |
| 095 | Careers And Operations | Employer applicant board | `employer-applicant-board` | Planned — not implemented |
| 096 | Careers And Operations | Internship application tracking | `internship-application-tracking` | Planned — not implemented |
| 097 | Careers And Operations | Inbox / enquiries | `inbox-enquiries` | Partial — generic/shared flow |
| 098 | Careers And Operations | Conversation detail | `conversation-detail` | Planned — not implemented |
| 099 | Careers And Operations | Notifications centre | `notifications-centre` | Planned — not implemented |
| 100 | Careers And Operations | Notification settings | `notification-settings` | Planned — not implemented |
| 101 | Careers And Operations | Basic inventory overview | `basic-inventory-overview` | Implemented — core flow |
| 102 | Careers And Operations | Inventory item list | `inventory-item-list` | Implemented — core flow |
| 103 | Careers And Operations | Inventory item detail | `inventory-item-detail` | Partial — generic/shared flow |
| 104 | Careers And Operations | Add inventory item | `add-inventory-item` | Implemented — core flow |
| 105 | Careers And Operations | Stock movement | `stock-movement` | Implemented — core flow |
| 106 | Careers And Operations | Low-stock alerts | `low-stock-alerts` | Implemented — core flow |
| 107 | Billing, Admin And Analytics | Plan comparison | `plan-comparison` | Planned — not implemented |
| 108 | Billing, Admin And Analytics | Upgrade bottom sheet | `upgrade-bottom-sheet` | Planned — not implemented |
| 109 | Billing, Admin And Analytics | Billing history | `billing-history` | Planned — not implemented |
| 110 | Billing, Admin And Analytics | Subscription management | `subscription-management` | Planned — not implemented |
| 111 | Billing, Admin And Analytics | Admin operations dashboard | `admin-operations-dashboard` | Planned — not implemented |
| 112 | Billing, Admin And Analytics | Listing moderation queue | `listing-moderation-queue` | Implemented — admin report/hide queue |
| 113 | Billing, Admin And Analytics | Community moderation | `community-moderation` | Implemented — reports and admin moderation |
| 114 | Billing, Admin And Analytics | User verification queue | `user-verification-queue` | Planned — not implemented |
| 115 | Billing, Admin And Analytics | Category/taxonomy admin | `category-taxonomy-admin` | Planned — not implemented |
| 116 | Billing, Admin And Analytics | Country and feature configuration | `country-and-feature-configuration` | Planned — not implemented |
| 117 | Billing, Admin And Analytics | Audit log | `audit-log` | Partial — admin moderation actions only |
| 118 | Billing, Admin And Analytics | Analytics overview | `analytics-overview` | Planned — not implemented |
| 119 | Billing, Admin And Analytics | Division performance report | `division-performance-report` | Planned — not implemented |
| 120 | Billing, Admin And Analytics | Seller performance report | `seller-performance-report` | Planned — not implemented |
| 121 | Billing, Admin And Analytics | Transport activity report | `transport-activity-report` | Planned — not implemented |
| 122 | Billing, Admin And Analytics | Inventory report | `inventory-report` | Planned — not implemented |
| 123 | Billing, Admin And Analytics | Account settings | `account-settings` | Planned — not implemented |
| 124 | Billing, Admin And Analytics | Privacy and visibility | `privacy-and-visibility` | Planned — not implemented |
| 125 | Billing, Admin And Analytics | Security and sessions | `security-and-sessions` | Planned — not implemented |
| 126 | Billing, Admin And Analytics | Language, units and currency | `language` | Planned — not implemented |
| 127 | Billing, Admin And Analytics | Help and support | `help-and-support` | Planned — not implemented |
| 128 | Billing, Admin And Analytics | Account data export/deletion | `account-data-export-deletion` | Planned — not implemented |

**Total source routes: 128.** Current code coverage: 21 routes implemented, 64 partially represented and 43 planned. These are catalogue-level classifications, not a claim that the entire product scope is complete.
