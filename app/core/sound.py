from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect


class SoundManager(QObject):
    def __init__(self, enabled: bool = True, parent=None):
        super().__init__(parent)
        self._enabled = bool(enabled)

        app_dir = Path(__file__).resolve().parents[1]
        self._sound_path = app_dir / "resources" / "sounds" / "reminder.wav"
        self._ensure_default_sound(self._sound_path)

        self._effect = QSoundEffect(self)
        self._effect.setLoopCount(1)
        self._effect.setVolume(0.7)
        self._effect.setSource(QUrl.fromLocalFile(str(self._sound_path)))

    def play_reminder(self):
        if not self._enabled:
            return
        if not self._sound_path.exists():
            self._ensure_default_sound(self._sound_path)
            self._effect.setSource(QUrl.fromLocalFile(str(self._sound_path)))
        self._effect.play()

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)

    def set_volume(self, volume: float):
        clamped = max(0.0, min(1.0, float(volume)))
        self._effect.setVolume(clamped)

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @staticmethod
    def _ensure_default_sound(sound_path: Path):
        sound_path.parent.mkdir(parents=True, exist_ok=True)
        if sound_path.exists() and sound_path.stat().st_size > 44:
            return

        sample_rate = 44_100
        duration_seconds = 0.5
        frequency_hz = 440.0
        amplitude = int(0.3 * 32767)
        total_samples = int(sample_rate * duration_seconds)

        with wave.open(str(sound_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                envelope = math.exp(-4.0 * t / duration_seconds)
                sample = int(amplitude * envelope * math.sin(2 * math.pi * frequency_hz * t))
                frames.extend(struct.pack("<h", sample))

            wav_file.writeframes(bytes(frames))
