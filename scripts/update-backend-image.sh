#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
	echo "Usage: $0 <image-tag>" >&2
	exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.."

image="harbor.student-service.internal/student-service/backend:$1"
job="apps/student-service/migrations/job.yaml"
deployment="apps/student-service/backend/deployment.yaml"

read_image() {
	local manifest="$1"
	local container="$2"

	CONTAINER="$container" yq -er \
		'.spec.template.spec.containers[] | select(.name == strenv(CONTAINER)) | .image' \
		"$manifest"
}

if [[ "$(read_image "$job" migrations)" != "$(read_image "$deployment" backend)" ]]; then
	echo "Migration and backend image pins differ; resolve the drift before promotion." >&2
	exit 1
fi

if [[ "$(read_image "$job" migrations)" == "$image" ]]; then
	exit 0
fi

temp_dir="$(mktemp -d)"
restore=false

cleanup() {
	if [[ "$restore" == true ]]; then
		cp "$temp_dir/job.original.yaml" "$job"
		cp "$temp_dir/deployment.original.yaml" "$deployment"
	fi
	rm -rf "$temp_dir"
}
trap cleanup EXIT

cp "$job" "$temp_dir/job.original.yaml"
cp "$deployment" "$temp_dir/deployment.original.yaml"
cp "$job" "$temp_dir/job.updated.yaml"
cp "$deployment" "$temp_dir/deployment.updated.yaml"

IMAGE="$image" CONTAINER=migrations yq -i \
	'(.spec.template.spec.containers[] | select(.name == strenv(CONTAINER)).image) = strenv(IMAGE)' \
	"$temp_dir/job.updated.yaml"
IMAGE="$image" CONTAINER=backend yq -i \
	'(.spec.template.spec.containers[] | select(.name == strenv(CONTAINER)).image) = strenv(IMAGE)' \
	"$temp_dir/deployment.updated.yaml"

[[ "$(read_image "$temp_dir/job.updated.yaml" migrations)" == "$image" ]]
[[ "$(read_image "$temp_dir/deployment.updated.yaml" backend)" == "$image" ]]

restore=true
cp "$temp_dir/job.updated.yaml" "$job"
cp "$temp_dir/deployment.updated.yaml" "$deployment"

[[ "$(read_image "$job" migrations)" == "$image" ]]
[[ "$(read_image "$deployment" backend)" == "$image" ]]
git diff --check -- "$job" "$deployment"
restore=false
