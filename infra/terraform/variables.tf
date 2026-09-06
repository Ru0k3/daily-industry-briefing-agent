variable "project_id" {
  description = "GCP project hosting the Cloud Run service."
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and Artifact Registry."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "provider-neutral-agent"
}

variable "container_image" {
  description = "Fully qualified container image, preferably pinned by digest in production."
  type        = string
}

variable "provider" {
  description = "Model provider selected by the container."
  type        = string
  default     = "gemini"

  validation {
    condition     = contains(["gemini", "claude", "ollama", "openai_compatible", "mock"], var.provider)
    error_message = "provider must be gemini, claude, ollama, openai_compatible, or mock."
  }
}

variable "model" {
  description = "Provider model identifier."
  type        = string
  default     = "gemini-2.5-flash"
}

variable "secret_id" {
  description = "Secret Manager secret containing the selected provider API key."
  type        = string
  default     = "provider-api-key"
}

variable "secret_value" {
  description = "Optional initial secret value. Prefer creating the secret version outside Terraform to avoid storing the value in Terraform state."
  type        = string
  sensitive   = true
  default     = null
}

variable "service_account_id" {
  description = "Account ID for the Cloud Run runtime service account."
  type        = string
  default     = "provider-neutral-agent"
}

variable "min_instance_count" {
  description = "Minimum Cloud Run instances."
  type        = number
  default     = 0
}

variable "max_instance_count" {
  description = "Maximum Cloud Run instances."
  type        = number
  default     = 10
}
