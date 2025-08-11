"""Registry for industry-specific content packs."""

from typing import Dict, Type, Any

from .fintech_saas import FintechSaaSPack


class IndustryPackRegistry:
    """Registry for managing industry-specific content packs."""

    def __init__(self) -> None:
        """Initialize with available industry packs."""
        self._packs: Dict[str, Type] = {
            "Fintech SaaS": FintechSaaSPack,
            "fintech": FintechSaaSPack,  # alias
            "fintech_saas": FintechSaaSPack,  # alias
        }

    def get_pack(self, industry: str):
        """Get industry pack by name."""
        pack_class = self._packs.get(industry)
        if not pack_class:
            # Return a default/generic pack
            return self._get_generic_pack()
        return pack_class()

    def _get_generic_pack(self):
        """Return a generic industry pack for unknown industries."""
        class GenericPack:
            @staticmethod
            def get_products():
                return ["Software Platform", "API Service", "Data Analytics", "Web Application"]
            
            @staticmethod
            def get_constraints():
                return ["Security requirements", "Scalability needs", "Performance targets", "Budget limitations"]
            
            @staticmethod
            def get_tech_stack():
                return {
                    "backend": ["Python", "Java", "Node.js"],
                    "frontend": ["React", "Vue.js", "Angular"],
                    "databases": ["PostgreSQL", "MongoDB", "Redis"],
                    "infrastructure": ["AWS", "Docker", "Kubernetes"],
                    "monitoring": ["Prometheus", "Grafana", "ELK Stack"]
                }
            
            @staticmethod
            def get_communication_style():
                return {
                    "tone": "professional, collaborative",
                    "formality": "medium",
                    "technical_depth": "medium",
                    "common_metrics": ["performance", "reliability", "user satisfaction"]
                }
            
            @staticmethod
            def get_typical_tickets():
                return [
                    {
                        "type": "Story",
                        "title_pattern": "Implement {feature}",
                        "features": ["user authentication", "data export", "search functionality", "reporting"]
                    },
                    {
                        "type": "Bug",
                        "title_pattern": "Fix {issue}",
                        "issues": ["performance issue", "UI bug", "data inconsistency", "error handling"]
                    }
                ]
            
            @staticmethod
            def get_email_topics():
                return {
                    "work": ["feature development", "bug fixes", "code review", "testing"],
                    "customer": ["support request", "feature request", "bug report"],
                    "vendor": ["tool integration", "service discussion"]
                }
            
            @staticmethod
            def get_jargon():
                return ["API", "UI/UX", "backend", "frontend", "database", "deployment", "testing"]
            
            @staticmethod
            def get_compliance_keywords():
                return ["security", "privacy", "data protection", "access control"]
            
            @staticmethod
            def get_performance_metrics():
                return ["response time", "uptime", "user engagement", "error rate"]
        
        return GenericPack()

    def register_pack(self, industry: str, pack_class: Type) -> None:
        """Register a custom industry pack."""
        self._packs[industry] = pack_class

    def get_available_industries(self) -> list[str]:
        """Get list of available industry names."""
        return list(self._packs.keys())

    def get_industry_context(self, industry: str) -> Dict[str, Any]:
        """Get comprehensive industry context."""
        pack = self.get_pack(industry)
        
        return {
            "industry": industry,
            "products": pack.get_products(),
            "constraints": pack.get_constraints(),
            "tech_stack": pack.get_tech_stack(),
            "communication_style": pack.get_communication_style(),
            "typical_tickets": pack.get_typical_tickets(),
            "email_topics": pack.get_email_topics(),
            "jargon": pack.get_jargon(),
            "compliance_keywords": pack.get_compliance_keywords(),
            "performance_metrics": pack.get_performance_metrics()
        }
