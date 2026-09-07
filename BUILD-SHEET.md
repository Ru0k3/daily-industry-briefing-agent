# Build Sheet: Scheduled Industry Briefing Agent

## Outcome

Deliver one source-grounded technical industry briefing PDF to the user's Gmail each morning at 08:00 UTC.

## Provider-neutral contract

| Concept | Implementation |
|---|---|
| Agent | Prompt and synthesis logic in `industry_briefing.py` |
| Session | One isolated GitHub Actions run per day |
| Tools | RSS/Atom HTTP fetch, OpenAI-compatible LLM call, ReportLab PDF renderer, Gmail SMTP |
| Environment | Ubuntu GitHub-hosted runner with Python 3.12 |
| Outcome | PDF generated and attached to a Gmail message |
| Memory | None required for v0; URL deduplication is per run |
| Approval gate | Initial manual workflow run is recommended before enabling unattended schedule |
| Deployment | `.github/workflows/daily-industry-briefing.yml` |
| Adapter | OpenAI-compatible API configuration via `LLM_BASE_URL` |

## Success criteria

A successful run fetches recent feed items, produces valid structured JSON from the model, renders a readable PDF, and sends the PDF through Gmail SMTP. Missing or failed feeds are non-fatal. Missing secrets or an LLM failure fail the workflow visibly for recovery.

## Main assumptions

The user supplies the destination Gmail address through `GMAIL_TO`, a Gmail app password, an LLM provider key, and any private feeds. The system uses public RSS/Atom metadata by default and does not bypass paywalls or authentication.
