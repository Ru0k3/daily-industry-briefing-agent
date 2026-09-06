output "cloud_run_service_name" {
  value       = google_cloud_run_v2_service.agent.name
  description = "Cloud Run service name."
}

output "cloud_run_uri" {
  value       = google_cloud_run_v2_service.agent.uri
  description = "Cloud Run service URI."
}

output "runtime_service_account" {
  value       = google_service_account.runtime.email
  description = "Runtime service account email."
}

output "secret_id" {
  value       = google_secret_manager_secret.provider_key.secret_id
  description = "Secret Manager secret ID."
}
