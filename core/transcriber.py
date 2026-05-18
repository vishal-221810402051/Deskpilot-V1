from pathlib import Path
from faster_whisper import WhisperModel


class SpeechTranscriber:
    """
    Handles offline speech-to-text using faster-whisper.
    """

    def __init__(self, model_size: str = "base"):
        print(f"Loading Whisper model: {model_size}")
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )
        print("Whisper model loaded.")

    def transcribe_audio(self, audio_path: str | Path) -> str:
        audio_file = Path(audio_path)

        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        print(f"Transcribing: {audio_file}")

        segments, info = self.model.transcribe(
            str(audio_file),
            beam_size=5,
            language="en",
        )

        text_parts = []

        for segment in segments:
            text_parts.append(segment.text.strip())

        final_text = " ".join(text_parts).strip().lower()

        print(f"Detected language: {info.language}")
        print(f"Transcribed text: {final_text}")

        return final_text
