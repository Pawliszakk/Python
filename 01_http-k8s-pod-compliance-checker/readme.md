# Kube Compliance Checker

A CLI tool for auditing Kubernetes Pods against security and resource standards — a learning project focused on Python for SRE use cases.

## Goal

Scan running Pods from the command line and report every compliance deviation, in a way that's genuinely useful when reviewing a cluster's security and resource posture.

The goal is **not** to invent arbitrary rules. Checks are anchored in existing sources of truth (Kubernetes Pod Security Standards, resource requests/limits semantics, runtime facts), so results are defensible rather than opinionated. Conceptually it's *"OpenSCAP for Kubernetes Pods"*.

## Examples

```bash
# Scan a single namespace
python main.py -n gitea

# Scan the whole cluster
python main.py

# Only the things that need attention today
python main.py --high

# HIGH and MEDIUM together — severity filters are additive
python main.py --high --medium

# Machine-readable output for piping into jq
python main.py -n gitea -o json | jq '.[] | select(.rule_id == "RES-005")'

# YAML, when you want to eyeball nested observed/expected values
python main.py -n gitea -o yaml

# Export everything to a spreadsheet
python main.py -o csv --csv-path findings.csv

# Count violations by rule across the cluster
python main.py -o json | jq -r '.[].rule_id' | sort | uniq -c | sort -rn
```

## Implemented Rules

Severity legend: 🟢 OK · ℹ️ INFO · 🔵 LOW · 🟡 MEDIUM · 🔴 HIGH

### PSS-Baseline — Pod Security Standards

| Rule ID | Severity | Bad state |
|---|---|---|
| `PSS-B-001` | 🔴 HIGH | `privileged: true` |
| `PSS-B-002` | 🔴 HIGH | `hostNetwork` / `hostPID` / `hostIPC` enabled |
| `PSS-B-003` | 🔴 HIGH | `capabilities.add` outside the Baseline allowed set |
| `PSS-B-004` | 🔴 HIGH | `hostPath` volume mounted |

### PSS-Restricted — Pod Security Standards

| Rule ID | Severity | Bad state |
|---|---|---|
| `PSS-R-001` | 🟡 MEDIUM | `runAsNonRoot` not `true` |
| `PSS-R-002` | 🟡 MEDIUM | `allowPrivilegeEscalation` not `false` |
| `PSS-R-003` | 🟡 MEDIUM | `capabilities.drop` missing `ALL` |
| `PSS-R-004` | 🟡 MEDIUM | seccomp profile not `RuntimeDefault` (`Localhost` accepted) |

`PSS-R-001` and `PSS-R-004` resolve the effective value — container-level `securityContext` overrides the Pod-level one. `PSS-R-002` and `PSS-R-003` are container-level only, since those fields do not exist in `PodSecurityContext`.

### Resources

| Rule ID | Severity | Bad state |
|---|---|---|
| `RES-001` | 🔴 HIGH | `requests.cpu` missing |
| `RES-002` | 🔴 HIGH | `requests.memory` missing |
| `RES-003` | 🟡 MEDIUM | `limits.memory` missing |
| `RES-004` | 🔵 LOW | `limits.cpu` missing |
| `RES-005` | 🔴 HIGH | both requests and limits missing |
| `RES-006` | 🔴 HIGH | requests block missing |
| `RES-007` | 🔴 HIGH | limits block missing |

Rules are mutually exclusive by construction: `RES-005` short-circuits the rest, `RES-006`/`RES-007` fire only when the whole block is absent, and `RES-001`–`RES-004` fire only when the block exists but a field is missing.

### Runtime

| Rule ID | Severity | Bad state |
|---|---|---|
| `RT-001` | 🔴 HIGH | `lastState.terminated.reason == OOMKilled` |
| `RT-002` | ℹ️ INFO | current usage vs configured limits (snapshot) |

`RT-002` is skipped for Pods whose `status.phase` is not `Running` — completed Job/CronJob Pods have no metrics and would otherwise produce 404s.

## Finding Structure

Every deviation is a structured record:

| Field | Description |
|---|---|
| `namespace` | Pod namespace |
| `pod` | Pod name |
| `container` | Container name (empty for pod-level checks) |
| `standard` | `PSS-Baseline`, `PSS-Restricted`, `Resources`, `Runtime` |
| `rule_id` | Stable rule identifier |
| `severity` | `OK` / `INFO` / `LOW` / `MEDIUM` / `HIGH` |
| `observed` | Actual value found in the cluster |
| `expected` | Compliant value |
| `message` | Human-readable description |

## Architecture Notes

- **Metrics come from a different API group.** `CoreV1Api` serves `v1` (core) objects — Pod spec and status — but carries no live resource usage. Usage is served by `metrics.k8s.io/v1beta1`, provided by metrics-server via the API aggregation layer, and reached through `CustomObjectsApi`. This is the same endpoint `kubectl top pods` hits.
- **`last_state` vs `state`.** `state` is the container's current state; `last_state` holds the previous termination and is only populated after a restart. `RT-001` reads `last_state` so an OOMKill is still caught after the container has come back up.
- **Checks are pure functions.** Each `check_*` function takes a Pod and appends to a shared `findings` list. Adding a rule means adding a function and one call in `main.py`.