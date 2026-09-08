#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

image="harbor.student-service.internal/student-service/frontend:$1"
deployment="apps/student-service/frontend/deployment.yaml"
image_query='.spec.template.spec.containers[] | select(.name == "frontend").image'

current_image="$(yq -er "$image_query" "$deployment")"
if [[ "$current_image" == "$image" ]]; then
	exit 0
fi

export IMAGE="$image"
yq -i "($image_query) = strenv(IMAGE)" "$deployment"

updated_image="$(yq -er "$image_query" "$deployment")"

if [[ "$updated_image" != "$image" ]]; then
	echo "Frontend image was not updated." >&2
	exit 1
fi

git diff --check -- "$deployment"
