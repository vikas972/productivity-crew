"""Base source generator classes."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path

from ..app.logging import LoggerMixin


class BaseSourceGenerator(LoggerMixin, ABC):
    """Base class for all source generators."""

    def __init__(self, config: Dict[str, Any], output_dir: Path) -> None:
        """Initialize the source generator."""
        self.config = config
        self.output_dir = output_dir

    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate source data and return results."""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> List[str]:
        """Validate generated output and return list of errors."""
        pass

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_generation_start(self, source_type: str, **kwargs: Any) -> None:
        """Log the start of generation."""
        self.logger.info(
            "Source generation started",
            source_type=source_type,
            **kwargs
        )

    def log_generation_complete(self, source_type: str, result: Dict[str, Any], **kwargs: Any) -> None:
        """Log the completion of generation."""
        self.logger.info(
            "Source generation completed",
            source_type=source_type,
            result_keys=list(result.keys()),
            **kwargs
        )
