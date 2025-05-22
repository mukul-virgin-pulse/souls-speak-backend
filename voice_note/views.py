import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from voice_note.service import get_audio_by_id
from .service import calculate_average_scores, create_emotion_analysis, delete_audio_by_id, get_all_audio, get_all_emotion_analysis, get_emotion_by_id, save_audio_file

voice_note_router = APIRouter()

@voice_note_router.post("/upload-audio/")
async def upload_audio(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None)
):
    audio_doc = await save_audio_file(file, title, description)
    return audio_doc


@voice_note_router.get("/audio/{audio_id}")
async def fetch_audio(audio_id: str):
    audio_doc = await get_audio_by_id(audio_id)
    if not audio_doc:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio_doc


@voice_note_router.get("/get_all_audio")
async def fetch_audio():
    audio_doc = await get_all_audio()
    if not audio_doc:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio_doc


@voice_note_router.post("/analyze-emotion/")
async def analyze_emotion_endpoint(file: UploadFile = File(...)):
    """
    Accepts a voice note (.wav) and returns emotion predictions.
    Also stores the result in the database.
    """
    # Analyze the emotion

    result = await create_emotion_analysis(file)

    return result


@voice_note_router.get("/get_all_emotion/")
async def get_all_emotion():
    all_emotion_analysis = await get_all_emotion_analysis()
    if not all_emotion_analysis:
        raise HTTPException(status_code=404, detail="Audio not found")
    return all_emotion_analysis


@voice_note_router.post("/get_emotion_by_id/{emotion_id}")
async def get_emotion_endpoint(emotion_id: str):
    emotion_analysis = await get_emotion_by_id(emotion_id)
    if not emotion_analysis:
        raise HTTPException(status_code=404, detail="Audio not found")
    return emotion_analysis


@voice_note_router.get("/average-emotions/")
async def get_average_emotions():

    # Calculate averages
    average_scores = await calculate_average_scores()

    # Return as JSON
    return JSONResponse(content=average_scores)


@voice_note_router.delete("/delete-audio/{audio_id}")
async def delete_audio(audio_id: str):
    deleted_audio = await delete_audio_by_id(audio_id)
    if not delete_audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return deleted_audio