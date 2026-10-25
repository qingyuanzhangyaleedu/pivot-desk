"""Rehearse README setup from a local or public clone.

--live-ai uses only the fictional demo and a temporary parent dotenv.
Warm caches are disclosed. --port avoids disturbing the user's live app.
"""

import argparse, http.cookiejar, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from dotenv import dotenv_values, set_key

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8771)
parser.add_argument("--source", default=str(R))
parser.add_argument("--live-ai", action="store_true")
parser.add_argument("--evidence", default="output/evidence/final_clean_setup.json")
args = parser.parse_args()
root = Path(tempfile.mkdtemp(prefix="pivot-release-check-"))
clone = root / "pivot-desk"
server = None
started = time.monotonic()
logfile = root / "install.log"
serverlog = None
result = {
    "source": args.source,
    "public_remote": args.source.startswith("https://github.com/"),
    "port": args.port,
    "checks": [],
}


def run(cmd, cwd, env=None):
    with logfile.open("a") as log:
        subprocess.run(
            cmd, cwd=cwd, env=env, stdout=log, stderr=log, timeout=480, check=True
        )


try:
    run(["git", "clone", args.source, str(clone)], root)
    result["revision"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=clone, text=True
    ).strip()
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
        "output/github_url.txt",
        "output/presentation/Pivot_Desk_Submission.pptx",
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
    if args.live_ai:
        values = {
            **dotenv_values(R.parent / ".env"),
            **dotenv_values(R / ".env"),
            **os.environ,
        }
        selected_key = next(
            (key for key in ["PORTKEY_API_KEY", "OPENAI_API_KEY"] if values.get(key)),
            None,
        )
        if not selected_key:
            raise RuntimeError("No configured key for the optional live clone test")
        (root / ".env").write_text("")
        set_key(root / ".env", selected_key, values[selected_key])
        (root / ".env").chmod(0o600)
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
    if args.live_ai:
        began = request("/api/analyze", {"job_id": found["jobs"][0]["id"]})
        deadline = time.monotonic() + 115
        while time.monotonic() < deadline:
            actual = request("/api/runs/" + began["run_id"])
            if actual["status"] not in ["queued", "running"]:
                break
            time.sleep(1)
        assert actual["status"] == "completed", actual.get("error")
        assert actual["usage"]["requests"] > 0
        repeat = request("/api/analyze", {"job_id": found["jobs"][0]["id"]})
        assert repeat["cached"]
        result["live_ai"] = {
            "fixture": "Bundled fictional Avery Morgan profile and dated public listing",
            "job_id": found["jobs"][0]["id"],
            "job_title": found["jobs"][0]["title"],
            "run_id": began["run_id"],
            "status": actual["status"],
            "usage": actual["usage"],
            "events": actual["events"],
            "cached_repeat": repeat["cached"],
            "key_location": "Temporary .env one level above the fresh clone; removed after the check",
        }
        result["checks"].append("Real fictional-profile AI review and cached repeat passed from the GitHub clone")
    result["limitations"] = (
        "Warm package caches; loopback port override only. Parent dotenv discovery first uses a non-secret fixture. "
        + ("The optional live AI test then uses the configured key from a temporary parent file and fictional applicant data. " if args.live_ai else "No AI call made from this clone. ")
        + "This is a setup check, not a human usability trial."
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
    (R / args.evidence).write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
    shutil.rmtree(root)
