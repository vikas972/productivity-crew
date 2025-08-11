"""Privacy and redaction utilities for production-like data handling."""

import re
from typing import Any, Dict


class ProductionRedactor:
    """Handles redaction of sensitive information from generated content."""

    def __init__(self) -> None:
        """Initialize redaction patterns."""
        self.patterns = {
            # Email addresses (partial redaction)
            'email': re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
            
            # Phone numbers
            'phone': re.compile(r'(\+91|0)?[\s-]?[6-9]\d{2}[\s-]?\d{3}[\s-]?\d{4}'),
            
            # Credit card numbers
            'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            
            # Account numbers
            'account': re.compile(r'\b\d{10,16}\b'),
            
            # API keys (simple pattern)
            'api_key': re.compile(r'\b[A-Za-z0-9]{32,}\b'),
            
            # URLs with sensitive paths
            'sensitive_url': re.compile(r'https?://[^\s]+/(api|admin|private|internal)[^\s]*'),
        }

    def redact_email(self, email: str) -> str:
        """Redact email address partially."""
        match = self.patterns['email'].match(email)
        if match:
            local, domain = match.groups()
            if len(local) > 2:
                redacted_local = local[:2] + '*' * (len(local) - 2)
            else:
                redacted_local = local[0] + '*'
            return f"{redacted_local}@{domain}"
        return email

    def redact_phone(self, phone: str) -> str:
        """Redact phone number."""
        return re.sub(r'\d', '*', phone[-4:])  # Keep only last 4 digits pattern

    def redact_sensitive_content(self, content: str) -> str:
        """Apply redaction to sensitive content in text."""
        redacted = content
        
        # Redact emails
        redacted = self.patterns['email'].sub(
            lambda m: self.redact_email(m.group(0)), redacted
        )
        
        # Redact phone numbers
        redacted = self.patterns['phone'].sub('[PHONE_REDACTED]', redacted)
        
        # Redact credit cards
        redacted = self.patterns['credit_card'].sub('[CARD_REDACTED]', redacted)
        
        # Redact account numbers
        redacted = self.patterns['account'].sub('[ACCOUNT_REDACTED]', redacted)
        
        # Redact API keys
        redacted = self.patterns['api_key'].sub('[API_KEY_REDACTED]', redacted)
        
        # Redact sensitive URLs
        redacted = self.patterns['sensitive_url'].sub('[URL_REDACTED]', redacted)
        
        return redacted

    def sanitize_for_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data structure for export."""
        if isinstance(data, dict):
            return {k: self.sanitize_for_export(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_for_export(item) for item in data]
        elif isinstance(data, str):
            return self.redact_sensitive_content(data)
        else:
            return data

    def apply_synthetic_markers(self, content: str) -> str:
        """Add markers to indicate synthetic content."""
        markers = [
            "# SYNTHETIC DATA - NOT FOR PRODUCTION USE",
            "# Generated for testing and development purposes only",
        ]
        
        if content.strip():
            return "\n".join(markers) + "\n\n" + content
        return content
