"""Fintech SaaS industry pack with domain-specific content."""

from typing import Dict, List, Any


class FintechSaaSPack:
    """Industry-specific content pack for Fintech SaaS companies."""

    @staticmethod
    def get_products() -> List[str]:
        """Get typical Fintech SaaS products."""
        return [
            "Digital Payment Gateway",
            "KYC Verification Platform",
            "Fraud Detection Engine",
            "SME Banking API Suite",
            "Transaction Monitoring Dashboard"
        ]

    @staticmethod
    def get_constraints() -> List[str]:
        """Get industry-specific constraints."""
        return [
            "RBI compliance requirements",
            "PCI DSS security standards",
            "Real-time transaction processing demands",
            "99.9% uptime SLA requirements",
            "Multi-currency support complexity"
        ]

    @staticmethod
    def get_tech_stack() -> Dict[str, List[str]]:
        """Get preferred technology stack."""
        return {
            "backend": ["Java", "Spring Boot", "Python", "Node.js"],
            "frontend": ["React", "TypeScript", "Next.js"],
            "databases": ["PostgreSQL", "MongoDB", "Redis", "ClickHouse"],
            "infrastructure": ["AWS", "Kubernetes", "Docker", "Terraform"],
            "monitoring": ["Prometheus", "Grafana", "ELK Stack", "Jaeger"],
            "security": ["Vault", "OAuth 2.0", "JWT", "SSL/TLS"],
            "payment": ["Razorpay", "PayU", "Paytm", "UPI APIs"]
        }

    @staticmethod
    def get_communication_style() -> Dict[str, Any]:
        """Get communication style guidelines."""
        return {
            "tone": "professional, data-driven, compliance-aware",
            "formality": "medium-formal",
            "technical_depth": "high",
            "compliance_mentions": "frequent",
            "customer_focus": "SME and enterprise",
            "urgency_indicators": ["payment failure", "fraud alert", "compliance issue"],
            "common_metrics": ["TPS", "success rate", "latency", "fraud rate", "uptime"]
        }

    @staticmethod
    def get_typical_tickets() -> List[Dict[str, Any]]:
        """Get domain-specific ticket templates."""
        return [
            {
                "type": "Story",
                "title_pattern": "Implement {feature} for {payment_method}",
                "features": ["webhook validation", "retry mechanism", "rate limiting", "fraud scoring"],
                "payment_methods": ["UPI", "Net Banking", "Credit Card", "Wallet"]
            },
            {
                "type": "Bug",
                "title_pattern": "Fix {issue} in {component}",
                "issues": ["timeout handling", "validation error", "callback failure", "status mismatch"],
                "components": ["payment gateway", "KYC service", "notification service", "dashboard"]
            },
            {
                "type": "Task",
                "title_pattern": "Configure {task} for {environment}",
                "tasks": ["monitoring alerts", "backup strategy", "security policies", "compliance audit"],
                "environments": ["production", "staging", "sandbox", "compliance env"]
            }
        ]

    @staticmethod
    def get_email_topics() -> Dict[str, List[str]]:
        """Get domain-specific email topics."""
        return {
            "work": [
                "Payment gateway integration",
                "KYC verification process",
                "Fraud detection rules",
                "API rate limiting",
                "Transaction reconciliation",
                "Security vulnerability assessment",
                "Performance optimization",
                "Compliance documentation"
            ],
            "customer": [
                "Payment failure investigation",
                "Integration support request",
                "API documentation query",
                "Compliance requirement clarification",
                "Feature request discussion"
            ],
            "vendor": [
                "Banking partner API updates",
                "Security audit scheduling",
                "Compliance tool procurement",
                "Infrastructure scaling discussion",
                "Third-party service integration"
            ],
            "security": [
                "Fraud alert investigation",
                "Security incident response",
                "Compliance audit findings",
                "Penetration testing results",
                "Data privacy assessment"
            ]
        }

    @staticmethod
    def get_jargon() -> List[str]:
        """Get industry-specific terminology."""
        return [
            "TPS", "PCI DSS", "KYC", "AML", "UPI", "IMPS", "NEFT", "RTGS",
            "webhook", "callback", "settlement", "reconciliation", "chargeback",
            "acquirer", "issuer", "interchange", "MDR", "tokenization",
            "3DS", "OTP", "PIN", "CVV", "fraud scoring", "risk assessment"
        ]

    @staticmethod
    def get_compliance_keywords() -> List[str]:
        """Get compliance-related keywords."""
        return [
            "RBI guidelines", "PCI compliance", "data retention", "audit trail",
            "encryption standards", "access controls", "incident reporting",
            "regulatory approval", "license requirements", "risk assessment"
        ]

    @staticmethod
    def get_performance_metrics() -> List[str]:
        """Get key performance indicators."""
        return [
            "Transaction success rate", "Payment latency", "API response time",
            "System uptime", "Fraud detection rate", "False positive rate",
            "Customer onboarding time", "Settlement accuracy", "Dispute resolution time"
        ]
