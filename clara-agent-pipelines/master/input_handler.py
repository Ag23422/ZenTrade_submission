import os
import whisper

TRANSCRIPT_DIR = "dataset/transcripts"

model = whisper.load_model("base")

AUDIO_EXT = [".wav", ".mp3", ".m4a", ".flac"]
TEXT_EXT = [".txt"]


def is_audio(file):
    return any(file.lower().endswith(e) for e in AUDIO_EXT)


def is_text(file):
    return any(file.lower().endswith(e) for e in TEXT_EXT)


def transcribe(file_path):

    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    name = os.path.basename(file_path).split(".")[0]
    transcript_path = f"{TRANSCRIPT_DIR}/{name}.txt"

    if os.path.exists(transcript_path):
        return open(transcript_path).read()

    result = model.transcribe(file_path)

    with open(transcript_path, "w") as f:
        f.write(result["text"])

    return result["text"]


def load_text(file_path):

    with open(file_path) as f:
        return f.read()


def get_transcript(file_path):

    if is_audio(file_path):
        return transcribe(file_path)

    if is_text(file_path):
        return load_text(file_path)

    raise ValueError("Unsupported input format")
