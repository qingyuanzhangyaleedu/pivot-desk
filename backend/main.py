"""Run from backend/: uvicorn main:app --port 8000."""

from pathlib import Path
import sys, json, asyncio, hashlib, io, zipfile
from contextlib import asynccontextmanager
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from backend import storage, tools, agent, config
from backend.models import (
    Profile,
    SearchRequest,
    AnalyzeRequest,
    ImportJob,
    Job,
    TrackerUpdate,
)

tasks = set()


@asynccontextmanager
async def lifespan(app):
    storage.initialize()
    with storage.db() as c:
        c.execute(
            "UPDATE runs SET status='error',error='Server restarted before this run finished. Retry when ready.' WHERE status IN ('queued','running')"
        )
    yield
    for t in tasks:
        t.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="Pivot Desk", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def boundary(request, call_next):
    if request.method in ["POST", "PUT", "DELETE"]:
        origin = request.headers.get("origin")
        if (
            origin
            and origin
            not in [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ]
        ) or request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Cross-site changes are blocked. Use the local Pivot Desk app."
                },
            )
        try:
            size = int(request.headers.get("content-length", "0") or 0)
        except ValueError:
            return JSONResponse(
                status_code=400, content={"detail": "Invalid request length."}
            )
        if size > 5 * 1024 * 1024:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large. Resumes must be under 4 MB."},
            )
    old = request.cookies.get("pivot_session")
    s = storage.session(old)
    request.state.session = s
    response = await call_next(request)
    if s != old:
        response.set_cookie(
            "pivot_session",
            s,
            httponly=True,
            samesite="strict",
            max_age=60 * 60 * 24 * 30,
        )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(ValueError)
async def bad_request(request, e):
    return JSONResponse(status_code=400, content={"detail": str(e)[:300]})


def sid(r):
    return r.state.session


def start(coro):
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)


def get_job(s, ident):
    public = storage.job(ident)
    return public or next(
        (x for x in storage.get(s, "imports", []) if x["id"] == ident), None
    )


def profile(s):
    p = storage.get(s, "profile")
    if not p or not p.get("confirmed"):
        raise HTTPException(409, "Review and save your resume profile first.")
    return p


@app.get("/api/status")
async def status(request: Request):
    return {
        "name": "Pivot Desk",
        "model": config.MODEL_NAME,
        "ai_available": config.key_status(),
        "source_count": len(tools.BOARDS),
        "industries": tools.INDUSTRIES,
        "profile": storage.get(sid(request), "profile"),
        "draft": storage.get(sid(request), "profile_draft"),
        "preferences": storage.get(sid(request), "preferences"),
        "privacy": "Resume files are processed in memory. Confirmed profile and extracted text stay in this local, browser-scoped workspace. AI extraction sends the resume text only after consent. Job analysis excludes contact and sensitive answers.",
        "limits": {
            "requests_per_run": config.REQUEST_LIMIT,
            "daily_ai_runs": config.DAILY_AI_CALLS,
            "tokens_per_run": config.TOKEN_LIMIT,
            "timeout_seconds": config.RUN_TIMEOUT,
        },
    }


@app.post("/api/demo")
async def demo(request: Request):
    data = json.loads((ROOT / "data/demo_profile.json").read_text())
    Profile.model_validate(data)
    storage.put(sid(request), "profile", data)
    storage.put(sid(request), "profile_draft", None)
    return data


@app.post("/api/resume")
async def resume(
    request: Request, file: UploadFile = File(...), consent: bool = Form(False)
):
    if not consent:
        raise HTTPException(
            400, "Confirm that the resume text may be sent to the configured AI model."
        )
    data = await file.read(4 * 1024 * 1024 + 1)
    try:
        text = await asyncio.to_thread(
            tools.extract_document, data, file.filename or ""
        )
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise HTTPException(
            400,
            "This document could not be read. Try another PDF/DOCX or paste the text.",
        ) from exc
    if not config.key_status():
        raise HTTPException(
            503,
            "AI key not configured. Use the demo profile to explore or configure the server key.",
        )
    s = sid(request)
    ident = agent.reserve(s, "resume")
    storage.put(s, "resume_text", text)
    start(agent.execute(s, ident, "resume", {"text": text}))
    return {"run_id": ident, "characters": len(text)}


@app.put("/api/profile")
async def update_profile(request: Request, body: Profile):
    if not body.confirmed:
        raise HTTPException(400, "Confirm that you reviewed the profile.")
    if len({f.id for f in body.facts}) != len(body.facts):
        raise HTTPException(400, "Fact IDs must be unique.")
    storage.put(sid(request), "profile", body.model_dump())
    storage.put(sid(request), "profile_draft", None)
    return body


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    s = sid(request)
    storage.put(s, "preferences", body.preferences.model_dump())
    refresh = (
        await tools.refresh_jobs()
        if body.refresh
        else {
            "sources": [],
            "cached": True,
            "message": "Using the stored public snapshot. Refresh for current source status.",
        }
    )
    p = storage.get(s, "profile")
    p = p if p and p.get("confirmed") else None
    jobs = storage.all_jobs() + storage.get(s, "imports", [])
    found = []
    excluded = 0
    for j in jobs:
        if tools.eligible(j, body.preferences):
            excluded += 1
            continue
        found.append({**j, **tools.rank(j, p, body.preferences)})
    found.sort(
        key=lambda x: (
            x["score"] if x["score"] is not None else -1,
            x["updated_at"] or "",
        ),
        reverse=True,
    )
    return {
        "jobs": found[:100],
        "total_matches": len(found),
        "screened": len(jobs),
        "excluded": excluded,
        "returned_cap": 100,
        **refresh,
    }


