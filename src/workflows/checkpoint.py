"""Workflow checkpointing and resume functionality."""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

import structlog

from ..app.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class WorkflowStep(Enum):
    """Workflow execution steps."""
    INDUSTRY_SELECTION = "industry_selection"
    ORG_DESIGN = "org_design"
    PRODUCT_STRATEGY = "product_strategy"
    SPRINT_PLANNING = "sprint_planning"
    TICKET_GENERATION = "ticket_generation"
    MAILBOX_GENERATION = "mailbox_generation"
    QA_AUDIT = "qa_audit"
    EXPORT_BUNDLER = "export_bundler"


class CheckpointManager(LoggerMixin):
    """Manages workflow checkpoints for resume functionality."""
    
    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """Initialize checkpoint manager."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Current session checkpoint file
        self.session_file = self.checkpoint_dir / "current_session.json"
        self.data_file = self.checkpoint_dir / "workflow_data.pkl"
        
        # Load existing session if available
        self.session_data = self._load_session()
        
    def _load_session(self) -> Dict[str, Any]:
        """Load existing session data."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning("Failed to load session data", error=str(e))
        
        return {
            "created_at": datetime.now().isoformat(),
            "steps_completed": [],
            "current_step": None,
            "last_updated": None,
            "step_results": {},
            "config_hash": None
        }
    
    def _save_session(self):
        """Save session metadata."""
        self.session_data["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            self.logger.error("Failed to save session data", error=str(e))
    
    def _save_data(self, data: Any):
        """Save workflow data using pickle."""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            self.logger.error("Failed to save workflow data", error=str(e))
    
    def _load_data(self) -> Optional[Any]:
        """Load workflow data using pickle."""
        if not self.data_file.exists():
            return None
            
        try:
            with open(self.data_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logger.warning("Failed to load workflow data", error=str(e))
            return None
    
    def save_step_result(self, step: WorkflowStep, result: Any, repo_state: Any):
        """Save the result of a completed step."""
        step_name = step.value
        
        # Update session metadata
        if step_name not in self.session_data["steps_completed"]:
            self.session_data["steps_completed"].append(step_name)
        
        self.session_data["current_step"] = step_name
        self.session_data["step_results"][step_name] = {
            "completed_at": datetime.now().isoformat(),
            "success": True,
            "result_type": str(type(result).__name__)
        }
        
        # Save the actual data
        checkpoint_data = {
            "step": step_name,
            "result": result,
            "repo_state": repo_state,
            "completed_steps": self.session_data["steps_completed"].copy()
        }
        
        self._save_data(checkpoint_data)
        self._save_session()
        
        self.logger.info(
            "✅ Checkpoint saved", 
            step=step_name,
            completed_steps=len(self.session_data["steps_completed"])
        )
    
    def save_step_failure(self, step: WorkflowStep, error: str):
        """Save information about a failed step."""
        step_name = step.value
        
        self.session_data["current_step"] = step_name
        self.session_data["step_results"][step_name] = {
            "completed_at": datetime.now().isoformat(),
            "success": False,
            "error": error
        }
        
        self._save_session()
        
        self.logger.error(
            "❌ Step failed", 
            step=step_name,
            error=error
        )
    
    def can_resume_from(self, step: WorkflowStep) -> bool:
        """Check if we can resume from a specific step."""
        step_name = step.value
        return step_name in self.session_data["steps_completed"]
    
    def get_last_successful_step(self) -> Optional[WorkflowStep]:
        """Get the last successfully completed step."""
        completed = self.session_data["steps_completed"]
        if not completed:
            return None
        
        # Return the last completed step
        last_step_name = completed[-1]
        
        try:
            return WorkflowStep(last_step_name)
        except ValueError:
            return None
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next step to execute."""
        all_steps = list(WorkflowStep)
        completed = set(self.session_data["steps_completed"])
        
        for step in all_steps:
            if step.value not in completed:
                return step
        
        return None  # All steps completed
    
    def load_checkpoint_data(self) -> Optional[Dict[str, Any]]:
        """Load the most recent checkpoint data."""
        return self._load_data()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of current progress."""
        all_steps = [step.value for step in WorkflowStep]
        completed = self.session_data["steps_completed"]
        
        progress = {
            "total_steps": len(all_steps),
            "completed_steps": len(completed),
            "progress_percentage": (len(completed) / len(all_steps)) * 100,
            "remaining_steps": [step for step in all_steps if step not in completed],
            "last_updated": self.session_data.get("last_updated"),
            "session_created": self.session_data.get("created_at")
        }
        
        return progress
    
    def clear_checkpoints(self):
        """Clear all checkpoint data."""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            if self.data_file.exists():
                self.data_file.unlink()
                
            self.session_data = self._load_session()  # Reset to empty
            
            self.logger.info("🗑️ All checkpoints cleared")
            
        except Exception as e:
            self.logger.error("Failed to clear checkpoints", error=str(e))
    
    def print_progress(self):
        """Print a nice progress summary."""
        progress = self.get_progress_summary()
        
        print("\n" + "="*60)
        print("🚀 WORKFLOW PROGRESS SUMMARY")
        print("="*60)
        
        completed = progress["completed_steps"]
        total = progress["total_steps"]
        percentage = progress["progress_percentage"]
        
        print(f"📊 Progress: {completed}/{total} steps ({percentage:.1f}%)")
        
        if progress["last_updated"]:
            print(f"⏰ Last updated: {progress['last_updated']}")
        
        print("\n✅ Completed Steps:")
        for step in self.session_data["steps_completed"]:
            step_info = self.session_data["step_results"].get(step, {})
            completed_at = step_info.get("completed_at", "Unknown time")
            print(f"   • {step.replace('_', ' ').title()} - {completed_at}")
        
        if progress["remaining_steps"]:
            print("\n⏳ Remaining Steps:")
            for step in progress["remaining_steps"]:
                print(f"   • {step.replace('_', ' ').title()}")
        
        print("="*60 + "\n")


def create_step_title(step: WorkflowStep, status: str = "EXECUTING") -> str:
    """Create a formatted step title."""
    step_name = step.value.replace('_', ' ').title()
    
    status_icons = {
        "EXECUTING": "🔄",
        "COMPLETED": "✅", 
        "FAILED": "❌",
        "SKIPPED": "⏭️"
    }
    
    icon = status_icons.get(status, "📋")
    
    title = f"\n{icon} {status}: {step_name}"
    separator = "="*60
    
    return f"\n{separator}\n{title}\n{separator}\n"
