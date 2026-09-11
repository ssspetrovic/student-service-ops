#!/usr/bin/env bash
set -euo pipefail

script_dir="$(dirname "$0")"
repo_root="$(cd "$script_dir/.." && pwd)"
temp_root="$(mktemp -d)"

cleanup() {
	rm -rf "$temp_root"
}
trap cleanup EXIT

# backend check

backend_root="$temp_root/backend"
mkdir -p "$backend_root/scripts" "$backend_root/apps/student-service/backend/bootstrap"

cp "$repo_root/scripts/update-backend-image.sh" "$backend_root/scripts/"
cp "$repo_root/apps/student-service/backend/bootstrap/job.yaml" "$backend_root/apps/student-service/backend/bootstrap/job.yaml"
cp "$repo_root/apps/student-service/backend/deployment.yaml" "$backend_root/apps/student-service/backend/deployment.yaml"

git -C "$backend_root" init --quiet
git -C "$backend_root" add .

backend_tag="ci-validation-backend"
backend_image="harbor.student-service.internal/student-service/backend:$backend_tag"

pushd "$backend_root"
./scripts/update-backend-image.sh "$backend_tag"
popd

backend_job_image="$(yq -er '.spec.template.spec.containers[] | select(.name == "migrations").image' \
	"$backend_root/apps/student-service/backend/bootstrap/job.yaml")"
backend_deployment_image="$(yq -er '.spec.template.spec.containers[] | select(.name == "backend").image' \
	"$backend_root/apps/student-service/backend/deployment.yaml")"

if [[ "$backend_job_image" != "$backend_image" ]]; then
	echo "Backend job image was not updated as expected" >&2
	exit 1
fi

if [[ "$backend_deployment_image" != "$backend_image" ]]; then
	echo "Backend deployment image was not updated as expected" >&2
	exit 1
fi

# frontend chgeck

frontend_root="$temp_root/frontend"
mkdir -p "$frontend_root/scripts" "$frontend_root/apps/student-service/frontend"

cp "$repo_root/scripts/update-frontend-image.sh" "$frontend_root/scripts/"
cp "$repo_root/apps/student-service/frontend/deployment.yaml" "$frontend_root/apps/student-service/frontend/deployment.yaml"

git -C "$frontend_root" init --quiet
git -C "$frontend_root" add .

frontend_tag="ci-validation-frontend"
frontend_image="harbor.student-service.internal/student-service/frontend:$frontend_tag"

pushd "$frontend_root"
./scripts/update-frontend-image.sh "$frontend_tag"
popd

frontend_deployment_image="$(yq -er '.spec.template.spec.containers[] | select(.name == "frontend").image' \
	"$frontend_root/apps/student-service/frontend/deployment.yaml")"

if [[ "$frontend_deployment_image" != "$frontend_image" ]]; then
	echo "Frontend deployment image was not updated as expected" >&2
	exit 1
fi

echo "Image promotion scripts passed isolated validation."
