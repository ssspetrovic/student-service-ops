#!/usr/bin/env bash
set -euo pipefail

search_dirs=()
for dir in clusters infra apps; do
	[[ -d "$dir" ]] && search_dirs+=("$dir")
done

if [[ ${#search_dirs[@]} -eq 0 ]]; then
	echo "No Kubernetes manifest directories found."
	exit 0
fi

find "${search_dirs[@]}" -type f \( -name '*.yaml' -o -name '*.yml' \) \
	! -name 'kustomization.yaml' \
	! -name '*.sops.yaml' \
	! -path '*/flux-system/*' \
	-exec kubeconform \
		-strict \
		-ignore-missing-schemas \
		-kubernetes-version 1.35.3 \
		-schema-location "https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json" \
		-schema-location default \
		-summary \
		{} +
