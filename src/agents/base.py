"""Base agent class for CrewAI agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from crewai import Agent, Task
from ..app.logging import LoggerMixin


class BaseAgent(LoggerMixin, ABC):
    """Base class for all CrewAI agents with common functionality."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self.config = config
        self._agent: Agent | None = None

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role of this agent."""
        pass

    @property
    @abstractmethod
    def goal(self) -> str:
        """Return the goal of this agent."""
        pass

    @property
    @abstractmethod
    def backstory(self) -> str:
        """Return the backstory of this agent."""
        pass

    @property
    def agent(self) -> Agent:
        """Get or create the CrewAI agent instance."""
        if self._agent is None:
            self._agent = Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                verbose=self.config.get("verbose", False),
                allow_delegation=False,
                memory=self.config.get("memory", False)
            )
        return self._agent

    @abstractmethod
    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create a CrewAI task for this agent."""
        pass

    def log_execution(self, task_description: str, **kwargs: Any) -> None:
        """Log agent execution."""
        self.logger.info(
            "Agent execution started",
            agent=self.role,
            task=task_description,
            **kwargs
        )

    def log_completion(self, task_description: str, result: Any, **kwargs: Any) -> None:
        """Log agent completion."""
        self.logger.info(
            "Agent execution completed",
            agent=self.role,
            task=task_description,
            result_type=type(result).__name__,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"""
You are a {self.role}.

Goal: {self.goal}

Background: {self.backstory}

Instructions:
- Be concise and deterministic in your outputs
- Focus on synthetic data generation only
- Ensure all outputs are valid and realistic
- Follow the provided schemas and constraints strictly
- Use the context provided to make informed decisions
- Generate content that aligns with the company culture and industry
"""
