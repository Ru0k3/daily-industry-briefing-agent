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

resource "google_project_service" "redis" {
  count              = var.enable_redis ? 1 : 0
  project            = var.project_id
  service            = "redis.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vpcaccess" {
  count              = var.enable_redis ? 1 : 0
  project            = var.project_id
  service            = "vpcaccess.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "servicenetworking" {
  count              = var.enable_redis ? 1 : 0
  project            = var.project_id
  service            = "servicenetworking.googleapis.com"
  disable_on_destroy = false
}

data "google_compute_network" "selected" {
  name    = var.network_name
  project = var.project_id
}

resource "google_compute_global_address" "private_service_range" {
  count         = var.enable_redis ? 1 : 0
  name          = "${var.service_name}-private-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = data.google_compute_network.selected.id
  project       = var.project_id

  depends_on = [google_project_service.redis]
}

resource "google_service_networking_connection" "private_service_access" {
  count                   = var.enable_redis ? 1 : 0
  network                 = data.google_compute_network.selected.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_range[0].name]

  depends_on = [google_project_service.redis, google_project_service.servicenetworking]
}

resource "google_vpc_access_connector" "agent" {
  count         = var.enable_redis ? 1 : 0
  name          = "${var.service_name}-vpc"
  region        = var.region
  project       = var.project_id
  network       = data.google_compute_network.selected.name
  ip_cidr_range = "10.8.0.0/28"

  depends_on = [google_project_service.vpcaccess]
}

resource "google_redis_instance" "agent" {
  count                   = var.enable_redis ? 1 : 0
  name                    = "${var.service_name}-redis"
  tier                    = var.redis_tier
  memory_size_gb          = var.redis_memory_size_gb
  region                  = var.region
  redis_version           = "REDIS_7_2"
  authorized_network      = data.google_compute_network.selected.id
  connect_mode            = "PRIVATE_SERVICE_ACCESS"
  project                 = var.project_id
  transit_encryption_mode = "DISABLED"

  depends_on = [google_project_service.redis, google_service_networking_connection.private_service_access]
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

    dynamic "vpc_access" {
      for_each = var.enable_redis ? [1] : []
      content {
        connector = google_vpc_access_connector.agent[0].id
        egress    = "PRIVATE_RANGES_ONLY"
      }
    }

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
        value = var.model_provider
      }

      env {
        name  = "MODEL"
        value = var.model
      }

      dynamic "env" {
        for_each = var.enable_redis ? [1] : []
        content {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.agent[0].host}:6379/0"
        }
      }

      env {
        name = var.model_provider == "claude" ? "ANTHROPIC_API_KEY" : var.model_provider == "gemini" ? "GEMINI_API_KEY" : "OPENAI_COMPATIBLE_API_KEY"
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
    google_project_service.redis,
    google_project_service.vpcaccess,
  ]
}
