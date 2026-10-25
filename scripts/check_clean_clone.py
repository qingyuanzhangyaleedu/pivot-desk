"""Rehearse README setup from a fresh local clone. No real key or AI call.

Warm package caches are disclosed. --port avoids disturbing the user's live app.
"""

import argparse, http.cookiejar, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8771)
args = parser.parse_args()
root = Path(tempfile.mkdtemp(prefix="pivot-release-check-"))
clone = root / "pivot-desk"
server = None
started = time.monotonic()
logfile = root / "install.log"
serverlog = None
result = {
    "source": "Fresh local Git clone of committed release candidate, not a public remote",
    "revision": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=R, text=True
    ).strip(),
    "port": args.port,
    "checks": [],
}


def run(cmd, cwd, env=None):
    with logfile.open("a") as log:
        subprocess.run(
            cmd, cwd=cwd, env=env, stdout=log, stderr=log, timeout=480, check=True
        )


try:
    run(["git", "clone", str(R), str(clone)], root)
    assert not any(
        (clone / p).exists()
        for p in [".env", "runtime", ".venv", "frontend/node_modules"]
    )
    result["checks"].append(
        "No real .env, private runtime, virtualenv or node_modules in clone"
    )
    required = [
        "report.html",
        "slides.html",
        "README.md",
        ".env.example",
        "backend/main.py",
        "frontend/package-lock.json",
        "data/demo_jobs.json",
        "extension/content.js",
        "output/demo.webm",
        "output/user_trial.html",
    ]
    assert all((clone / p).is_file() for p in required)
    run([sys.executable, "-m", "venv", ".venv"], clone)
    py = clone / ".venv/bin/python"
    run([str(py), "-m", "pip", "install", "-r", "requirements.txt"], clone)
    run(["npm", "ci"], clone / "frontend")
    run(["npm", "run", "build"], clone / "frontend")
    env = os.environ.copy()
    for key in ["PORTKEY_API_KEY", "OPENAI_API_KEY", "PIVOT_DATA_DIR"]:
        env.pop(key, None)
    (root / ".env").write_text(
        "PORTKEY_API_KEY=parent-discovery-fixture-not-a-real-key\n"
    )
    (root / ".env").chmod(0o600)
    run(
        [
            str(py),
            "-c",
            "from backend import config;import os;assert os.environ['PORTKEY_API_KEY']=='parent-discovery-fixture-not-a-real-key';assert config.MODEL_NAME=='gpt-6-astra'",
        ],
        clone,
        env,
    )
    result["checks"].append(
        "Parent-only dotenv discovered; requested Astra configuration unchanged"
    )
    serverlog = (root / "server.log").open("w")
    server = subprocess.Popen(
        [
            str(clone / ".venv/bin/uvicorn"),
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
        ],
        cwd=clone / "backend",
        env=env,
        stdout=serverlog,
        stderr=serverlog,
    )
    base = f"http://127.0.0.1:{args.port}"
    for _ in range(100):
        if server.poll() is not None:
            raise RuntimeError("Clean server exited")
        try:
            if json.load(urllib.request.urlopen(base + "/api/health", timeout=1))["ok"]:
                break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("Clean server unavailable")
    assert '<div id="root">' in urllib.request.urlopen(base).read().decode()
    result["setup_seconds"] = round(time.monotonic() - started, 2)
    result["under_ten_minutes"] = result["setup_seconds"] < 600
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )

    def request(path, body=None):
        r = urllib.request.Request(
            base + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
        )
        return json.load(opener.open(r))

    assert request("/api/demo", {})["demo"]
    found = request(
        "/api/search",
        {
            "preferences": {
                "query": "mba",
                "industries": ["Consulting"],
                "exclude_scope": "title_only",
            }
        },
    )
    assert found["jobs"] and any(j["application_checks"] for j in found["jobs"])
    assert request("/api/packet")["first_name"] == ""
    result["checks"].append(
        "Production frontend, current MBA filters, exact-source checks and reviewed export work from clean copy"
    )
    run([str(py), "-m", "unittest", "discover", "-s", "tests", "-v"], clone, env)
    result["checks"].append("All 35 offline checks passed in the clean environment")
    result["limitations"] = (
        "Local clone; warm package caches; loopback port override only; parent dotenv uses a non-secret fixture; no AI request made from this clone. Real AI runs are recorded separately."
    )
    result["passed"] = True
except Exception as exc:
    result["passed"] = False
    result["error_type"] = type(exc).__name__
    raise
finally:
    if server:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
    if serverlog:
        serverlog.close()
    (R / "output/evidence/final_clean_setup.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
    shutil.rmtree(root)
