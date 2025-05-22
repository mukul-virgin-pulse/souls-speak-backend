from pydantic import BaseModel
from typing import Optional

class AudioMetadata(BaseModel):
    title: Optional[str]
    description: Optional[str]

class AudioInDB(BaseModel):
    id: str
    filename: Optional[str]
    title: Optional[str]
    description: Optional[str]
    transcription: str
    # file_data: str  # Base64-encoded audio
    content_type: str
