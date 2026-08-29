#!/usr/bin/env bash
set -euo pipefail

fix_mode=false

if [[ "${1:-}" == "--fix" ]]; then
	fix_mode=true
fi

files=()
while IFS= read -r -d '' file; do
	files+=("$file")
done < <(
	find . \
		-type f \
		-name '*.sh' \
		! -path './.git/*' \
		! -path './.agents/*' \
		! -path './.codex/*' \
		-print0
)

if [[ ${#files[@]} -eq 0 ]]; then
	echo "No shell scripts found."
	exit 0
fi

if [[ "$fix_mode" == "true" ]]; then
	shfmt -w "${files[@]}"
else
	shellcheck "${files[@]}"
fi
