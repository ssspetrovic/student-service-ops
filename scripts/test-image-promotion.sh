#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
temp_root="$(mktemp -d)"

cleanup() {
	rm -rf -- "$temp_root"
}
trap cleanup EXIT

prepare_repo() {
	local target="$1"
	shift

	local path
	for path in "$@"; do
		mkdir -p -- "$target/$(dirname -- "$path")"
		cp -- "$repo_root/$path" "$target/$path"
	done

	git -C "$target" init --quiet
	git -C "$target" add .
}

read_image() {
	local root="$1"
	local manifest="$2"
	local container="$3"

	CONTAINER="$container" yq -er \
		'.spec.template.spec.containers[] | select(.name == strenv(CONTAINER)) | .image' \
		"$root/$manifest"
}

backend_root="$temp_root/backend"
prepare_repo "$backend_root" \
	scripts/update-backend-image.sh \
	apps/student-service/backend/bootstrap/job.yaml \
	apps/student-service/backend/deployment.yaml

backend_tag="ci-validation-backend"
backend_image="harbor.student-service.internal/student-service/backend:$backend_tag"
(
	cd "$backend_root"
	./scripts/update-backend-image.sh "$backend_tag"
)

[[ "$(read_image "$backend_root" apps/student-service/backend/deployment.yaml backend)" == "$backend_image" ]]
[[ "$(read_image "$backend_root" apps/student-service/backend/bootstrap/job.yaml migrations)" == "$backend_image" ]]

frontend_root="$temp_root/frontend"
prepare_repo "$frontend_root" \
	scripts/update-frontend-image.sh \
	apps/student-service/frontend/deployment.yaml

frontend_tag="ci-validation-frontend"
frontend_image="harbor.student-service.internal/student-service/frontend:$frontend_tag"
(
	cd "$frontend_root"
	./scripts/update-frontend-image.sh "$frontend_tag"
)
[[ "$(read_image "$frontend_root" apps/student-service/frontend/deployment.yaml frontend)" == "$frontend_image" ]]

echo "Image promotion scripts passed isolated validation."
