variable "cluster_name" {
  description = "Name of the local kind cluster."
  type        = string
  default     = "monitoring-system"
}

variable "node_image" {
  description = "kind node image, pins the Kubernetes version of the cluster."
  type        = string
  default     = "kindest/node:v1.36.1"
}
