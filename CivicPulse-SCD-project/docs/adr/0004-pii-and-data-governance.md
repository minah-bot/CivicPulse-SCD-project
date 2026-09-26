
ADR 0004: PII and Data Governance
Status
Accepted
Context
A complaint's text field is free-form — a citizen can write anything, including their own name, a phone number, or other identifying details, even though the form doesn't ask for that. Separately, ComplaintCreate has an explicit reporter_contact field for anyone who wants to be reachable about their complaint. When the real LlmProvider is active, complaint content is sent to a third-party API (Groq) to be classified — which means some decision has to be made about what leaves our own infrastructure and what doesn't.
Decision
Only text and location are ever sent to the LLM provider — this is visible directly in llm_provider.py's triage() signature, which takes exactly those two fields and nothing else. reporter_contact is never passed to triage() at all; it's stored in the database via models.py and used only for the backend's own record-keeping, not for classification, so it never reaches Groq or any other external API.
The system prompt in llm_provider.py also explicitly tells the model to treat the complaint text as data to classify, not as instructions to follow — this is a safeguard against a complaint containing something like "ignore previous instructions," rather than a data-minimization measure, but it's part of the same "what do we let external input do" thinking.
For any run using RuleProvider or SimulatedProvider (the default in dev and CI), no complaint data leaves the machine at all — both run entirely locally with no network call, so the PII question only actually applies to production runs using LlmProvider or OllamaProvider. OllamaProvider sends text to a locally-hosted model, so even there nothing leaves our own infrastructure — the third-party exposure is specific to LlmProvider alone.
We do not currently redact or scrub names/phone numbers a citizen might type into the complaint body itself before sending it to Groq — flagged honestly below as a limitation, since building real PII-detection is out of scope for this project's timeline.
Consequences
What this limits: reporter_contact — the field most likely to contain a direct personal identifier — structurally cannot reach the LLM provider, because the code path that calls triage() never has access to it in the first place. This isn't a policy we have to remember to follow; it's enforced by the function signature.
What this doesn't cover: if someone writes "my name is X, call me at Y" inside the complaint text field itself, that does reach Groq's API as part of normal classification, subject to Groq's own data usage terms. A production version of this system would likely want a redaction pass before the LLM call — this is named here as a known gap, not something we're claiming to have solved.

