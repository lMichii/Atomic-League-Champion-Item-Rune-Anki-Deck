# Author-model comparison — 2026-11-01

These bounded experiments reuse retained pilot-01 source packets, images, prompts,
schemas and core inventories. No candidates were imported. Production configuration,
editorial decisions and approved cards were not changed. They test author substitution,
with an independent `gpt-6.1-sol` checker, rather than replacing every generation stage.

| Candidate / source packet | Outcome | New attempts | Available input / output tokens | Elapsed |
| --- | --- | ---: | ---: | ---: |
| gpt-6-luna / Annie | Rejected by deterministic contracts twice | 2 | 50,748 / 5,007 | 40.88 s |
| gpt-6-luna / Karma | Structurally valid after repair; checker found two missing cores | 3 | 68,530 / 6,899 | 73.88 s |
| gpt-6.1-terra / Annie | Author passed contracts first attempt; verification incomplete | 3 | 53,298 / 10,550 | 413.77 s |

Totals include author repairs and independent checking, where executed. Terra's
checker timed out once, then returned an unknown source reference; one attempt
lacks usage. Its result is **inconclusive**, not proof of inferior author quality.
No candidate completed all quality gates in this small comparison.

Luna's first Annie response placed build focus on an ability; its repair introduced
a numeric claim without a matching cited number. On Karma, a repaired response
passed structural checks but omitted the overview's slowing behavior and Renewal's
missing-health-dependent healing. These are practical recognition/counterplay details,
not formatting preferences. The independent checker remains fallible; it grants no
editorial approval.

## Recommendation

Keep the production model unchanged. Luna is not a demonstrated replacement for
source-grounded champion authoring. Terra may merit a further **controlled** trial
after verification reliability is addressed, but this one incomplete case cannot
justify switching mass production. Do not spend further calls on benchmarks during
this batch. Do not downgrade core-inventory creation or independent verification.

Current standard API short-context list prices per million tokens are shown only
for context, checked against official documentation on 2026-11-01:

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| gpt-6.1-sol | $2.00 | $0.10 | $10.00 |
| gpt-6.1-terra | $1.00 | $0.05 | $5.00 |
| gpt-6-luna | $0.10 | $0.01 | $0.50 |

Sources: [API pricing](https://developers.openai.com/api/docs/pricing),
[model selection](https://developers.openai.com/api/docs/guides/model-selection),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra).

These are not Codex subscription charges or an invoice. Production uses the
authenticated runtime default, whose identity is not exposed by its retained
metadata; do not assign that workload a guessed model or dollar cost. Candidate
token totals also differ because of repairs, checking and missing receipts.

Prioritize completing cached runs, preserving accepted stages and avoiding repeated
retrieval/authoring. Any future prompt reduction must retain the cited core inventory,
variant context and validation evidence. Assess total calls, missing mechanics and
editorial correction time alongside token price.

Exact public request/response and error receipts are retained in the three
`pilot-02-*` experiment directories. Repeating a completed evaluation returns its
saved report with zero new calls. These experiments are not pending champion cards.
