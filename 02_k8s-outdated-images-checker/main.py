import hashlib
import re
import subprocess
import json

from connect_to_k8s import connect_to_k8s
from get_args import get_args
from models import Entry
from packaging.version import Version, InvalidVersion

_LEADING_VERSION_RE = re.compile(r"^(?P<version>\d+(?:\.\d+)*)(?P<suffix>[-+_.].*)?$")


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"


def parse_tag(tag: str) -> tuple[Version, str] | None:
    """Parse a tag into (version, variant_suffix).

    Standard PEP 440-ish tags (semver, rc/alpha/beta, +build metadata) parse
    directly and keep their prerelease/local-version semantics. Tags with a
    non-standard trailing variant marker (e.g. "4.11-ce", "1.2.3-alpine")
    fall back to parsing just the leading numeric version, keeping the
    marker as an opaque suffix so it never gets compared against a
    differently-suffixed (or unsuffixed) tag.
    """
    stripped = tag.lstrip("v")

    try:
        return Version(stripped), ""
    except InvalidVersion:
        pass

    match = _LEADING_VERSION_RE.match(stripped)
    if not match:
        return None

    try:
        version = Version(match.group("version"))
    except InvalidVersion:
        return None

    return version, (match.group("suffix") or "")


def get_latest_tag(
    tags: list[str],
    current_suffix: str = "",
    include_prerelease: bool = False,
) -> str | None:
    parsed = []
    for tag in tags:
        result = parse_tag(tag)
        if result is None:
            continue

        version, suffix = result
        if suffix != current_suffix:
            continue

        if version.is_prerelease and not include_prerelease:
            continue

        parsed.append((version, tag))

    if not parsed:
        return None

    return max(parsed, key=lambda x: x[0])[1]


def parse_image_ref(image: str) -> tuple[str, str | None, str | None]:
    """Split an image reference into (repository, tag, digest).

    Handles registries with an explicit port (e.g. "host:5000/repo:tag")
    by only treating a colon after the last "/" as a tag separator.
    """
    digest = None
    if "@" in image:
        image, digest = image.split("@", 1)

    tag = None
    last_slash = image.rfind("/")
    last_colon = image.rfind(":")
    if last_colon > last_slash:
        image, tag = image.rsplit(":", 1)

    return image, tag, digest


def get_digest(image_ref: str) -> str | None:
    # --raw avoids skopeo resolving a single-platform instance out of a
    # manifest list based on the *local* host's OS/arch (e.g. it would try
    # to find a "darwin" image when run from a Mac to check a Linux-only
    # cluster image, and fail). Hashing the raw manifest bytes gives the
    # same content digest a registry reports and Kubernetes resolves
    # image:tag to, independent of what platform we're running on.
    command = ["skopeo", "inspect", "--raw", f"docker://{image_ref}"]
    result = subprocess.run(command, capture_output=True)

    if result.returncode != 0:
        print(colorize(f"WARN | Failed to inspect {image_ref}: {result.stderr.decode().strip()}", Color.RED))
        return None

    return f"sha256:{hashlib.sha256(result.stdout).hexdigest()}"


def get_tags(repository: str) -> list[str]:
    command = ["skopeo", "list-tags", f"docker://{repository}"]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(colorize(f"WARN | Failed to list tags for {repository}: {result.stderr.strip()}", Color.RED))
        return []

    data = json.loads(result.stdout)
    return data.get("Tags", [])


def list_pods(v1, namespace: str | None):
    if namespace:
        return v1.list_namespaced_pod(namespace).items
    return v1.list_pod_for_all_namespaces().items


def collect_container_images(v1, namespace: str | None = None) -> list[Entry]:
    container_images: list[Entry] = []

    for pod in list_pods(v1, namespace):
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace

        for container in pod.spec.containers:
            if "rancher" in container.image:
                continue

            if any(entry.image == container.image for entry in container_images):
                continue

            container_images.append(Entry(
                pod=pod_name,
                namespace=pod_namespace,
                container=container.name,
                image=container.image
            ))

    return container_images


def check_image(entry: Entry) -> None:
    print(f"Processing {entry.image}, searching for newest container...")

    repository, tag, digest = parse_image_ref(entry.image)

    current_suffix = ""
    if tag is not None:
        parsed_tag = parse_tag(tag)
        if parsed_tag is not None:
            current_suffix = parsed_tag[1]

    latest_tag = get_latest_tag(get_tags(repository), current_suffix=current_suffix)
    if latest_tag is None:
        print(colorize(f"WARN | Could not determine a comparable latest tag for {entry.image}", Color.RED))
        entry.status = "warn"
        return

    latest_image_ref = f"{repository}:{latest_tag}"

    current_digest = digest if digest is not None else get_digest(entry.image)
    latest_digest = get_digest(latest_image_ref)

    entry.image_latest = latest_image_ref

    if current_digest is None or latest_digest is None:
        print(colorize(f"WARN | Could not resolve digest for {entry.image}, skipping comparison", Color.RED))
        entry.status = "warn"
        return

    if current_digest == latest_digest:
        print(colorize(f"OK | {entry.image} is already latest image.", Color.GREEN))
        entry.status = "ok"
    else:
        print(colorize(f"INFO | Found newest version of {entry.image} -> {latest_image_ref}", Color.YELLOW))
        entry.status = "outdated"


def print_report(container_images: list[Entry]) -> None:
    outdated = [entry for entry in container_images if entry.status == "outdated"]

    print()
    print(colorize("Report", Color.BOLD))

    if not outdated:
        print(colorize("All container images are up to date.", Color.GREEN))
        return

    for entry in outdated:
        message = (
            f"Container {entry.image} in namespace {entry.namespace} "
            f"in pod {entry.pod} can be replaced with {entry.image_latest}"
        )
        print(colorize(message, Color.YELLOW))


def print_report_simple(container_images: list[Entry]) -> None:
    outdated = [entry for entry in container_images if entry.status == "outdated"]

    print()
    print(colorize("Report (simple)", Color.BOLD))

    if not outdated:
        print(colorize("All container images are up to date.", Color.GREEN))
        return

    for entry in outdated:
        print(colorize(f"{entry.image} -> {entry.image_latest}", Color.YELLOW))


def main():
    args = get_args()

    v1 = connect_to_k8s()

    container_images = collect_container_images(v1, namespace=args.namespace)

    for entry in container_images:
        check_image(entry)

    print_report(container_images)
    print_report_simple(container_images)


if __name__ == "__main__":
    main()
