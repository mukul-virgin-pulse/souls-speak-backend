from uuid import uuid4
import os
import shutil
from .schema import AudioInDB
from llm_models.transcript import asr_pipeline
from db.utils import DB  # Import your DB class
from transformers import pipeline
from fastapi import UploadFile
import tempfile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize DB instance
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db = DB(MONGO_URL, "audio_db")

async def save_audio_file(file, title: str, description: str):
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe the audio
    result = asr_pipeline(file_path)
    transcription = result["text"]

    audio_doc = {
        "filename": unique_filename,
        "filepath": file_path,
        "title": title,
        "description": description,
        "transcription": transcription
    }

    inserted_id = await db.create("audio_files", audio_doc)
    audio_doc["id"] = inserted_id

    return AudioInDB(**audio_doc)


async def get_audio_by_id(audio_id: str) -> AudioInDB:
    document = await db.read("audio_files", audio_id)
    if not document:
        return None
    document["id"] = document.pop("_id")
    return AudioInDB(**document)


# Load the model once when the service is initialized
emotion_pipeline = pipeline(
    "audio-classification",
    model="firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"
)


def analyze_emotion(audio_file: UploadFile):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.file.read())
        tmp_path = tmp.name

    # Run the model on the saved file
    predictions = emotion_pipeline(tmp_path)

    # Format the results
    return [{"label": pred["label"], "score": round(pred["score"], 4)} for pred in predictions]
