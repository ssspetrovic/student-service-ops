#!/usr/bin/env bash
set -euo pipefail

# Validate built-in Kubernetes resources with kubeconform's default schema
# catalog, then try Datree's CRD catalog for common operator resources.
search_dirs=()
for dir in clusters infra apps; do
	if [[ -d "${dir}" ]]; then
		search_dirs+=("${dir}")
	fi
done

if [[ ${#search_dirs[@]} -eq 0 ]]; then
	echo "No Kubernetes manifest directories found."
	exit 0
fi

mapfile -d '' files < <(
	find "${search_dirs[@]}" \
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
	-schema-location "https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json" \
	-schema-location default \
	-summary \
	"${files[@]}"
