# Security and Next Steps

## Security baseline

Store all credentials in GitHub Actions secrets. Restrict repository write access and enable branch protection if this repository is shared. Use a dedicated Gmail sender account when possible. Rotate the Gmail app password and LLM key if they are exposed. Do not include article contents or credentials in debug logs.

The workflow grants only `contents: read`. It does not use repository write tokens. The LLM receives public feed text, so do not add private or regulated sources without reviewing the provider's data handling terms.

## Planned improvements

1. Add a durable URL ledger to prevent duplicate articles across overlapping runs.
2. Add article-body extraction and canonical URL normalization for feeds with sparse summaries.
3. Add source-specific parsers for regulatory disclosures and authenticated APIs.
4. Add a dry-run mode and a staging recipient for safer prompt and formatting changes.
5. Add a second-pass factuality/citation checker for high-stakes briefings.
6. Add Slack or Discord delivery as an optional adapter without changing synthesis or PDF logic.
