# Terraform for Cloud Run and Secret Manager

This module provisions the GCP resources required for the containerized provider-neutral agent: required APIs, a Cloud Run runtime service account, a Secret Manager secret, secret-access IAM, and a Cloud Run v2 service. The Cloud Run container receives the platform `PORT` contract and exposes `/health`.

## Before applying

Build and push the Docker image to Artifact Registry, then set `container_image` to the full image reference. Prefer an immutable digest in production. Authenticate Terraform with Application Default Credentials:

```bash
gcloud auth application-default login
```

Copy the example variables file and replace the project, image, provider, and model values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Do not put an API key in `terraform.tfvars`. If `secret_value` is supplied, the value is stored in Terraform state. The safer default is to leave it null and create the secret version out of band:

```bash
printf '%s' "$GEMINI_API_KEY" | gcloud secrets versions add provider-api-key --data-file=-
```

Create the secret itself first if it does not exist:

```bash
gcloud secrets create provider-api-key --replication-policy=automatic
printf '%s' "$GEMINI_API_KEY" | gcloud secrets versions add provider-api-key --data-file=-
```

## Apply

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

The configuration defaults to an internal load-balancer ingress policy. Change `ingress` in `main.tf` only after deciding how the service will be authenticated. For a public endpoint, add application authentication and rate limiting before changing the policy.

The selected provider secret is mapped automatically for Gemini and Claude. For an OpenAI-compatible endpoint, set `provider = "openai_compatible"` and ensure the endpoint and `BASE_URL` are configured in the service. Native Ollama is usually better hosted separately on a suitable private or GPU-capable machine; Cloud Run is not automatically a local-model host.

## Destroy

```bash
terraform destroy -var-file=terraform.tfvars
```

Destroying the Terraform-managed Secret Manager resource can be destructive. Use a separate state or lifecycle policy if the secret must outlive the Cloud Run service.
