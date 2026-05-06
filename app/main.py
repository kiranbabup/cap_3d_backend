from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="AI 3D Generation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev: allow all frontends
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

jobs = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-3d-generation-api"}


@app.post("/api/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required.")
    if len(files) > 8:
        raise HTTPException(status_code=400, detail="Maximum 8 images allowed.")

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    saved = []
    for f in files:
        if f.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file: {f.filename}")

        data = await f.read()
        if len(data) > 8 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large: {f.filename}")

        file_id = f"{uuid4()}_{f.filename}"
        file_path = UPLOAD_DIR / file_id
        file_path.write_bytes(data)
        saved.append({"name": f.filename, "storedAs": file_id})

    return {
        "message": "Images uploaded successfully.",
        "count": len(saved),
        "files": saved,
    }


@app.post("/api/process")
def process_to_3d(image_names: list[str]):
    if not image_names:
        raise HTTPException(status_code=400, detail="Image list cannot be empty.")

    job_id = str(uuid4())
    output_name = f"{job_id}.glb"
    output_path = OUTPUT_DIR / output_name
    output_path.write_text(
        "Mock GLB placeholder. Replace with real PyTorch/Open3D pipeline output.",
        encoding="utf-8",
    )

    jobs[job_id] = {
        "jobId": job_id,
        "status": "completed",
        "uploadedImages": image_names,
        "createdAt": datetime.utcnow().isoformat(),
        "modelFile": output_name,
        "segments": ["panel_A", "panel_B", "panel_C"],
        "supportedDownloads": ["glb", "obj", "stl"],
    }
    return jobs[job_id]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@app.get("/api/download/{job_id}/{fmt}")
def download_details(job_id: str, fmt: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    fmt = fmt.lower()
    if fmt not in {"glb", "obj", "stl"}:
        raise HTTPException(status_code=400, detail="Format must be glb, obj, or stl.")

    return {
        "jobId": job_id,
        "format": fmt,
        "message": "Download endpoint ready. Integrate file conversion here.",
        "file": f"{job_id}.{fmt}",
    }
