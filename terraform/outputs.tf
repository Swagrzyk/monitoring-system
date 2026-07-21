output "cluster_name" {
  description = "Name of the provisioned kind cluster (also the kubeconfig context name)."
  value       = kind_cluster.this.name
}

output "kubeconfig_path" {
  description = "Path to the kubeconfig file written by the kind provider."
  value       = kind_cluster.this.kubeconfig_path
}

output "endpoint" {
  description = "Kubernetes API server endpoint."
  value       = kind_cluster.this.endpoint
}

output "kubeconfig" {
  description = "Full kubeconfig content, in case you need it outside of kubeconfig_path."
  value       = kind_cluster.this.kubeconfig
  sensitive   = true
}
