"""Audit the candidate repository and its history without printing secret values."""

import json, re, subprocess, sys, os
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
from backend import config, tools
from dotenv import dotenv_values


def git(*args):
    return subprocess.check_output(["git", *args], cwd=R)


files = sorted(
    set(
        git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
        .decode()
        .split("\0")
    )
    - {""}
)
secrets = []
for p in [R / ".env", R.parent / ".env"]:
    if p.exists():
        secrets.extend(
            v
            for k, v in dotenv_values(p).items()
            if v
            and len(v) > 14
            and any(word in k.upper() for word in ["KEY", "TOKEN", "SECRET"])
        )
for k in ["PORTKEY_API_KEY", "OPENAI_API_KEY", "GH_TOKEN", "GITHUB_TOKEN"]:
    v = os.getenv(k)
    if v and len(v) > 14:
        secrets.append(v)
secrets = list(set(secrets))
problems = []
for filename in files:
    p = R / filename
    if not p.is_file():
        continue
    if (
        p.name == ".env"
        or ("runtime" in p.parts)
        or (p.name.startswith(".env.") and p.name != ".env.example")
    ):
        problems.append({"file": filename, "reason": "Private/runtime file included"})
    blob = p.read_bytes()
    for value in secrets:
        if value.encode() in blob:
            problems.append(
                {"file": filename, "reason": "Configured credential present"}
            )
    if re.search(
        rb"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{25,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b",
        blob,
    ):
        problems.append(
            {
                "file": filename,
                "reason": "Credential-like pattern; manual review needed",
            }
        )
history = []
for row in git("rev-list", "--all", "--objects").decode().splitlines():
    sha, _, name = row.partition(" ")
    if not name:
        continue
    typ = git("cat-file", "-t", sha).decode().strip()
    if typ != "blob":
        continue
    blob = git("cat-file", "blob", sha)
    if Path(name).name == ".env" or any(v.encode() in blob for v in secrets):
        history.append(
            {
                "path": name,
                "object": sha,
                "reason": "Private env or configured credential in history",
            }
        )
required = [
    "AI_prompts.md",
    "requirements.txt",
    "requirements-dev.txt",
    ".env.example",
    ".gitignore",
    "README.md",
    "backend/main.py",
    "backend/agent.py",
    "backend/models.py",
    "backend/tools.py",
    "frontend/package-lock.json",
    "extension/manifest.json",
    "data/demo_profile.json",
    "data/demo_jobs.json",
    "report.html",
    "slides.html",
    "output/harness.md",
    "output/design.md",
    "output/usability.md",
    "output/agent_evaluation.md",
    "output/user_trial.html",
    "output/demo.webm",
    "output/submission_checklist.md",
]
missing = [x for x in required if not (R / x).is_file()]
result = {
    "candidate_file_count": len(files),
    "missing": missing,
    "credential_findings": problems,
    "historical_findings": history,
    "configured_credential_values_checked": len(secrets),
    "model": config.MODEL_NAME,
    "boards": len(tools.BOARDS),
    "sectors": len(tools.INDUSTRIES),
    "bundled_jobs": len(json.loads((R / "data/demo_jobs.json").read_text())),
    "git_remote_present": bool(git("remote").strip()),
    "passed": not (missing or problems or history),
    "note": "No secret values printed. Pattern scan and configured-value matching do not prove absence of every possible secret.",
}
(R / "output/evidence/release_check.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print(json.dumps(result, indent=2))
if not result["passed"]:
    sys.exit(1)
