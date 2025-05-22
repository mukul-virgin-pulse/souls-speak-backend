from uuid import uuid4
import os
from .schema import AudioInDB
from llm_models.transcript import asr_pipeline
from db.utils import DB  # Import your DB class
from transformers import pipeline
from fastapi import UploadFile
import tempfile
from uuid import uuid4
from voice_note.schema import AudioInDB  # Assuming this is your Pydantic model
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize DB instance
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db = DB(MONGO_URL, "audio_db")
# fs = AsyncIOMotorGridFSBucket(db)


# MongoDB and GridFS setup


async def save_audio_file(file, title: str, description: str):
    # Upload file to GridFS
    file_id = await fs.upload_from_stream(file.filename, file.file)

    # Save file temporarily for transcription
    file.file.seek(0)
    temp_path = f"/tmp/{uuid4()}.wav"
    with open(temp_path, "wb") as temp_file:
        temp_file.write(await file.read())

    # Transcribe the audio
    result = asr_pipeline(temp_path)
    transcription = result["text"]

    # Prepare metadata document
    audio_doc = {
        "title": title,
        "description": description,
        "filename": file.filename,
        "file_id": str(file_id),
        "transcription": transcription
    }

    inserted_id = await db.create("audio_files", audio_doc)
    audio_doc["id"] = inserted_id
    return AudioInDB(**audio_doc)


async def get_audio_by_id(audio_id: str) -> AudioInDB:
    # import ipdb; ipdb.set_trace()
    document = await db.read("audio_files", audio_id)
    if not document:
        return None
    # document["id"] = document.pop("_id")
    return AudioInDB(**document)


async def get_all_audio_by_id():
    # import ipdb; ipdb.set_trace()
    document = await db.find("audio_files", {})
    if not document:
        return None
    # document["id"] = document.pop("_id")
    # return [TranscriptData(**doc) for doc in document]
    return document


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
