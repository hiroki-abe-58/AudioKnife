"""
Resemble Enhance Processor
Wraps the Resemble Enhance model for audio denoising and enhancement
"""

import asyncio
import torch
from pathlib import Path
from typing import Optional

class ResembleProcessor:
    """Processor for Resemble Enhance audio processing"""
    
    def __init__(self):
        self.device = self._get_device()
        self._model = None
        self._enhancer = None
    
    def _get_device(self) -> str:
        """Get the best available device"""
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        return "cpu"
    
    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from resemble_enhance.enhancer import enhance
                self._enhancer = enhance
            except ImportError:
                raise ImportError("resemble-enhance not installed. Run: pip install resemble-enhance")
    
    async def denoise(self, input_path: str, output_path: str) -> str:
        """
        Denoise audio using Resemble Enhance
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            
        Returns:
            Path to processed file
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._denoise_sync, input_path, output_path
        )
    
    def _denoise_sync(self, input_path: str, output_path: str) -> str:
        """Synchronous denoise implementation"""
        import torchaudio
        
        self._load_model()
        
        # Load audio
        audio, sr = torchaudio.load(input_path)
        
        # Move to device
        audio = audio.to(self.device)
        
        # Process with denoise only
        from resemble_enhance.enhancer import enhance
        enhanced, new_sr = enhance(
            audio.squeeze(0),
            sr,
            self.device,
            nfe=32,
            solver="midpoint",
            lambd=0.9,  # Higher = more denoising
            tau=0.5
        )
        
        # Save output
        torchaudio.save(output_path, enhanced.unsqueeze(0).cpu(), new_sr)
        
        return output_path
    
    async def enhance(self, input_path: str, output_path: str) -> str:
        """
        Enhance audio using Resemble Enhance (denoise + quality boost)
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            
        Returns:
            Path to processed file
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._enhance_sync, input_path, output_path
        )
    
    def _enhance_sync(self, input_path: str, output_path: str) -> str:
        """Synchronous enhance implementation"""
        import torchaudio
        
        self._load_model()
        
        # Load audio
        audio, sr = torchaudio.load(input_path)
        
        # Move to device
        audio = audio.to(self.device)
        
        # Process with full enhancement
        from resemble_enhance.enhancer import enhance
        enhanced, new_sr = enhance(
            audio.squeeze(0),
            sr,
            self.device,
            nfe=64,
            solver="midpoint",
            lambd=0.1,  # Lower = more enhancement
            tau=0.5
        )
        
        # Save output
        torchaudio.save(output_path, enhanced.unsqueeze(0).cpu(), new_sr)
        
        return output_path
