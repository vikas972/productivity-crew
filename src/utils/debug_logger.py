"""Debug logging utilities for LLM outputs and workflow debugging."""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..app.logging import LoggerMixin


class DebugLogger(LoggerMixin):
    """Enhanced debugging logger for LLM outputs and workflow data."""
    
    def __init__(self, debug_dir: str = "debug_logs"):
        """Initialize debug logger."""
        self.debug_dir = Path(debug_dir)
        self.debug_dir.mkdir(exist_ok=True)
        
        # Create session-specific subdirectory
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.debug_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)
        
        self.logger.info("🔍 Debug logger initialized", session_id=self.session_id, debug_dir=str(self.session_dir))
    
    def log_llm_output(self, step_name: str, agent_name: str, raw_output: Any, parsed_output: Any = None, error: Optional[str] = None) -> None:
        """Log LLM output for a specific step and agent."""
        timestamp = datetime.now().isoformat()
        
        # Create step-specific directory
        step_dir = self.session_dir / step_name
        step_dir.mkdir(exist_ok=True)
        
        # Log raw output
        raw_file = step_dir / f"{agent_name}_raw.txt"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(f"=== LLM RAW OUTPUT ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Step: {step_name}\n")
            f.write(f"Agent: {agent_name}\n")
            f.write(f"Output Type: {type(raw_output)}\n")
            f.write(f"="*50 + "\n\n")
            f.write(str(raw_output))
        
        # Log parsed output if available
        if parsed_output is not None:
            parsed_file = step_dir / f"{agent_name}_parsed.json"
            try:
                with open(parsed_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": timestamp,
                        "step": step_name,
                        "agent": agent_name,
                        "parsed_type": str(type(parsed_output)),
                        "parsed_data": parsed_output if isinstance(parsed_output, (dict, list)) else str(parsed_output)
                    }, f, indent=2, default=str)
            except Exception as e:
                # If JSON serialization fails, save as text
                with open(parsed_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"=== PARSED OUTPUT (JSON failed: {e}) ===\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"Parsed Type: {type(parsed_output)}\n")
                    f.write(f"="*50 + "\n\n")
                    f.write(str(parsed_output))
        
        # Log error if any
        if error:
            error_file = step_dir / f"{agent_name}_error.txt"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"=== ERROR LOG ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Step: {step_name}\n")
                f.write(f"Agent: {agent_name}\n")
                f.write(f"="*50 + "\n\n")
                f.write(error)
        
        self.logger.info("📝 LLM output logged", 
                        step=step_name, 
                        agent=agent_name, 
                        raw_file=str(raw_file),
                        has_parsed=parsed_output is not None,
                        has_error=error is not None)
    
    def log_validation_error(self, step_name: str, data_type: str, validation_error: str, raw_data: Any) -> None:
        """Log validation errors with the data that failed."""
        timestamp = datetime.now().isoformat()
        
        step_dir = self.session_dir / step_name
        step_dir.mkdir(exist_ok=True)
        
        error_file = step_dir / f"validation_error_{data_type}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"=== VALIDATION ERROR ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Step: {step_name}\n")
            f.write(f"Data Type: {data_type}\n")
            f.write(f"Error: {validation_error}\n")
            f.write(f"="*50 + "\n\n")
            f.write("=== RAW DATA THAT FAILED ===\n")
            f.write(str(raw_data))
        
        self.logger.error("❌ Validation error logged", 
                         step=step_name, 
                         data_type=data_type, 
                         error_file=str(error_file))
    
    def log_transformation_step(self, step_name: str, transformation_name: str, before_data: Any, after_data: Any) -> None:
        """Log data transformation steps."""
        timestamp = datetime.now().isoformat()
        
        step_dir = self.session_dir / step_name
        step_dir.mkdir(exist_ok=True)
        
        transform_file = step_dir / f"transform_{transformation_name}.json"
        try:
            with open(transform_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": timestamp,
                    "step": step_name,
                    "transformation": transformation_name,
                    "before": before_data if isinstance(before_data, (dict, list)) else str(before_data),
                    "after": after_data if isinstance(after_data, (dict, list)) else str(after_data)
                }, f, indent=2, default=str)
        except Exception as e:
            # If JSON fails, save as text
            with open(transform_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(f"=== TRANSFORMATION LOG ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Step: {step_name}\n")
                f.write(f"Transformation: {transformation_name}\n")
                f.write(f"JSON Error: {e}\n")
                f.write(f"="*50 + "\n\n")
                f.write("=== BEFORE ===\n")
                f.write(str(before_data))
                f.write("\n\n=== AFTER ===\n")
                f.write(str(after_data))
        
        self.logger.info("🔄 Transformation logged", 
                        step=step_name, 
                        transformation=transformation_name,
                        transform_file=str(transform_file))
    
    def log_repository_state(self, step_name: str, repo_state: Dict[str, Any]) -> None:
        """Log current repository state."""
        timestamp = datetime.now().isoformat()
        
        step_dir = self.session_dir / step_name
        step_dir.mkdir(exist_ok=True)
        
        repo_file = step_dir / "repository_state.json"
        try:
            # Create serializable version of repo state
            serializable_state = {
                "timestamp": timestamp,
                "step": step_name,
                "persons_count": len(repo_state.get("persons", {})),
                "tickets_count": len(repo_state.get("tickets", {})),
                "mail_messages_count": len(repo_state.get("mail_messages", {})),
                "company_context": repo_state.get("company_context")
            }
            
            with open(repo_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, indent=2, default=str)
        except Exception as e:
            with open(repo_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(f"=== REPOSITORY STATE ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Step: {step_name}\n")
                f.write(f"JSON Error: {e}\n")
                f.write(f"="*50 + "\n\n")
                f.write(str(repo_state))
        
        self.logger.info("📊 Repository state logged", 
                        step=step_name,
                        persons=len(repo_state.get("persons", {})),
                        tickets=len(repo_state.get("tickets", {})),
                        repo_file=str(repo_file))
    
    def get_session_summary(self) -> str:
        """Get a summary of the current debug session."""
        if not self.session_dir.exists():
            return "No debug session found."
        
        summary = [f"Debug Session: {self.session_id}"]
        summary.append(f"Location: {self.session_dir}")
        summary.append("="*50)
        
        for step_dir in sorted(self.session_dir.iterdir()):
            if step_dir.is_dir():
                files = list(step_dir.glob("*"))
                summary.append(f"📁 {step_dir.name}: {len(files)} files")
                for file_path in sorted(files):
                    summary.append(f"   📄 {file_path.name}")
        
        return "\n".join(summary)
