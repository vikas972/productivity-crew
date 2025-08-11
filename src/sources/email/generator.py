"""Email source generator for mailbox data."""

import json
from typing import Any, Dict, List
from pathlib import Path

from ..base import BaseSourceGenerator
from ...okg.models import MailMessage
from ...utils.hashing import DeterministicHasher


class EmailGenerator(BaseSourceGenerator):
    """Generator for email JSONL export format."""

    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mail_<person_id>.jsonl files from email data."""
        self.log_generation_start("email")
        
        mail_messages = data.get("mail_messages", {})
        persons = data.get("persons", [])
        
        if not mail_messages:
            raise ValueError("No mail messages available for email generation")
        
        # Ensure output directory exists
        self.ensure_output_dir()
        
        generated_files = []
        total_emails = 0
        emails_by_person = {}
        emails_by_category = {}
        
        # Generate one JSONL file per person
        for person_id, messages in mail_messages.items():
            if not messages:
                continue
            
            # Sort messages deterministically by timestamp
            sorted_messages = sorted(messages, key=lambda m: m.timestamp)
            
            # Convert to dictionaries for JSONL serialization
            message_dicts = []
            for message in sorted_messages:
                if isinstance(message, MailMessage):
                    message_dict = message.model_dump()
                    # Handle the alias for 'from' field
                    if 'from_' in message_dict:
                        message_dict['from'] = message_dict.pop('from_')
                    message_dicts.append(message_dict)
                else:
                    message_dicts.append(message)
            
            # Write to JSONL file
            output_file = self.output_dir / f"mail_{person_id}.jsonl"
            with open(output_file, "w", encoding="utf-8") as f:
                for message_dict in message_dicts:
                    json_line = json.dumps(message_dict, default=str, ensure_ascii=False)
                    f.write(json_line + "\n")
            
            # Calculate metadata
            file_size = output_file.stat().st_size
            content_hash = DeterministicHasher.batch_fingerprint(message_dicts)
            
            file_info = {
                "filename": output_file.name,
                "person_id": person_id,
                "message_count": len(message_dicts),
                "file_size_bytes": file_size,
                "content_hash": content_hash,
            }
            
            generated_files.append(file_info)
            total_emails += len(message_dicts)
            emails_by_person[person_id] = len(message_dicts)
            
            # Count by category
            for message_dict in message_dicts:
                category = message_dict.get("category", "unknown")
                emails_by_category[category] = emails_by_category.get(category, 0) + 1
        
        result = {
            "files_generated": generated_files,
            "total_emails": total_emails,
            "emails_by_person": emails_by_person,
            "emails_by_category": emails_by_category,
            "persons_with_email": len(emails_by_person),
        }
        
        self.log_generation_complete("email", result)
        return result

    def validate_output(self, output: Dict[str, Any]) -> List[str]:
        """Validate email output."""
        errors = []
        
        files_generated = output.get("files_generated", [])
        if not files_generated:
            errors.append("No email files were generated")
            return errors
        
        for file_info in files_generated:
            filename = file_info.get("filename", "")
            file_path = self.output_dir / filename
            
            if not file_path.exists():
                errors.append(f"Email file does not exist: {file_path}")
                continue
            
            try:
                # Validate JSONL format
                with open(file_path, "r", encoding="utf-8") as f:
                    line_count = 0
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            data = json.loads(line)
                            line_count += 1
                            
                            # Validate required fields
                            required_fields = ["msg_id", "thread_id", "subject", "from", "to", "timestamp"]
                            for field in required_fields:
                                if field not in data:
                                    errors.append(f"{filename}:{line_num} missing required field: {field}")
                            
                            # Validate msg_id format
                            if not data.get("msg_id", "").startswith("MSG-"):
                                errors.append(f"{filename}:{line_num} invalid msg_id format: {data.get('msg_id')}")
                        
                        except json.JSONDecodeError as e:
                            errors.append(f"{filename}:{line_num} invalid JSON: {e}")
                
                # Verify line count matches metadata
                expected_count = file_info.get("message_count", 0)
                if line_count != expected_count:
                    errors.append(f"{filename} has {line_count} messages, expected {expected_count}")
            
            except Exception as e:
                errors.append(f"Error validating email file {filename}: {e}")
        
        return errors

    def _validate_message_format(self, message: Dict[str, Any], filename: str, line_num: int) -> List[str]:
        """Validate individual message format."""
        errors = []
        
        # Check required fields
        required_fields = [
            "msg_id", "thread_id", "subject", "from", "to", "timestamp",
            "body_md", "category", "importance", "spam_score", "refs"
        ]
        
        for field in required_fields:
            if field not in message:
                errors.append(f"{filename}:{line_num} missing required field: {field}")
        
        # Validate field formats
        if "msg_id" in message and not message["msg_id"].startswith("MSG-"):
            errors.append(f"{filename}:{line_num} invalid msg_id format")
        
        if "thread_id" in message and not message["thread_id"].startswith("MAIL-TH-"):
            errors.append(f"{filename}:{line_num} invalid thread_id format")
        
        if "spam_score" in message:
            try:
                score = float(message["spam_score"])
                if not 0 <= score <= 1:
                    errors.append(f"{filename}:{line_num} spam_score must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append(f"{filename}:{line_num} spam_score must be a number")
        
        return errors
