from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from voice_note.service import get_audio_by_id
from .service import analyze_emotion, get_all_audio_by_id, save_audio_file

voice_note_router = APIRouter()

@voice_note_router.post("/upload-audio/")
async def upload_audio(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None)
):
    audio_doc = await save_audio_file(file, title, description)
    return JSONResponse(audio_doc.dict())


@voice_note_router.get("/audio/{audio_id}")
async def fetch_audio(audio_id: str):
    audio_doc = await get_audio_by_id(audio_id)
    if not audio_doc:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio_doc


@voice_note_router.get("/transcription")
async def fetch_audio():
    audio_doc = await get_all_audio_by_id()
    if not audio_doc:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio_doc


@voice_note_router.post("/analyze-emotion/")
async def analyze_emotion_endpoint(file: UploadFile = File(...)):
    """
    Accepts a voice note (.wav) and returns emotion predictions.
    """
    results = analyze_emotion(file)
    return {"predictions": results}
