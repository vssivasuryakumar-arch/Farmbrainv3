# FARM BRAIN AI layer — future integration plan

## Status

**Not implemented in this repository.** No model provider, API key, AI endpoint or approved document corpus was supplied. The website can run without an AI integration.

The Engineering Specification v1.0 describes a grounded knowledge assistant as P2 / release 1.3. Its proposed behavior is to answer from approved knowledge sources with citations and uncertainty cues. This is a future module, not an assumption that a general-purpose model can safely answer every agriculture question.

## Safe first use cases

1. Help a user choose a category and improve a listing title/description.
2. Convert a natural-language search into division/category/location filters.
3. Explain how to use FARM BRAIN features and guide a user to the correct workflow.
4. Retrieve reviewed farming knowledge with a source link and date.
5. Explain why a marketplace result matched a query, without promising trade success.

## Do not use the model as the authority for

- Veterinary diagnosis, treatment decisions or emergencies.
- Pesticide/fertilizer dosage, chemical safety or product certification.
- Financial, investment, lending or insurance advice.
- Land title, legal compliance, identity or professional credential verification.
- Guaranteed crop price, quality, yield, funding, jobs, sale or delivery.

These cases need reviewed specialist sources, clear scope limits, escalation and human review where appropriate.

## Proposed architecture

```text
Website / mobile app
        │
        ▼
Authenticated FARM BRAIN API
        │  user consent + role + country + language + rate limits
        ▼
AI orchestration service
        ├── Intent / category router
        ├── Retrieval from approved knowledge index
        ├── Policy and safety checks
        ├── Model provider adapter (selected later)
        └── Output verifier / citation formatter
                 │
                 ▼
Response + cited sources + uncertainty + report option
```

- Retrieval should be scoped by the user's access rights. Private business records and messages must never be returned to another user's answer.
- Knowledge sources need an owner, review date, jurisdiction, language, version and expiry/review schedule.
- Answers should distinguish sourced facts from model-generated suggestions and show when a source is missing or stale.
- Store only the minimum conversation data needed for safety, quality and user-visible history.
- Do not train on private chats or use them in a shared knowledge index without clear user permission and a lawful basis.
- Log evaluation metadata without exposing secrets or sensitive personal content.

## Before enabling an AI provider

1. Select and approve the provider, model, region, data-retention terms and cost controls.
2. Define the knowledge corpus and content-review owner.
3. Define per-country/locale rules and risky-topic escalation.
4. Build offline evaluation questions for Tamil and English first, then other approved languages.
5. Test retrieval correctness, citation accuracy, harmful advice, refusal behavior, prompt injection and cross-user data leakage.
6. Add API rate limits, token budgets, abuse reporting, latency monitoring and fallback behavior.
7. Keep AI output as assistance; users make decisions and the platform does not certify the answer.
