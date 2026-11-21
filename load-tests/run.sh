#!/usr/bin/env bash

trap 'exit 130' INT
trap 'exit 143' TERM

results_dir="load-results/full-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p load-results || exit 1
mkdir "$results_dir" || exit 1
echo "Results folder: $results_dir"

unset K6_OUT K6_SUMMARY_EXPORT
export LOAD_TEST_PAUSE_SECONDS=1
any_failed=false

for vus in 10 100 200; do
	level_dir="$results_dir/$vus-vu"
	mkdir "$level_dir" || exit 1
	export LOAD_TEST_VUS="$vus"
	level_failed=false

	echo "$(date -u +%FT%TZ) Starting warm-up with $vus HTTP users."
	export LOAD_TEST_PHASE=warmup
	export LOAD_TEST_DURATION_SECONDS=60
	if k6 run --summary-mode=full --out "csv=$level_dir/warmup.csv" load-tests/test.js; then
		echo "Warm-up done. Waiting 60 seconds."
	else
		status=$?
		if [ "$status" -eq 99 ]; then
			echo "Warm-up did not meet the checks. It only prepares the system, so the tests continue."
		else
			echo "Warm-up stopped (code $status). Stopping tests."
			exit "$status"
		fi
	fi
	sleep 60 || exit 1

	export LOAD_TEST_PHASE=measured
	export LOAD_TEST_DURATION_SECONDS=180
	for repetition in 01 02 03; do
		echo "$(date -u +%FT%TZ) Starting test $repetition with $vus HTTP users."
		if k6 run --summary-mode=full --out "csv=$level_dir/run-$repetition.csv" load-tests/test.js; then
			echo "$(date -u +%FT%TZ) Test $repetition passed the checks."
		else
			status=$?
			if [ "$status" -eq 99 ]; then
				level_failed=true
				echo "$(date -u +%FT%TZ) Some checks failed. Finishing the tests with $vus HTTP users."
			else
				echo "Test stopped (code $status). Stopping all tests."
				exit "$status"
			fi
		fi
		if [ "$repetition" != 03 ]; then
			echo "Waiting 60 seconds."
			sleep 60 || exit 1
		fi
	done

	if [ "$level_failed" = true ]; then
		any_failed=true
		echo "Checks failed with $vus HTTP users. Continuing with the next level."
	fi
	if [ "$vus" -ne 200 ]; then
		echo "Waiting 60 seconds before adding more users."
		sleep 60 || exit 1
	fi
done

echo "$(date -u +%FT%TZ) Tests finished. Check the saved results and system health."
if [ "$any_failed" = true ]; then
	exit 99
fi
