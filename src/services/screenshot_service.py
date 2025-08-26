"""
Screenshot Service for Craftbug Agentic System.
This module handles all screenshot processing, compression, and validation.
"""

import os
import base64
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

from config.settings import get_settings
from src.core.exceptions import ScreenshotError
from src.core.types import ScreenshotData


class ScreenshotService:
    """Service for handling screenshot processing."""
    
    def __init__(self, settings=None):
        """Initialize the screenshot service."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance tracking
        self.stats = {
            "total_processed": 0,
            "successful_compressions": 0,
            "failed_compressions": 0,
            "total_size_before": 0,
            "total_size_after": 0
        }
    
    async def process_screenshots(self, screenshot_paths: List[str]) -> List[ScreenshotData]:
        """Process multiple screenshots and return ScreenshotData objects."""
        results = []
        
        for path in screenshot_paths:
            try:
                screenshot_data = await self.process_single_screenshot(path)
                if screenshot_data:
                    results.append(screenshot_data)
            except Exception as e:
                self.logger.error(f"Failed to process screenshot {path}: {e}")
                self.stats["failed_compressions"] += 1
        
        return results
    
    async def process_single_screenshot(self, screenshot_path: str) -> Optional[ScreenshotData]:
        """Process a single screenshot and return ScreenshotData."""
        try:
            # Validate file exists
            if not os.path.exists(screenshot_path):
                raise ScreenshotError(f"Screenshot file not found: {screenshot_path}")
            
            # Get original file info
            original_size = os.path.getsize(screenshot_path)
            self.stats["total_size_before"] += original_size
            
            # Compress image
            compressed_bytes = await self._compress_image(screenshot_path)
            if not compressed_bytes:
                raise ScreenshotError(f"Failed to compress image: {screenshot_path}")
            
            # Encode to base64
            base64_data = base64.b64encode(compressed_bytes).decode('utf-8')
            
            # Get image dimensions
            dimensions = await self._get_image_dimensions(screenshot_path)
            
            # Update stats
            self.stats["total_processed"] += 1
            self.stats["successful_compressions"] += 1
            self.stats["total_size_after"] += len(compressed_bytes)
            
            return ScreenshotData(
                path=screenshot_path,
                base64=base64_data,
                size_bytes=len(compressed_bytes),
                width=dimensions[0] if dimensions else None,
                height=dimensions[1] if dimensions else None,
                format=self._get_image_format(screenshot_path)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing screenshot {screenshot_path}: {e}")
            self.stats["failed_compressions"] += 1
            return None
    
    async def _compress_image(self, image_path: str) -> Optional[bytes]:
        """Compress image for analysis."""
        try:
            from PIL import Image
            import io
            
            # Open and compress image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (keep width >= 1600px for quality)
                if img.width < 1600:
                    # Calculate new height maintaining aspect ratio
                    ratio = 1600 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1600, new_height), Image.Resampling.LANCZOS)
                
                # Save as high-quality JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95, optimize=True)
                return buffer.getvalue()
                
        except ImportError:
            # Fallback: read file directly
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Image compression failed for {image_path}: {e}")
            return None
    
    async def _get_image_dimensions(self, image_path: str) -> Optional[Tuple[int, int]]:
        """Get image dimensions."""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                return img.size
        except ImportError:
            # Fallback: try to get dimensions without PIL
            return None
        except Exception:
            return None
    
    def _get_image_format(self, image_path: str) -> Optional[str]:
        """Get image format from file extension."""
        ext = Path(image_path).suffix.lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return ext[1:]  # Remove the dot
        return None
    
    def validate_screenshot_path(self, path: str) -> bool:
        """Validate that a screenshot path is valid and file exists."""
        if not path:
            return False
        
        if not os.path.exists(path):
            return False
        
        # Check if it's a file
        if not os.path.isfile(path):
            return False
        
        # Check if it's a supported image format
        ext = Path(path).suffix.lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return False
        
        return True
    
    def deduplicate_screenshots(self, screenshot_paths: List[str]) -> List[str]:
        """Remove duplicate screenshots based on file size and content."""
        unique_paths = []
        seen_sizes = set()
        
        for path in screenshot_paths:
            if not self.validate_screenshot_path(path):
                continue
            
            try:
                file_size = os.path.getsize(path)
                if file_size in seen_sizes:
                    self.logger.info(f"Skipping duplicate screenshot (same size): {path}")
                    continue
                
                seen_sizes.add(file_size)
                unique_paths.append(path)
                
            except Exception as e:
                self.logger.error(f"Error checking screenshot {path}: {e}")
        
        return unique_paths
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        stats = self.stats.copy()
        if stats["total_processed"] > 0:
            stats["compression_ratio"] = stats["total_size_after"] / stats["total_size_before"]
            stats["success_rate"] = stats["successful_compressions"] / stats["total_processed"]
        return stats
    
    def reset_stats(self):
        """Reset service statistics."""
        self.stats = {
            "total_processed": 0,
            "successful_compressions": 0,
            "failed_compressions": 0,
            "total_size_before": 0,
            "total_size_after": 0
        }
