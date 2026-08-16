#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
	echo "Usage: $0 <image-tag>" >&2
	exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.."

image="harbor.student-service.internal/student-service/frontend:$1"
deployment="apps/student-service/frontend/deployment.yaml"

current_image="$(yq -er '.spec.template.spec.containers[] | select(.name == "frontend") | .image' "$deployment")"
if [[ "$current_image" == "$image" ]]; then
	exit 0
fi

IMAGE="$image" yq -i \
	'(.spec.template.spec.containers[] | select(.name == "frontend").image) = strenv(IMAGE)' \
	"$deployment"

[[ "$(yq -er '.spec.template.spec.containers[] | select(.name == "frontend") | .image' "$deployment")" == "$image" ]]
git diff --check -- "$deployment"
