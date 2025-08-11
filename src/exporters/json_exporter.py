"""JSON exporter for structured data output."""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from ..app.logging import LoggerMixin
from ..utils.hashing import DeterministicHasher


class JSONExporter(LoggerMixin):
    """Exports data to JSON format with proper formatting and validation."""

    def __init__(self, output_dir: Path) -> None:
        """Initialize JSON exporter."""
        self.output_dir = output_dir

    def export_data(self, data: Any, filename: str) -> Dict[str, Any]:
        """Export data to JSON file."""
        self.logger.info("Starting JSON export", filename=filename)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare file path
        file_path = self.output_dir / filename
        
        try:
            # Convert data to JSON-serializable format
            serializable_data = self._make_serializable(data)
            
            # Write to file with proper formatting
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    serializable_data,
                    f,
                    indent=2,
                    default=str,
                    ensure_ascii=False,
                    sort_keys=True
                )
            
            # Calculate metadata
            file_size = file_path.stat().st_size
            content_hash = DeterministicHasher.content_fingerprint(serializable_data)
            record_count = self._count_records(serializable_data)
            
            result = {
                "filename": filename,
                "file_path": str(file_path),
                "file_size_bytes": file_size,
                "content_hash": content_hash,
                "record_count": record_count,
                "exported_at": datetime.now().isoformat()
            }
            
            self.logger.info("JSON export completed", **result)
            return result
            
        except Exception as e:
            self.logger.error("JSON export failed", filename=filename, error=str(e))
            raise

    def validate_json_file(self, file_path: Path) -> List[str]:
        """Validate JSON file format and structure."""
        errors = []
        
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return errors
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {e}")
        except Exception as e:
            errors.append(f"Error reading file: {e}")
        
        return errors

    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format."""
        if hasattr(data, 'model_dump'):
            # Pydantic model
            return data.model_dump()
        elif isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, (datetime, )):
            return data.isoformat()
        else:
            return data

    def _count_records(self, data: Any) -> int:
        """Count the number of records in the data."""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return 1
        else:
            return 1

    def create_index_file(self, file_manifests: List[Dict[str, Any]], statistics: Dict[str, Any]) -> Dict[str, Any]:
        """Create an index file with metadata about all exports."""
        index_data = {
            "generation_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "schema_version": "1.0"
            },
            "file_manifest": file_manifests,
            "statistics": statistics,
            "integrity": {
                "total_files": len(file_manifests),
                "total_records": sum(f.get("record_count", 0) for f in file_manifests),
                "manifest_hash": DeterministicHasher.batch_fingerprint(file_manifests)
            }
        }
        
        return self.export_data(index_data, "index.json")
