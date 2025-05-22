from transformers import pipeline

# Load the model once
emotion_pipeline = pipeline(
    "audio-classification",
    model="firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"
)

def predict_emotion(audio_path: str):
    predictions = emotion_pipeline(audio_path)
    return [{"label": pred["label"], "score": round(pred["score"], 4)} for pred in predictions]
