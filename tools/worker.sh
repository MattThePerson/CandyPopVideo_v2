#!/usr/bin/env bash
set -e
go run -C go_backend ./cmd/worker "$@"
