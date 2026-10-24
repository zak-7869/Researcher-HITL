import logging, time, uuid
from collections import defaultdict, deque
from threading import Lock
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .config import settings
from .graph import build_graph
from .schemas import ResearchRequest, ReviewRequest
from .metrics import REQUESTS, RUNS, RUN_DURATION

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("researcher")
app = FastAPI(title="Researcher AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=False, allow_methods=["GET","POST","OPTIONS"],
                   allow_headers=["Content-Type","X-Request-ID"])
graph = build_graph()
runs = {}
events = defaultdict(deque)
lock = Lock()

@app.middleware("http")
async def telemetry(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:100]
    request.state.request_id = rid
    if request.url.path == "/api/research" and request.method == "POST":
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        with lock:
            q = events[ip]
            while q and now - q[0] > 60: q.popleft()
            if len(q) >= max(1, settings.max_requests_per_minute):
                return JSONResponse(status_code=429, content={"detail":"Rate limit exceeded","request_id":rid})
            q.append(now)
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    REQUESTS.labels(route=request.url.path, status=str(response.status_code)).inc()
    log.info("http_request", extra={"request_id":rid,"path":request.url.path,
             "status":response.status_code,"duration_ms":round((time.perf_counter()-start)*1000,2)})
    return response

@app.get("/api/health")
def health():
    return {"status":"ok","service":"researcher-ai-api","model":settings.groq_model}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/research")
def research(payload: ResearchRequest, request: Request):
    rid = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        result = graph.invoke({"run_id":rid,"topic":payload.topic,
            "max_iterations":payload.max_iterations,"iteration":0,"sources":[],"status":"running"})
        record = {"run_id":rid,"topic":payload.topic,"status":result.get("status","pending_review"),
            "report":result.get("report",""),"sources":result.get("sources",[]),
            "iterations":result.get("iteration",0),"evaluation":result.get("evaluation",{}),
            "plan":result.get("plan",""),"review_comment":""}
        runs[rid] = record
        RUNS.labels(status=record["status"]).inc()
        RUN_DURATION.observe(time.perf_counter()-started)
        return record
    except Exception as exc:
        RUNS.labels(status="failed").inc()
        log.exception("research_failed", extra={"run_id":rid,"request_id":request.state.request_id})
        raise HTTPException(status_code=502, detail=f"Research failed; reference request ID {request.state.request_id}. Check server logs.") from exc

@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in runs: raise HTTPException(status_code=404, detail="Run not found; this starter uses in-memory storage")
    return runs[run_id]

@app.post("/api/research/{run_id}/review")
def review(run_id: str, payload: ReviewRequest):
    record = runs.get(run_id)
    if not record: raise HTTPException(status_code=404, detail="Run not found")
    if record["status"] != "pending_review": raise HTTPException(status_code=409, detail="Run has already been reviewed")
    record["status"] = "approved" if payload.decision == "approve" else "changes_requested"
    record["review_comment"] = payload.comment
    RUNS.labels(status=record["status"]).inc()
    return {"run_id":run_id,"status":record["status"],"comment":payload.comment}
