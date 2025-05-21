from voice_note.views import voice_note_router
from fastapi import APIRouter

router = APIRouter(
    prefix = '/api/v1',
)


router.include_router(voice_note_router, prefix="/voice-note", tags=["Voice Notes"])

