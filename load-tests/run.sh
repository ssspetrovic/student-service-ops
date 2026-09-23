#!/usr/bin/env bash
set -euo pipefail

workload="${1:?Usage: $0 frontend|backend|write}"

results_dir="${LOAD_TEST_RESULTS_DIR:-load-results}"
mkdir -p "$results_dir"

results_file="$results_dir/summary.csv"

summary_file="$(mktemp "$results_dir/.summary.XXXXXX.json")"
trap 'rm -f "$summary_file"' EXIT

k6_status=0
k6 run \
	--summary-export "$summary_file" \
	-e LOAD_TEST_WORKLOAD="$workload" \
	load-tests/load.js || k6_status=$?

if [[ ! -s "$summary_file" ]]; then
	echo "k6 did not produce a summary" >&2
	exit 1
fi

if [[ ! -f "$results_file" ]]; then
	printf '%s\n' \
		'timestamp,workload,vus,requests,requests_per_second,failed_percent,average_ms,p95_ms,checks_passed_percent,threshold_result' \
		>"$results_file"
fi

result="PASS"
if ((k6_status != 0)); then
	result="FAIL"
fi

protocol_vus="${LOAD_TEST_VUS:-10}"
if [[ "$workload" == "write" ]]; then
	protocol_vus=1
fi

jq -r \
	--arg timestamp "$(date --iso-8601=seconds)" \
	--arg workload "$workload" \
	--arg vus "$protocol_vus" \
	--arg result "$result" \
	'
    def round2: (. * 100 | round) / 100;
    [
      $timestamp,
      $workload,
      ($vus | tonumber),
      .metrics.http_reqs.count,
      (.metrics.http_reqs.rate | round2),
      (.metrics.http_req_failed.value * 100 | round2),
      (.metrics.http_req_duration.avg | round2),
      (.metrics.http_req_duration["p(95)"] | round2),
      (.metrics.checks.value * 100 | round2),
      $result
    ] | @csv
  ' "$summary_file" >>"$results_file"

echo "Saved result to $results_file"

exit "$k6_status"
