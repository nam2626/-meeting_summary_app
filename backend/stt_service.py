# backend/stt_service.py
import torch
from faster_whisper import WhisperModel
import os

class STTService:
    def __init__(self):
        # 하드웨어 자동 감지 로직
        if torch.cuda.is_available():
            self.model_size = "medium"
            self.device = "cuda"
            self.compute_type = "float16"
        else:
            self.model_size = "base"
            self.device = "cpu"
            self.compute_type = "int8"
        
        print(f"Loading Whisper model: {self.model_size} on {self.device} with {self.compute_type}")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def transcribe(self, audio_path: str):
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text.strip()

stt_service = STTService()
