from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration

# Use CPU
device = -1
model_id = "openai/whisper-small"

# Load processor and model
processor = WhisperProcessor.from_pretrained(model_id)
model = WhisperForConditionalGeneration.from_pretrained(model_id)

# Create ASR pipeline
forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
    forced_decoder_ids=forced_decoder_ids,
    chunk_length_s=30,
)
