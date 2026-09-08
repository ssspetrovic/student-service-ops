#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

image="harbor.student-service.internal/student-service/backend:$1"
job="apps/student-service/backend/bootstrap/job.yaml"
deployment="apps/student-service/backend/deployment.yaml"
job_image_query='.spec.template.spec.containers[] | select(.name == "migrations").image'
deployment_image_query='.spec.template.spec.containers[] | select(.name == "backend").image'

job_image="$(yq -er "$job_image_query" "$job")"
deployment_image="$(yq -er "$deployment_image_query" "$deployment")"

if [[ "$job_image" != "$deployment_image" ]]; then
	echo "Migration and backend image pins are not the same" >&2
	exit 1
fi

if [[ "$job_image" == "$image" ]]; then
	exit 0
fi

export IMAGE="$image"
yq -i "($job_image_query) = strenv(IMAGE)" "$job"
yq -i "($deployment_image_query) = strenv(IMAGE)" "$deployment"

updated_job_image="$(yq -er "$job_image_query" "$job")"
updated_deployment_image="$(yq -er "$deployment_image_query" "$deployment")"

if [[ "$updated_job_image" != "$image" || "$updated_deployment_image" != "$image" ]]; then
	echo "Backend images were not updated." >&2
	exit 1
fi

git diff --check -- "$job" "$deployment"
