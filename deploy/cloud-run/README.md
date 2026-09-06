# Deploy the Dockerized agent to Google Cloud Run

This example deploys the repository’s Docker image as a Cloud Run service. Cloud Run provides the `PORT` environment variable, and the container already listens on it. Store model credentials in Secret Manager rather than committing them to the repository. [1] [2]

## Prerequisites

Install and authenticate the Google Cloud CLI, select a project, and enable Cloud Run, Artifact Registry, and Secret Manager APIs:

```bash
gcloud auth login
gcloud auth configure-docker REGION-docker.pkg.dev
gcloud config set project PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

Replace `PROJECT_ID`, `REGION`, and `REPOSITORY` below. Create the Artifact Registry repository once:

```bash
gcloud artifacts repositories create REPOSITORY \
  --repository-format=docker \
  --location=REGION \
  --description='Provider-neutral agent containers'
```

## Build and push the image

From the repository root:

```bash
PROJECT_ID="$(gcloud config get-value project)"
REGION="us-central1"
REPOSITORY="agent-images"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/provider-neutral-agent:latest"

gcloud builds submit --tag "$IMAGE" .
```

Cloud Build is optional; you can build locally and push with Docker if your environment has Docker and Artifact Registry authentication configured.

## Configure a provider secret

For Gemini:

```bash
printf '%s' "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
```

For Claude:

```bash
printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
```

Grant the Cloud Run service identity access to the selected secret. Replace `SERVICE_ACCOUNT` with the runtime service account email:

```bash
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

Use the equivalent command for `anthropic-api-key` when deploying Claude.

## Deploy with gcloud

The simplest deployment is a stateless Cloud Run service. This example uses Gemini; change the provider and secret arguments for Claude or an OpenAI-compatible endpoint:

```bash
gcloud run deploy provider-neutral-agent \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --port 8000 \
  --service-account SERVICE_ACCOUNT \
  --set-env-vars PROVIDER=gemini,MODEL=gemini-2.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --no-allow-unauthenticated
```

For a public demo, replace `--no-allow-unauthenticated` with `--allow-unauthenticated`, but add application-level authentication before exposing `/run` to the internet. Cloud Run services can also be deployed from a YAML configuration with `gcloud run services replace service.yaml` after substituting the image and project values. [3]

## Test the service

Retrieve the service URL and call the health endpoint:

```bash
SERVICE_URL="$(gcloud run services describe provider-neutral-agent --region "$REGION" --format='value(status.url)')"
curl "$SERVICE_URL/health"
```

If authentication is required, use an identity token:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$SERVICE_URL/health"
```

## Claude, Ollama, and operational notes

For Claude, set `PROVIDER=claude`, `MODEL` to a currently supported Claude model, and reference `ANTHROPIC_API_KEY` with `--set-secrets`. For Ollama, do not place a large local model inside this small stateless service unless the selected Cloud Run configuration has suitable resources. Instead, run Ollama on a GPU-capable private host or use a managed endpoint, then set `PROVIDER=ollama` and `BASE_URL` to an authenticated private endpoint. Cloud Run service-to-service networking, VPC egress, request timeouts, concurrency, minimum instances, and cost should be designed for the expected agent workload.

Keep Cloud Run revisions immutable, pin image tags or digests for production, configure a staging service before production, and monitor logs and latency. Add a queue and a durable database for long-running or resumable agents; do not rely on one HTTP request for work that may exceed request limits.

## References

[1]: https://docs.cloud.google.com/run/docs/deploying — Google Cloud, Deploy container images to Cloud Run services
[2]: https://docs.cloud.google.com/run/docs/configuring/services/secrets — Google Cloud, Configure secrets for services
[3]: https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy — Google Cloud SDK, `gcloud run deploy`
