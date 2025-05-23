import datetime
from typing import Dict
from uuid import uuid4
import os
from .schema import AudioInDB
from llm_models.transcript import asr_pipeline
from db.utils import DB
from transformers import pipeline
from fastapi import UploadFile
import tempfile
from uuid import uuid4
from voice_note.schema import AudioInDB
import gridfs
from pymongo import MongoClient
from fastapi.responses import StreamingResponse
from bson.objectid import ObjectId


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize DB instance
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db = DB(MONGO_URL, "audio_db")

client = MongoClient(MONGO_URL)
aDB = client["audio_store"]
fs = gridfs.GridFS(aDB)
fs_files_collection = aDB["fs.files"]


# MongoDB and GridFS setup


async def save_audio_file(file, title: str, description: str):
    file.file.seek(0)
    temp_path = f"/tmp/{uuid4()}.wav"
    with open(temp_path, "wb") as temp_file:
        temp_file.write(await file.read())

    # Transcribe the audio
    result = asr_pipeline(temp_path)
    transcription = result["text"]

    # Analyze emotion
    predictions = predictions = emotion_pipeline(temp_file.name)
    [{"label": pred["label"], "score": round(pred["score"], 4)} for pred in predictions]

    # Upload to GridFS
    file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)

    # Prepare metadata document
    audio_doc = {
        "filename": file.filename,
        "title": title,
        "description": description,
        "transcription": transcription,
        "created_at": datetime.datetime.utcnow(),
        "content_type": file.content_type,
        "predictions": predictions,
        "file_id": str(file_id)
    }

    inserted_id = await db.create("audio_files", audio_doc)

    audio_doc["_id"] = inserted_id
    audio_doc["created_at"] = audio_doc["created_at"].isoformat()

    return AudioInDB(**audio_doc)


async def get_audio_by_id(audio_id: str) -> AudioInDB:
    document = await db.read("audio_files", audio_id)
    if not document:
        return None
    # document["id"] = document.pop("_id")
    document["created_at"] = document["created_at"].isoformat()
    return AudioInDB(**document)


async def get_all_audio():
    document = await db.find("audio_files", {})
    if not document:
        return None
    
    for doc in document:
        doc["created_at"] = doc["created_at"].isoformat()
        doc["file_id"] = str(doc["file_id"])
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


async def create_emotion_analysis(file: UploadFile):
    results = analyze_emotion(file)

    # Prepare the document to store
    document = {
        "filename": file.filename,
        "predictions": results,
        "timestamp": datetime.datetime.utcnow()
    }

    # Store in the database
    inserted_id = await db.create("emotion_analysis", document)

    return {"predictions": results, "document_id": inserted_id}


async def get_all_emotion_analysis():
    document = await db.find("emotion_analysis", {})
    if not document:
        return None
    return document


async def get_emotion_by_id(emotion_id: str):
    document = await db.read("emotion_analysis", emotion_id)
    if not document:
        return None
    return document


async def calculate_average_scores() -> Dict[str, float]:
        
    documents = await db.find("emotion_analysis", {})

    score_sums = {}
    label_counts = {}

    for entry in documents:
        for prediction in entry["predictions"]:
            label = prediction["label"]
            score = prediction["score"]

            if label in score_sums:
                score_sums[label] += score
                label_counts[label] += 1
            else:
                score_sums[label] = score
                label_counts[label] = 1

    average_scores = {
        label: round(score_sums[label] / label_counts[label], 4)
        for label in score_sums
    }

    return average_scores


async def delete_audio_by_id(audio_id: str):
    document = await db.read("audio_files", audio_id)
    if not document:
        return {"Audio not found"}
    
    deleted_data = {
        "title": document["title"],
        "id": document["_id"]
    }
    
    deleted_count = await db.delete("audio_files", audio_id)

    return {"deleted_count": deleted_count, "deleted_data": deleted_data}


async def download_file(self, file_id: str):
    files_cursor = fs_files_collection.find()
    files = []
    for file_doc in files_cursor:
        files.append({
            "file_id": str(file_doc["_id"]),
            "filename": file_doc.get("filename"),
            "length": file_doc.get("length"),
            "uploadDate": file_doc.get("uploadDate").isoformat() if file_doc.get("uploadDate") else None,
            "contentType": file_doc.get("metadata", {}).get("contentType") if file_doc.get("metadata") else None,
        })
    return files


def get_all_audio_files():
    files = []
    
    for file_doc in fs_files_collection.find():
        files.append({
            "file_id": str(file_doc["_id"]),
            "filename": file_doc.get("filename"),
            "length": file_doc.get("length"),
            "uploadDate": file_doc.get("uploadDate").isoformat() if file_doc.get("uploadDate") else None,
            "contentType": file_doc.get("metadata", {}).get("contentType") if file_doc.get("metadata") else None,
        })
    return files

async def get_playable_audio(file_id):     
    oid = ObjectId(file_id)
    grid_out = fs.get(oid)
    return StreamingResponse(
        grid_out,
        media_type=grid_out.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{grid_out.filename}"'}
    )


async def get_all_list_audio():
    audio_files = await db.find("audio_files", {})
    if not audio_files:
        return {"No Audio files found"}
    
    for doc in audio_files:
        doc["created_at"] = doc["created_at"].isoformat()
        doc["file_id"] = str(doc["file_id"])

    return audio_files