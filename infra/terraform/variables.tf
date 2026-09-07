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

variable "model_provider" {
  description = "Model provider selected by the container."
  type        = string
  default     = "gemini"

  validation {
    condition     = contains(["gemini", "claude", "ollama", "openai_compatible", "mock"], var.model_provider)
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

variable "enable_redis" {
  description = "Provision Memorystore Redis and attach Cloud Run to the VPC."
  type        = bool
  default     = false
}

variable "network_name" {
  description = "Existing VPC network name used by the Redis instance and Serverless VPC Access connector."
  type        = string
  default     = "default"
}

variable "redis_tier" {
  description = "Memorystore Redis tier. BASIC is suitable for development; STANDARD_HA is recommended for production."
  type        = string
  default     = "BASIC"

  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.redis_tier)
    error_message = "redis_tier must be BASIC or STANDARD_HA."
  }
}

variable "redis_memory_size_gb" {
  description = "Memorystore Redis memory size in GiB."
  type        = number
  default     = 1
}
