from transformers import pipeline

# Initialize the audio-classification pipeline with the model
pipe = pipeline("audio-classification", model="firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3")

# Path to your audio file (replace with your actual file path)
audio_file = "/Users/mukul.upadhyay/Documents/Hackathon/souls-speak-backend/scripts/sensitive.wav"

# Run emotion classification on the audio file
predictions = pipe(audio_file)

# Print the predictions
for pred in predictions:
    print(f"Label: {pred['label']}, Score: {pred['score']:.4f}")
