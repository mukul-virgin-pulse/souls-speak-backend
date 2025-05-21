from pydantic import BaseModel, Field
from typing import Optional

class AudioMetadata(BaseModel):
    title: Optional[str]
    description: Optional[str]

class AudioInDB(AudioMetadata):
    id: str = Field(default_factory=str)
    filename: str
    filepath: str
    transcription: str
