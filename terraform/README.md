# Terraform: local kind cluster

Provisions the local Kubernetes cluster (via [kind](https://kind.sigs.k8s.io/))
that the manifests in [`../k8s`](../k8s) and [`../argocd`](../argocd) deploy onto.

## Usage

```bash
cd terraform
terraform init
terraform apply
```

This creates a single-node kind cluster named `monitoring-system` (see
`variables.tf` to override the name or pinned node image) and switches your
kubeconfig context to it, same as running `kind create cluster` by hand.

From there, deploy the stack either manually:

```bash
kubectl apply -f ../k8s/namespace.yaml
kubectl apply -f ../k8s/exporter/ -f ../k8s/prometheus/ -f ../k8s/grafana/
```

or via GitOps by installing ArgoCD and applying `../argocd/application.yaml`
(see the root [README](../README.md) for the full flow).

## Teardown

```bash
terraform destroy
```

## Why a Terraform provider instead of a shell script

The [`tehcyx/kind`](https://registry.terraform.io/providers/tehcyx/kind) provider
manages the cluster as a real Terraform resource (`kind_cluster`) with proper
plan/apply/destroy semantics and state tracking, instead of shelling out to the
`kind` CLI from a `local-exec` provisioner.
