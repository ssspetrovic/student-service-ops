#!/usr/bin/env bash
set -euo pipefail

fix_arg="${1:-}"

fix_mode=false

if [[ "$fix_arg" == "--fix" ]]; then
	fix_mode=true
fi

if [[ "$fix_mode" == "true" ]]; then
	find . -type f -name '*.sh' \
		! -path './.git/*' \
		! -path './.agents/*' \
		! -path './.codex/*' \
		-exec shfmt -w {} +
else
	find . -type f -name '*.sh' \
		! -path './.git/*' \
		! -path './.agents/*' \
		! -path './.codex/*' \
		-exec shellcheck {} +
fi
