# Daily Industry Briefing Agent

This project adds a scheduled, serverless Python agent to GitHub Actions. At **08:00 UTC every morning**, it reads configured RSS feeds, keeps items from the previous 24 hours, asks an OpenAI-compatible chat-completions endpoint to synthesize a source-grounded technical briefing, renders the result as a clean PDF, and emails the PDF to a configured Gmail address.

## Architecture

| Stage | Implementation | Configuration |
|---|---|---|
| Schedule | GitHub Actions cron | `.github/workflows/daily-industry-briefing.yml` |
| Collection | RSS/Atom over HTTPS | `RSS_FEEDS` repository variable |
| Synthesis | Replaceable OpenAI-compatible adapter | `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` |
| PDF | ReportLab | Built in to the workflow |
| Delivery | Gmail SMTP over TLS | Gmail app password and recipient secrets |

The workflow is intentionally provider-neutral at the LLM boundary. Any endpoint compatible with the OpenAI Python client's chat-completions interface can be used by changing `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY`.

## GitHub configuration

In the repository settings, create these **Actions secrets**:

- `LLM_API_KEY`: API key for the selected OpenAI-compatible provider.
- `LLM_BASE_URL`: API base URL, such as `https://api.openai.com/v1`.
- `GMAIL_FROM`: Gmail address used to send the message.
- `GMAIL_TO`: Gmail address that should receive the briefing.
- `GMAIL_APP_PASSWORD`: A Gmail app password, not the normal account password.

Create these optional **Actions variables**:

- `LLM_MODEL`: Defaults to `gpt-4o-mini` in the workflow.
- `RSS_FEEDS`: Comma-separated RSS/Atom feed URLs. Defaults are applied by the Python script when the variable is blank.

### Gmail setup

The sending account must have two-step verification enabled. Create a dedicated app password in the Google Account security settings and store it only as `GMAIL_APP_PASSWORD`. Do not use the normal Gmail password. If the account is managed by an organization that disallows app passwords, use a transactional email provider's SMTP credentials instead and change `SMTP_HOST`, `SMTP_PORT`, and the related secrets in the workflow.

## First run

1. Add the secrets and optional variables above.
2. Open the **Actions** tab and run **Daily industry briefing** with **Run workflow**.
3. Confirm the email and inspect the uploaded PDF artifact.
4. After validation, the cron trigger runs each morning at 08:00 UTC.

GitHub Actions scheduled workflows can be delayed during periods of high platform load. The schedule is UTC and the workflow is also manually runnable for recovery.

## Local test

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-industry-briefing.txt
set -a; . .env; set +a
python industry_briefing.py
```

The script writes PDFs to `artifacts/` and sends the generated PDF as an email attachment. A local run therefore performs the external delivery action; use a test recipient or temporarily replace `send_email` with a dry-run while developing.

## Safety and reliability

The agent treats fetched article text as untrusted input and instructs the model not to follow embedded instructions. It uses HTTPS for feeds and Gmail SMTP TLS for delivery. Secrets are read only from environment variables. The generated PDF includes a verification disclaimer because summaries are machine-generated. Feed failures are logged and skipped so one unavailable source does not fail the entire collection stage.

The current implementation does not persist a cross-run database of article IDs. It deduplicates URLs within each run and uses a date-stamped artifact. If an exact-once delivery guarantee becomes important, add a durable run ledger or use GitHub's artifact/API state before sending.

## Extension points

The agent can be extended with authenticated disclosure feeds, a domain allowlist, article-body extraction, a Slack or Discord delivery adapter, an approval step, a richer citation section, or a second evaluator LLM. These should be added without putting credentials into source code.
