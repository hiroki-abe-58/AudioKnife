"""
Spleeter Processor
Wraps the Spleeter model for vocal/music separation
"""

import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional

class SpleeterProcessor:
    """Processor for Spleeter audio source separation"""
    
    def __init__(self):
        self._venv_path = self._find_venv()
    
    def _find_venv(self) -> Optional[Path]:
        """Find Spleeter virtual environment"""
        search_paths = [
            Path.home() / "spleeter_env",
            Path.home() / "spleeter_venv",
            Path.home() / ".spleeter",
        ]
        
        for path in search_paths:
            if (path / "bin" / "spleeter").exists():
                return path
        return None
    
    async def separate(
        self, 
        input_path: str, 
        output_path: str,
        stems: str = "2stems",
        extract_stem: str = "vocals"
    ) -> str:
        """
        Separate audio sources using Spleeter
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            stems: Model type - 2stems, 4stems, or 5stems
            extract_stem: Which stem to extract (vocals, drums, bass, piano, other)
            
        Returns:
            Path to extracted stem
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._separate_sync, input_path, output_path, stems, extract_stem
        )
    
    def _separate_sync(
        self, 
        input_path: str, 
        output_path: str, 
        stems: str,
        extract_stem: str
    ) -> str:
        """Synchronous separation implementation"""
        import tempfile
        
        if self._venv_path is None:
            raise RuntimeError("Spleeter virtual environment not found")
        
        spleeter_cmd = self._venv_path / "bin" / "spleeter"
        
        # Create temp output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run spleeter
            cmd = [
                str(spleeter_cmd), "separate",
                "-p", f"spleeter:{stems}",
                "-o", str(temp_path),
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Spleeter failed: {result.stderr}")
            
            # Find output file
            input_name = Path(input_path).stem
            stem_path = temp_path / input_name / f"{extract_stem}.wav"
            
            if not stem_path.exists():
                # Try to find what was created
                created_dir = temp_path / input_name
                if created_dir.exists():
                    available = [f.name for f in created_dir.glob("*.wav")]
                    raise RuntimeError(f"{extract_stem} not found. Available: {available}")
                raise RuntimeError(f"Output not found: {stem_path}")
            
            # Copy to output path
            shutil.copy(stem_path, output_path)
        
        return output_path
