"""JSONL exporter for line-delimited JSON output."""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from ..app.logging import LoggerMixin
from ..utils.hashing import DeterministicHasher


class JSONLExporter(LoggerMixin):
    """Exports data to JSONL format with proper formatting and validation."""

    def __init__(self, output_dir: Path) -> None:
        """Initialize JSONL exporter."""
        self.output_dir = output_dir

    def export_data(self, data: List[Any], filename: str) -> Dict[str, Any]:
        """Export list of data to JSONL file."""
        self.logger.info("Starting JSONL export", filename=filename, record_count=len(data))
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare file path
        file_path = self.output_dir / filename
        
        try:
            # Write to JSONL file
            with open(file_path, "w", encoding="utf-8") as f:
                for item in data:
                    # Convert to JSON-serializable format
                    serializable_item = self._make_serializable(item)
                    
                    # Write as single line JSON
                    json_line = json.dumps(
                        serializable_item,
                        default=str,
                        ensure_ascii=False,
                        separators=(',', ':')  # Compact format
                    )
                    f.write(json_line + "\n")
            
            # Calculate metadata
            file_size = file_path.stat().st_size
            serializable_data = [self._make_serializable(item) for item in data]
            content_hash = DeterministicHasher.batch_fingerprint(serializable_data)
            
            result = {
                "filename": filename,
                "file_path": str(file_path),
                "file_size_bytes": file_size,
                "content_hash": content_hash,
                "record_count": len(data),
                "exported_at": datetime.now().isoformat()
            }
            
            self.logger.info("JSONL export completed", **result)
            return result
            
        except Exception as e:
            self.logger.error("JSONL export failed", filename=filename, error=str(e))
            raise

    def validate_jsonl_file(self, file_path: Path) -> List[str]:
        """Validate JSONL file format and structure."""
        errors = []
        
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return errors
        
        try:
            line_count = 0
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        json.loads(line)
                        line_count += 1
                    except json.JSONDecodeError as e:
                        errors.append(f"Line {line_num}: Invalid JSON - {e}")
            
            if line_count == 0:
                errors.append("File is empty or contains no valid JSON lines")
                
        except Exception as e:
            errors.append(f"Error reading file: {e}")
        
        return errors

    def read_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read and parse JSONL file."""
        data = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        
        return data

    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format."""
        if hasattr(data, 'model_dump'):
            # Pydantic model
            serialized = data.model_dump()
            # Handle field aliases (like 'from' -> 'from_')
            if hasattr(data, '__fields__'):
                for field_name, field_info in data.__fields__.items():
                    if hasattr(field_info, 'alias') and field_info.alias:
                        if field_name in serialized and field_info.alias not in serialized:
                            serialized[field_info.alias] = serialized.pop(field_name)
            return serialized
        elif isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, (datetime, )):
            return data.isoformat()
        else:
            return data

    def export_by_key(self, data: Dict[str, List[Any]], filename_pattern: str) -> List[Dict[str, Any]]:
        """Export data grouped by key to separate JSONL files."""
        results = []
        
        for key, items in data.items():
            filename = filename_pattern.format(key=key)
            result = self.export_data(items, filename)
            result["key"] = key
            results.append(result)
        
        return results