@app.post("/api/jobs/import")
async def import_job(request: Request, body: ImportJob):
    data = body.model_dump()
    low, high = tools.salary(body.description)
    j = Job(
        **data,
        id="manual:"
        + hashlib.sha256((body.url + body.title).encode()).hexdigest()[:20],
        source="User-pasted listing (not live-verified)",
        retrieved_at=storage.now(),
        job_type=tools.classify_type(body.title + " " + body.description),
        salary_min=low,
        salary_max=high,
    ).model_dump()
    existing = storage.get(sid(request), "imports", [])
    existing = [x for x in existing if x["id"] != j["id"]]
    storage.put(sid(request), "imports", (existing + [j])[-50:])
    return j


@app.post("/api/analyze")
async def analyze(request: Request, body: AnalyzeRequest):
    s = sid(request)
    p = profile(s)
    j = get_job(s, body.job_id)
    if not j:
        raise HTTPException(
            404, "Listing not found. Refresh search or import the posting."
        )
    key = agent.fit_key(p, j, body.compact)
    hit = agent.cached(s, key)
    if hit:
        return {"run_id": agent.cache_run(s, key, hit), "cached": True}
    if not config.key_status():
        raise HTTPException(
            503, "AI key not configured. Evidence-overlap scores still work locally."
        )
    ident = agent.reserve(s, "fit")
    start(agent.execute(s, ident, "fit", {"profile": p, "job": j}, body.compact, key))
    return {"run_id": ident, "cached": False}


@app.get("/api/runs/{ident}")
async def run(request: Request, ident: str):
    s = sid(request)
    with storage.db() as c:
        row = c.execute(
            "SELECT * FROM runs WHERE id=? AND session=?", (ident, s)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Run not found in this workspace.")
        events = [
            dict(x)
            for x in c.execute(
                "SELECT id,agent,action,summary,created FROM events WHERE run_id=? AND session=? ORDER BY id",
                (ident, s),
            )
        ]
        usage = c.execute(
            "SELECT input_tokens,cached_tokens,output_tokens,requests,cost FROM usage WHERE run_id=? AND session=?",
            (ident, s),
        ).fetchone()
    return {
        "run_id": ident,
        "kind": row["kind"],
        "status": row["status"],
        "result": json.loads(row["result"]) if row["result"] else None,
        "error": row["error"],
        "events": events,
        "usage": dict(usage) if usage else None,
    }


@app.get("/api/metrics")
async def metrics(request: Request):
    s = sid(request)
    with storage.db() as c:
        rows = [
            dict(x)
            for x in c.execute(
                "SELECT run_id,input_tokens,cached_tokens,output_tokens,requests,cost,created FROM usage WHERE session=? ORDER BY id DESC",
                (s,),
            )
        ]
        hits = c.execute(
            "SELECT COUNT(*) FROM runs WHERE session=? AND status='cached'", (s,)
        ).fetchone()[0]
    return {
        "runs": rows,
        "cache_hits": hits,
        "total_cost": sum(x["cost"] for x in rows),
        "input_tokens": sum(x["input_tokens"] for x in rows),
        "cached_tokens": sum(x["cached_tokens"] for x in rows),
        "output_tokens": sum(x["output_tokens"] for x in rows),
        "prices": config.PRICES,
        "price_source": config.PRICE_SOURCE,
        "price_checked": config.PRICE_CHECKED,
        "cost_note": "Estimated model cost using public standard rates; your provider invoice or course credits may differ.",
    }


@app.get("/api/tracker")
async def tracker(request: Request):
    with storage.db() as c:
        rows = [
            dict(x)
            for x in c.execute(
                "SELECT job_id,stage,note,follow_up,updated FROM tracker WHERE session=? ORDER BY updated DESC",
                (sid(request),),
            )
        ]
    return [{**r, "job": get_job(sid(request), r["job_id"])} for r in rows]


@app.put("/api/tracker")
async def track(request: Request, body: TrackerUpdate):
    if not get_job(sid(request), body.job_id):
        raise HTTPException(404, "Listing not found.")
    if body.follow_up:
        try:
            datetime.strptime(body.follow_up, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(400, "Use YYYY-MM-DD for the follow-up date.")
    with storage.db() as c:
        c.execute(
            "INSERT OR REPLACE INTO tracker VALUES (?,?,?,?,?,?)",
            (
                sid(request),
                body.job_id,
                body.stage,
                body.note,
                body.follow_up,
                storage.now(),
            ),
        )
    return {"saved": True}


@app.get("/api/packet")
async def packet(request: Request):
    return tools.export_packet(profile(sid(request)))


@app.get("/api/extension.zip")
async def extension():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (ROOT / "extension").iterdir():
            if p.is_file():
                z.write(p, p.name)
    return Response(
        out.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="pivot-desk-extension.zip"'
        },
    )


@app.delete("/api/private")
async def erase(request: Request):
    s = sid(request)
    with storage.db() as c:
        if c.execute(
            "SELECT 1 FROM runs WHERE session=? AND status IN ('queued','running')",
            (s,),
        ).fetchone():
            raise HTTPException(
                409, "Wait for the active run to finish before deleting this workspace."
            )
        for table in ["state", "tracker", "cache", "events"]:
            c.execute("DELETE FROM " + table + " WHERE session=?", (s,))
        c.execute(
            "UPDATE runs SET session='deleted',result=NULL,error=NULL WHERE session=?",
            (s,),
        )
        c.execute("UPDATE usage SET session='deleted' WHERE session=?", (s,))
    return {
        "deleted": True,
        "retained": "Anonymous usage totals remain to enforce the shared daily budget.",
    }


@app.get("/api/health")
async def health():
    return {"ok": True}


if (ROOT / "frontend/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "frontend/dist", html=True), name="app")
