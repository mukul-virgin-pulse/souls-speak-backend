from uuid import uuid4
import os
import shutil
from .schema import AudioInDB
from llm_models.transcript import asr_pipeline
from db.utils import DB  # Import your DB class

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
