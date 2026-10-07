# SRE Log Parser CLI

A CLI tool for analyzing Traefik HTTP access logs — a learning project focused on Python for SRE use cases.

## Goal

Parse and analyze Traefik access logs from the command line, in a way that's genuinely useful when debugging production incidents.

## Input

- ✅ Traefik JSON access logs (`--accesslog.format=json`) pulled live from a production RKE2 cluster via the Kubernetes API.
- ✅ File input also supported (`--from-file`) for offline analysis of saved logs.

## Features

### 1. Parsing
Parses each log line into a structured record containing:
- ✅ client IP (`ClientHost`)
- ✅ timestamp (`time`, ISO8601 UTC)
- ✅ HTTP method (`RequestMethod`)
- ✅ path (`RequestPath`)
- ✅ status code (`DownstreamStatus`)
- ✅ response size (`DownstreamContentSize`)
- ✅ duration (`Duration`, in **microseconds** — converted before computing percentiles)
- ✅ service name (`ServiceName`) — useful for aggregating by application (e.g. Nextcloud, JumpServer)

### 2. Filtering
- ✅ by HTTP status (`--status`)
- ✅ by IP address (`--ip`)
- ✅ by path (`--path`) — exact match only, not substring/regex
- ✅ by host (`--host`)
- ✅ by time range (`--since` / `--until`)
- ✅ by minimum duration (`--slower-than`, in seconds)
- ✅ exclusion filters for noisy traffic (Rancher live-log streaming, `follow=true`, unreasonably long durations)

### 3. Statistics / aggregations
- ✅ top N IP addresses by request count
- ✅ request count per status code
- ✅ top N most requested endpoints
- ✅ top N 5xx error codes
- ✅ response time stats: average, median, p50/p95/p99
- ✅ slowest hosts, ranked by average response time

### 4. Error handling
- ✅ lines that don't match the expected pattern don't crash the program
- ✅ a summary report at the end shows how many lines failed to parse
- ✅ graceful "no data matched filters" message instead of crashing on empty result sets

### 5. Output
- ✅ readable terminal output via `show_top_metrics`, aligned columns
- ✅ CSV export for all metrics (`--output-dir`) — top IPs, status codes, error codes, request paths, request addresses, stats, slowest hosts, error logs, per-IP logs

### 6. CLI
- ✅ `argparse`-based CLI, with filter flags, `--show-all` convenience flag, `--results-number` for top-N size, and usage examples in `--help`

## Success criteria

Feeding the tool a real production access log produces a report that would genuinely help during incident debugging/analysis.

# Usage

Run `python main.py --help` for the full, up-to-date list of flags.

## Examples

```bash
# Show everything, pulling live from the cluster
python main.py --show-all

# Show top 20 IPs instead of default 10
python main.py --show-top-ips --results-number 20

# Analyze a saved log file instead of live cluster
python main.py --from-file access.log --show-stats

# Filter to a specific status code and print matching logs
python main.py --status 500 --show-error-logs

# Pull more lines and check top requested paths
python main.py --lines 5000 --show-top-request-paths

# Check stats for a specific IP address
python main.py --ip 192.168.0.63 --show-top-ips

# Custom namespace/labels when pulling from a different cluster setup
python main.py --namespace default --labels app=my-ingress --show-all

# Show requests slower than 10 seconds
python main.py --slower-than 10

# Show slowest hosts, ranked by average response time
python main.py --show-slowest

# Filter by a time window (from a saved log file)
python main.py --from-file access.log --since "2026-07-14 07:00" --until "2026-07-14 12:00" --show-top-request-addr

# Export all results to CSV instead of printing to terminal
python main.py --show-all --output-dir ./results

# Show requests slower than 10 seconds, with path shown
python main.py --slower-than 10 --slower-than-show-path

# Narrow down to a specific host and check its error logs
python main.py --host helpdesk-k8s.mw-wheels.com --show-error-logs

# Combine IP and status filters to trace a specific incident
python main.py --ip 192.168.0.52 --status 500 --show-error-logs

# Check top error codes (4xx/5xx) with a bigger sample size
python main.py --lines 20000 --show-top-error-codes
```