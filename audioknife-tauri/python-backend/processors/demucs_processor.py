"""
Demucs Processor
Wraps the Demucs model for music source separation / BGM removal
"""

import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional

class DemucsProcessor:
    """Processor for Demucs audio source separation"""
    
    def __init__(self, model: str = "htdemucs"):
        self.model = model
        self._venv_path = self._find_venv()
    
    def _find_venv(self) -> Optional[Path]:
        """Find Demucs virtual environment"""
        search_paths = [
            Path.home() / "demucs_venv310",
            Path.home() / "demucs_venv",
            Path.home() / ".demucs",
        ]
        
        for path in search_paths:
            if (path / "bin" / "python").exists():
                return path
        return None
    
    async def separate(
        self, 
        input_path: str, 
        output_path: str,
        stems: str = "vocals"
    ) -> str:
        """
        Separate audio sources using Demucs
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            stems: Which stem to extract (vocals, drums, bass, other)
            
        Returns:
            Path to extracted stem
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._separate_sync, input_path, output_path, stems
        )
    
    def _separate_sync(self, input_path: str, output_path: str, stems: str) -> str:
        """Synchronous separation implementation"""
        import tempfile
        
        if self._venv_path is None:
            raise RuntimeError("Demucs virtual environment not found")
        
        python_path = self._venv_path / "bin" / "python"
        
        # Create temp output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run demucs
            cmd = [
                str(python_path), "-m", "demucs.separate",
                "-n", self.model,
                "--two-stems=vocals",
                "-d", "mps" if self._check_mps() else "cpu",
                "-o", str(temp_path),
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Demucs failed: {result.stderr}")
            
            # Find output file
            input_name = Path(input_path).stem
            vocals_path = temp_path / self.model / input_name / f"{stems}.wav"
            
            if not vocals_path.exists():
                raise RuntimeError(f"Output not found: {vocals_path}")
            
            # Copy to output path
            shutil.copy(vocals_path, output_path)
        
        return output_path
    
    def _check_mps(self) -> bool:
        """Check if MPS is available"""
        try:
            import torch
            return torch.backends.mps.is_available()
        except:
            return False
