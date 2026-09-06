terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "run" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_service_account" "runtime" {
  account_id   = var.service_account_id
  display_name = "Provider-neutral agent Cloud Run runtime"
  project      = var.project_id
}

resource "google_secret_manager_secret" "provider_key" {
  project   = var.project_id
  secret_id = var.secret_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "provider_key" {
  count       = var.secret_value == null ? 0 : 1
  secret      = google_secret_manager_secret.provider_key.id
  secret_data = var.secret_value
}

resource "google_secret_manager_secret_iam_member" "runtime_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.provider_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "agent" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.runtime.email

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }

    containers {
      image = var.container_image

      ports {
        container_port = 8000
      }

      env {
        name  = "PROVIDER"
        value = var.provider
      }

      env {
        name  = "MODEL"
        value = var.model
      }

      env {
        name = var.provider == "claude" ? "ANTHROPIC_API_KEY" : var.provider == "gemini" ? "GEMINI_API_KEY" : "OPENAI_COMPATIBLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.provider_key.secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 2
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 6
      }
    }
  }

  depends_on = [
    google_project_service.run,
    google_secret_manager_secret_iam_member.runtime_accessor,
  ]
}
