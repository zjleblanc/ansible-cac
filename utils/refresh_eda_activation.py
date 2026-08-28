#!/usr/bin/env python3
# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring
"""Refresh an EDA rulebook activation after its project has been updated.

Flow: sync project -> disable -> detach/reattach event streams -> re-enable
-> validate startup.

Usage:
    AAP_HOSTNAME=https://aap.example.com AAP_TOKEN=... \\
        ./utils/refresh_eda_activation.py "DataDog Events"

Env vars (same as the config-as-code process, see README.md):
    AAP_HOSTNAME          required  Gateway URL, with or without scheme
                                     (e.g. https://aap.example.com)
    AAP_TOKEN             required  OAuth2 bearer token
    AAP_VALIDATE_CERTS    optional  "false" to skip TLS verification
                                     (default: true)
    SYNC_TIMEOUT          optional  Max seconds to wait for project sync
                                     (default: 120)
    ACTIVATION_TIMEOUT    optional  Max seconds to wait for activation
                                     start/stop (default: 120)
    POLL_INTERVAL         optional  Seconds between status polls (default: 5)

Only the Python standard library is used -- no third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOTAL_STEPS = 10


class Color:
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    RESET = "\033[0m"


def log_step(n: int, msg: str) -> None:
    print(f"\n{Color.BLUE}[{n}/{TOTAL_STEPS}]{Color.RESET} {msg}")


def log_ok(msg: str) -> None:
    print(f"{Color.GREEN}  done: {msg}{Color.RESET}")


def log_info(msg: str) -> None:
    print(f"  {msg}")


def log_fail(msg: str) -> None:
    print(f"{Color.RED}  fail: {msg}{Color.RESET}", file=sys.stderr)


class ApiError(RuntimeError):
    """Raised when the EDA API returns a non-2xx response, or a resource
    lookup / poll / reattach step can't proceed."""


class EdaClient:
    """Minimal JSON/REST client for the EDA API (`/api/eda/v1/...`).

    Wraps `urllib.request` rather than depending on `requests`, so the script
    has no dependencies beyond the Python standard library.
    """

    def __init__(self, base_url: str, token: str, validate_certs: bool):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._ssl_context = None
        if not validate_certs:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self._ssl_context = ctx

    def _request(self, method: str, path: str, body: dict | None = None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, context=self._ssl_context) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            raise ApiError(f"API {method} {path} returned HTTP {e.code}\n{raw}") from None
        except urllib.error.URLError as e:
            raise ApiError(f"Request failed for {method} {path}: {e.reason}") from None

    def get(self, path: str):
        return self._request("GET", path)

    def post(self, path: str, body: dict | None = None):
        return self._request("POST", path, body)

    def patch(self, path: str, body: dict):
        return self._request("PATCH", path, body)


