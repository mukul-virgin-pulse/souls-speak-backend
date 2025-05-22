import torch
from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration
 
# Use CPU explicitly since GPU is not available
device = -1
 
model_id = "openai/whisper-small"
 
# Load processor and model
processor = WhisperProcessor.from_pretrained(model_id)
model = WhisperForConditionalGeneration.from_pretrained(model_id)
# model.saveFromPretrained(model_id)
 
# Create ASR pipeline with forced decoder ids to English transcription task
forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")
 
asr = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
    forced_decoder_ids=forced_decoder_ids,
    chunk_length_s=30,
)

# Example: transcribe a local audio file (replace with your file path)
# audio_file = "/Users/mukul.upadhyay/Documents/Hackathon/soulspeak/scripts/test-file-2.wav"
audio_file = "-------***-------"

# Run transcription
result = asr(audio_file)

print("Transcription:", result["text"])
