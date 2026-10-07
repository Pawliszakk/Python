# k8s-outdated-images-checker

Scans the containers actually running in your cluster and tells you which ones are
behind the latest tag available in the registry.

## What it does

- Connects to your cluster using your local kubeconfig (same as `kubectl`).
- Walks every pod (or just one namespace) and collects the unique container images in use.
- Skips `rancher` system images automatically.
- For each image, asks the registry (via `skopeo`) for all available tags and figures out
  the newest one — matching `1.2.3`, `v1.2.3`, and variant-suffixed tags like `1.25-alpine`
  or `16.11.0-ce.0` correctly (it won't compare a `-ce` image against an `-ee` or plain tag).
- Compares the **image digest** you're running against the digest of the newest tag — not
  just the tag string — so it still catches drift even if a tag like `latest` or `stable`
  got silently re-pushed.
- Prints a clear status per image so you can scan the output at a glance.

## Requirements

- Python 3.10+
- [`skopeo`](https://github.com/containers/skopeo) installed and on your `PATH`
- `pip install kubernetes packaging`
- A working kubeconfig (`~/.kube/config` or `$KUBECONFIG`) pointing at your cluster

## Usage

Check every namespace in the cluster:

```bash
python main.py
```

Check just one namespace:

```bash
python main.py -n production
# or
python main.py --namespace production
```

## Example output

```text
$ python main.py -n monitoring
Processing prom/prometheus:v2.48.0, searching for newest container...
INFO | Found newest version of prom/prometheus:v2.48.0 -> prom/prometheus:v2.53.1
Processing grafana/grafana:10.2.0, searching for newest container...
OK | grafana/grafana:10.2.0 is already latest image.
Processing gitlab/gitlab-ce:16.9.0-ce.0, searching for newest container...
INFO | Found newest version of gitlab/gitlab-ce:16.9.0-ce.0 -> gitlab/gitlab-ce:16.11.0-ce.0
Processing myregistry:5000/internal/tool:1.4.2, searching for newest container...
WARN | Could not resolve digest for myregistry:5000/internal/tool:1.4.2, skipping comparison


Each line tells you exactly what happened:

| Prefix | Meaning |
|---|---|
| `OK`   | Image is already on the latest available tag/digest. |
| `INFO` | A newer image is available — the message shows exactly what to bump to. |
| `WARN` | Couldn't compare (registry unreachable, no comparable tag, or digest lookup failed) — nothing is assumed either way. |

## A few things it handles for you

- **Registries with a port**, e.g. `myregistry:5000/team/app:1.2.3` — parsed correctly instead
  of confusing the port for a tag.
- **Pinned-by-digest images**, e.g. `nginx@sha256:abcd...` — compared directly by digest
  instead of trying to guess a tag.
- **Pre-release tags** (`2.10.0-rc1`, `2.10.0-alpha`) are ignored when picking "latest" unless
  they're what you're currently running.
- **Variant suffixes** (`-ce`, `-ee`, `-alpine`, etc.) are treated as a distinct track, so you
  only ever get suggested an upgrade within the same variant you're already using.
