#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: $0 <40-character-git-sha>"
}

if [[ "${1:-}" == "--help" ]]; then
	usage
	exit 0
fi

if [[ $# -ne 1 ]]; then
	usage >&2
	exit 2
fi

image_tag="$1"
if [[ ! "$image_tag" =~ ^[0-9a-f]{40}$ ]]; then
	echo "Backend image tag must be a lowercase 40-character Git SHA." >&2
	exit 2
fi

if ! command -v yq >/dev/null 2>&1; then
	echo "yq is required. Run this script through the repository's mise environment." >&2
	exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
cd "$repo_root"

image_repository="harbor.student-service.internal/student-service/backend"
target_image="${image_repository}:${image_tag}"
job_manifest="apps/student-service/migrations/job.yaml"
deployment_manifest="apps/student-service/backend/deployment.yaml"

read_image() {
	local manifest="$1"
	local container_name="$2"

	CONTAINER_NAME="$container_name" yq -er \
		'.spec.template.spec.containers[] | select(.name == strenv(CONTAINER_NAME)) | .image' \
		"$manifest"
}

job_image="$(read_image "$job_manifest" migrations)"
deployment_image="$(read_image "$deployment_manifest" backend)"

if [[ "$job_image" != "$deployment_image" ]]; then
	echo "Migration and backend image pins differ; resolve the drift before promotion." >&2
	exit 1
fi

if [[ "$job_image" == "$target_image" ]]; then
	echo "Backend manifests are already pinned to ${target_image}."
	exit 0
fi

temp_dir="$(mktemp -d)"
restore_manifests=false

cleanup() {
	if [[ "$restore_manifests" == "true" ]]; then
		cp -- "$temp_dir/job.original.yaml" "$job_manifest"
		cp -- "$temp_dir/deployment.original.yaml" "$deployment_manifest"
	fi
	rm -r -- "$temp_dir"
}
trap cleanup EXIT

cp -- "$job_manifest" "$temp_dir/job.original.yaml"
cp -- "$deployment_manifest" "$temp_dir/deployment.original.yaml"
cp -- "$job_manifest" "$temp_dir/job.updated.yaml"
cp -- "$deployment_manifest" "$temp_dir/deployment.updated.yaml"

IMAGE_REF="$target_image" CONTAINER_NAME=migrations yq -i \
	'(.spec.template.spec.containers[] | select(.name == strenv(CONTAINER_NAME)).image) = strenv(IMAGE_REF)' \
	"$temp_dir/job.updated.yaml"
IMAGE_REF="$target_image" CONTAINER_NAME=backend yq -i \
	'(.spec.template.spec.containers[] | select(.name == strenv(CONTAINER_NAME)).image) = strenv(IMAGE_REF)' \
	"$temp_dir/deployment.updated.yaml"

[[ "$(read_image "$temp_dir/job.updated.yaml" migrations)" == "$target_image" ]]
[[ "$(read_image "$temp_dir/deployment.updated.yaml" backend)" == "$target_image" ]]

restore_manifests=true
cp -- "$temp_dir/job.updated.yaml" "$job_manifest"
cp -- "$temp_dir/deployment.updated.yaml" "$deployment_manifest"

[[ "$(read_image "$job_manifest" migrations)" == "$target_image" ]]
[[ "$(read_image "$deployment_manifest" backend)" == "$target_image" ]]
git diff --check -- "$job_manifest" "$deployment_manifest"

restore_manifests=false
echo "Pinned migration and backend manifests to ${target_image}."
