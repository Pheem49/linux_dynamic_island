#!/usr/bin/env bash
# Quick test runner for Dynamic Island
cd "$(dirname "$0")" || exit 1
python3 tests/test_features.py "$@"
