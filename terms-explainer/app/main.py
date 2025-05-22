from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.explainer import summarize_terms, extract_text_from_pdf
import uuid

app = FastAPI()

# Serve static files (if needed)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Enable CORS (adjust allow_origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for summaries
saved_summaries = {}

# Optional: Set max upload size in bytes (e.g., 5 MB)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/explain")
async def explain_terms(file: UploadFile):
    try:
        if not file.filename.lower().endswith((".txt", ".pdf")):
            raise HTTPException(status_code=400, detail="File must be .txt or .pdf")

        # Read content and check size
        file_bytes = await file.read()
        if len(file_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max 5MB allowed.")

        # Parse content
        if file.filename.lower().endswith(".pdf"):
            content = extract_text_from_pdf(file_bytes)
        else:
            content = file_bytes.decode("utf-8")

        # Generate summary
        summary, confidence = summarize_terms(content)

        if not summary.strip():
            raise HTTPException(status_code=500, detail="Summarization failed or returned empty.")

        # Store and return summary
        summary_id = str(uuid.uuid4())
        saved_summaries[summary_id] = summary

        return {
            "summary": summary,
            "confidence_score": confidence,
            "share_link": f"/share/{summary_id}"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/share/{summary_id}")
async def share_summary(summary_id: str):
    summary = saved_summaries.get(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return JSONResponse(content={"summary": summary})
