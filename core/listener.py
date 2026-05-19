import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path


def record_audio(
    output_path: str = "data/test_command.wav",
    duration: int = 10,
    sample_rate: int = 16000,
) -> Path:
    """
    Records microphone audio and saves it as a WAV file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Recording for {duration} seconds...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )

    sd.wait()
    write(output_file, sample_rate, audio)

    print(f"Audio saved to: {output_file}")
    return output_file
