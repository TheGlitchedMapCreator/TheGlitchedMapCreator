"""Generate and download a textured banana model from Meshy."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import getpass
from pathlib import Path


API_BASE = "https://api.meshy.ai/openapi/v2/text-to-3d"
OUTPUT_FILE = Path(__file__).with_name("banana.glb")
PROMPT = (
    "A single realistic ripe yellow banana, gently curved, with a short dark stem, "
    "subtle natural brown speckles, smooth edible peel, whole fruit with no props; "
    "centered clean silhouette, detailed high-quality 3D model"
)


def read_key() -> str:
    key = os.environ.get("MESHY_API_KEY", "").strip()
    if not key:
        key = getpass.getpass("Meshy API key (input hidden): ").strip()
    if not key:
        raise RuntimeError("No Meshy API key provided. Set MESHY_API_KEY or enter it at the prompt.")
    return key


def api_call(key: str, method: str = "GET", payload: dict | None = None, task_id: str | None = None) -> dict:
    url = API_BASE + (f"/{task_id}" if task_id else "")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {key}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Meshy returned HTTP {error.code}.") from None
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach Meshy: {error.reason}") from None


def wait_for_task(key: str, task_id: str, label: str) -> dict:
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        task = api_call(key, task_id=task_id)
        status = task.get("status", "UNKNOWN")
        progress = task.get("progress")
        print(f"{label}: {status}" + (f" ({progress}%)" if progress is not None else ""), flush=True)
        if status == "SUCCEEDED":
            return task
        if status in {"FAILED", "CANCELED"}:
            raise RuntimeError(f"Meshy task {status.lower()}: {task.get('task_error', {}).get('message', 'no details')}")
        time.sleep(10)
    raise TimeoutError(f"Timed out waiting for {label.lower()}.")


def main() -> int:
    try:
        key = read_key()
        preview = api_call(
            key,
            method="POST",
            payload={"mode": "preview", "prompt": PROMPT, "target_formats": ["glb"]},
        )
        preview_id = preview["result"]
        print(f"Preview task submitted: {preview_id}", flush=True)
        wait_for_task(key, preview_id, "Preview")

        refine = api_call(
            key,
            method="POST",
            payload={
                "mode": "refine",
                "preview_task_id": preview_id,
                "enable_pbr": True,
                "target_formats": ["glb"],
            },
        )
        refine_id = refine["result"]
        print(f"Texturing task submitted: {refine_id}", flush=True)
        final_task = wait_for_task(key, refine_id, "Texturing")

        model_url = final_task.get("model_urls", {}).get("glb")
        if not model_url:
            raise RuntimeError("Meshy reported success but did not return a GLB download URL.")
        with urllib.request.urlopen(model_url, timeout=180) as response:
            OUTPUT_FILE.write_bytes(response.read())

        credits = final_task.get("consumed_credits")
        print(f"Banana model saved to: {OUTPUT_FILE}")
        if credits is not None:
            print(f"Credits reported for the texturing task: {credits}")
        return 0
    except (OSError, KeyError, RuntimeError, TimeoutError) as error:
        print(f"Generation did not complete: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