def url_encode(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def normalize_base_url(host: str) -> str:
    """Coerce AAP_HOSTNAME into a full base URL.

    The repo's README examples show AAP_HOSTNAME with a scheme (e.g.
    ``https://aap.example.com``), while the eda-parser skill's curl examples
    assume none. Accept either.
    """
    host = host.rstrip("/")
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"https://{host}"
    return host


def parse_source_mappings(text: str) -> list[dict]:
    """Normalize the activation's `source_mappings` field.

    The API stores it as a free-form string: either compact JSON or the
    block-style YAML text `yaml.dump()` produces (what the ansible.eda module
    and AAP UI typically write), e.g.:

        - event_stream_id: 12
          event_stream_name: My Event Stream
          rulebook_hash: 1e0f2202...
          source_name: My Source

    Returns a normalized list of {source_name, event_stream_name,
    event_stream_id} dicts, dropping the embedded rulebook_hash -- it is tied
    to the rulebook content at mapping time and must be recomputed against
    the freshly synced rulebook rather than reused (see `reattach_event_streams`).
    """
    text = text.strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = []
        current: dict | None = None
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue
            if line.startswith("- "):
                if current is not None:
                    data.append(current)
                current = {}
                line = line[2:]
            elif line.startswith(" ") and current is not None:
                line = line.strip()
            else:
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            if re.fullmatch(r"-?\d+", value):
                value = int(value)
            current[key] = value
        if current is not None:
            data.append(current)

    return [
        {
            "source_name": entry.get("source_name"),
            "event_stream_name": entry.get("event_stream_name"),
            "event_stream_id": entry.get("event_stream_id"),
        }
        for entry in data
    ]


def resolve_one(client: EdaClient, path: str, description: str) -> dict:
    """GET a list endpoint and return its single result, or raise ApiError
    if the count is zero or ambiguous (more than one match)."""
    resp = client.get(path)
    count = resp.get("count", 0)
    if count == 0:
        raise ApiError(f"No match for {description}")
    if count > 1:
        raise ApiError(f"Multiple ({count}) matches for {description} -- refine the search")
    return resp["results"][0]


def poll_until(
    client: EdaClient,
    path: str,
    extract,
    success: set,
    failure: set,
    timeout: int,
    poll_interval: int,
    label: str,
) -> None:
    """Poll `GET path`, applying `extract` to the response, until the
    resulting value is in `success` (returns normally) or in `failure` /
    the timeout elapses (raises ApiError)."""
    elapsed = 0
    while True:
        value = extract(client.get(path))
        if value in success:
            log_ok(f"{label} -> '{value}'")
            return
        if value in failure:
            raise ApiError(f"{label} entered failure state '{value}'")
        if elapsed >= timeout:
            raise ApiError(f"Timed out after {timeout}s waiting for {label} (last value: '{value}')")
        log_info(f"waiting for {label}... ({value}, {elapsed}s/{timeout}s)")
        time.sleep(poll_interval)
        elapsed += poll_interval


def disable_if_enabled(client: EdaClient, activation_id: int, was_enabled: bool) -> None:
    """Disable the activation if it's currently enabled.

    `is_enabled` is not toggled via PATCH -- the partial-update endpoint
    rejects any change (409 "not allowed to be updated") while the
    activation is enabled/running. Enable/disable are dedicated POST action
    endpoints instead.
    """
    if was_enabled:
        client.post(f"/api/eda/v1/activations/{activation_id}/disable/")
        log_ok("disable requested")
    else:
        log_info("already disabled, skipping")


# Statuses that mean the activation is actively transitioning and we must
# keep waiting. Everything else (stopped, error, failed, completed, ...) is
# settled -- nothing is running -- and safe to proceed from.
BUSY_ACTIVATION_STATUSES = {"starting", "running", "stopping", "pending", "unresponsive", "workers offline"}


def wait_for_stopped(client: EdaClient, activation_id: int, timeouts: dict) -> None:
    """Poll until the activation is no longer actively transitioning.

    Always polls, even if we didn't just request a disable: the
    detach/reattach PATCH that follows just needs nothing actively running,
    and an already-disabled activation could still be mid-transition (e.g.
    "stopping").

    A clean disable settles into "stopped", but a disabled activation can
    just as easily be sitting in "error" or "failed" (e.g. left over from a
    prior failed enable attempt) -- that's still safe to proceed from since
    nothing is running, so unlike other polls here we don't treat those as
    failures, only busy/transitional statuses block us.
    """
    elapsed = 0
    timeout = timeouts["activation"]
    poll_interval = timeouts["poll"]
    while True:
        status = client.get(f"/api/eda/v1/activations/{activation_id}/").get("status")
        if status not in BUSY_ACTIVATION_STATUSES:
            log_ok(f"activation settled -> '{status}'")
            return
        if elapsed >= timeout:
            raise ApiError(f"Timed out after {timeout}s waiting for activation to stop (last status: '{status}')")
        log_info(f"waiting for activation stop... ({status}, {elapsed}s/{timeout}s)")
        time.sleep(poll_interval)
        elapsed += poll_interval


def reattach_event_streams(
    client: EdaClient,
    activation_id: int,
    project_id: int,
    project_name: str,
    rulebook_name: str,
    source_mappings: str,
) -> None:
    """Rebuild and reattach the activation's event stream mappings.

    Rebuilt from scratch against the freshly synced rulebook rather than
    replaying the mapping captured before the sync: each mapping embeds a
    `rulebook_hash` tied to the rulebook content at mapping time, and the API
    rejects re-enabling with a stale hash ("Rulebook has changed since the
    sources were mapped"). Rulebook IDs are also not stable across a project
    sync (the ansible.eda module always re-resolves rulebooks by name), so
    the rulebook is re-looked-up here rather than reusing an ID captured
    before the sync.
    """
    old_mappings = parse_source_mappings(source_mappings)
    if not old_mappings:
        log_info("no event streams were mapped, nothing to reattach")
        return

    rulebook_match = resolve_one(
        client,
        f"/api/eda/v1/rulebooks/?name={url_encode(rulebook_name)}&project_id={project_id}",
        f"rulebook named '{rulebook_name}' in project '{project_name}'",
    )
    fresh_rulebook_id = rulebook_match["id"]

    sources_resp = client.get(f"/api/eda/v1/rulebooks/{fresh_rulebook_id}/sources/")
    current_sources = {s["name"]: s["rulebook_hash"] for s in sources_resp.get("results", [])}

    missing = sorted({m["source_name"] for m in old_mappings if m["source_name"] not in current_sources})
    if missing:
        log_fail(
            "Could not rebuild event stream mappings: source(s) not found in the synced "
            f"rulebook: {', '.join(missing)}. Original mapping for manual recovery:"
        )
        print(source_mappings, file=sys.stderr)
        raise ApiError("event stream reattach aborted")

    reattach_mappings = [{**m, "rulebook_hash": current_sources[m["source_name"]]} for m in old_mappings]
    try:
        client.patch(
            f"/api/eda/v1/activations/{activation_id}/",
            {"source_mappings": json.dumps(reattach_mappings, separators=(",", ":"))},
        )
    except ApiError:
        log_fail("Reattach failed. Rebuilt source_mappings for manual recovery:")
        print(json.dumps(reattach_mappings), file=sys.stderr)
        raise
    log_ok("event streams reattached")


def refresh_activation(client: EdaClient, activation_name: str, timeouts: dict) -> None:
    # 1. Resolve activation by name
    log_step(1, f"Resolving activation '{activation_name}'")
    match = resolve_one(
        client,
        f"/api/eda/v1/activations/?name={url_encode(activation_name)}",
        f"rulebook activation named '{activation_name}'",
    )
    activation_id = match["id"]
    activation = client.get(f"/api/eda/v1/activations/{activation_id}/")
    was_enabled = activation["is_enabled"]
    source_mappings = activation.get("source_mappings") or "[]"
    project_name = activation["project"]["name"]
    rulebook_name = activation["rulebook"]["name"]
    log_ok(f"found activation id={activation_id}, project='{project_name}', is_enabled={was_enabled}")

    # 2. Resolve project by name
    log_step(2, f"Resolving project '{project_name}'")
    project = resolve_one(
        client,
        f"/api/eda/v1/projects/?name={url_encode(project_name)}",
        f"project named '{project_name}'",
    )
    project_id = project["id"]
    log_ok(f"found project id={project_id}")

    # 3. Sync project
    log_step(3, "Triggering project sync")
    client.post(f"/api/eda/v1/projects/{project_id}/sync/")
    log_ok("sync triggered")

    # 4. Wait for sync to complete
    log_step(4, "Waiting for project sync to complete")
    poll_until(
        client,
        f"/api/eda/v1/projects/{project_id}/",
        lambda r: r.get("import_state"),
        success={"completed"},
        failure={"failed"},
        timeout=timeouts["sync"],
        poll_interval=timeouts["poll"],
        label="project sync",
    )

    # 5. Disable activation (only if currently enabled)
    log_step(5, "Disabling activation (if enabled)")
    disable_if_enabled(client, activation_id, was_enabled)

    # 6. Wait for activation to stop
    log_step(6, "Waiting for activation to stop")
    wait_for_stopped(client, activation_id, timeouts)

    # 7. Detach event streams
    log_step(7, "Detaching event streams")
    client.patch(f"/api/eda/v1/activations/{activation_id}/", {"source_mappings": "[]"})
    log_ok("event streams detached")

    # 8. Reattach event streams
    log_step(8, "Reattaching event streams")
    reattach_event_streams(client, activation_id, project_id, project_name, rulebook_name, source_mappings)

    # 9. Enable activation
    log_step(9, "Re-enabling activation")
    client.post(f"/api/eda/v1/activations/{activation_id}/enable/")
    log_ok("enable requested")

    # 10. Validate successful startup
    log_step(10, "Validating activation startup")
    poll_until(
        client,
        f"/api/eda/v1/activations/{activation_id}/",
        lambda r: r.get("status"),
        success={"running"},
        failure={"error", "failed"},
        timeout=timeouts["activation"],
        poll_interval=timeouts["poll"],
        label="activation startup",
    )


def validate_certs_from_env() -> bool:
    """True unless AAP_VALIDATE_CERTS is explicitly set to "false".

    The user must opt out of certificate validation; it is never off by
    default.
    """
    return os.environ.get("AAP_VALIDATE_CERTS", "true").strip().lower() != "false"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("activation_name", help="Name of the Rulebook Activation to refresh")
    args = parser.parse_args()

    aap_hostname = os.environ.get("AAP_HOSTNAME")
    aap_token = os.environ.get("AAP_TOKEN")
    if not aap_hostname:
        print("Error: environment variable AAP_HOSTNAME is required (e.g. https://aap.example.com)", file=sys.stderr)
        return 1
    if not aap_token:
        print("Error: environment variable AAP_TOKEN is required", file=sys.stderr)
        return 1

    timeouts = {
        "sync": int(os.environ.get("SYNC_TIMEOUT", "120")),
        "activation": int(os.environ.get("ACTIVATION_TIMEOUT", "120")),
        "poll": int(os.environ.get("POLL_INTERVAL", "5")),
    }

    base_url = normalize_base_url(aap_hostname)
    client = EdaClient(base_url, aap_token, validate_certs_from_env())

    print(f"Refreshing rulebook activation: {args.activation_name}")
    print(f"Gateway: {base_url}")

    try:
        refresh_activation(client, args.activation_name, timeouts)
    except ApiError as e:
        log_fail(str(e))
        return 1

    print()
    print(
        f"Refresh complete: '{args.activation_name}' is running with the latest "
        "project content and event stream bindings."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
