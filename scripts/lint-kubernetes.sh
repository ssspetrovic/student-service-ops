#!/usr/bin/env bash
set -euo pipefail

# First pass focuses on built-in Kubernetes resource validation.
# CRDs from Flux, Cilium, cert-manager, and Gateway API are skipped when
# kubeconform cannot resolve matching schemas.
mapfile -d '' files < <(
  find clusters infra apps \
    -type f \
    \( -name '*.yaml' -o -name '*.yml' \) \
    ! -name 'kustomization.yaml' \
    ! -name '*.sops.yaml' \
    -print0
)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No Kubernetes manifest files found."
  exit 0
fi

kubeconform \
  -strict \
  -ignore-missing-schemas \
  -kubernetes-version 1.35.3 \
  -summary \
  "${files[@]}"
