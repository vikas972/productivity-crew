"""Single team workflow manager using CrewAI orchestration."""

from typing import Any, Dict, List
from pathlib import Path

try:
    from crewai import Crew
except ImportError:
    from typing import Any
    class Crew:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        def kickoff(self) -> Any:
            pass

from ..app.logging import LoggerMixin
from ..app.settings import ConfigModel, Settings
from ..okg.repo import OKGRepository
from ..okg.validators import BusinessRuleValidator
from ..utils.debug_logger import DebugLogger
from .checkpoint import CheckpointManager, WorkflowStep, create_step_title
from ..agents.industry_selector import IndustrySelectorAgent
from ..agents.org_designer import OrgDesignerAgent
from ..agents.product_director import ProductDirectorAgent
from ..agents.sprint_planner import SprintPlannerAgent
from ..agents.ticket_factory import TicketFactoryAgent
from ..agents.mailbox_generator import MailboxGeneratorAgent
from ..agents.qa_auditor import QAAuditorAgent
from ..agents.export_bundler import ExportBundlerAgent
from ..sources.jira.generator import JiraGenerator
from ..sources.email.generator import EmailGenerator
from ..exporters.json_exporter import JSONExporter
from ..exporters.jsonl_exporter import JSONLExporter


class SingleTeamWorkflowManager(LoggerMixin):
    """Manages the complete workflow for generating single team data."""

    def __init__(self, config: ConfigModel, settings: Settings) -> None:
        """Initialize workflow manager."""
        self.config = config
        self.settings = settings
        self.repo = OKGRepository()
        self.output_dir = settings.ensure_output_dir()
        
        # Initialize checkpoint manager and debug logger
        self.checkpoint_manager = CheckpointManager()
        self.debug_logger = DebugLogger()
        
        # Initialize agents
        agent_config = {
            "verbose": settings.crew_verbose,
            "memory": settings.crew_memory
        }
        
        self.agents = {
            "industry_selector": IndustrySelectorAgent(agent_config),
            "org_designer": OrgDesignerAgent(agent_config),
            "product_director": ProductDirectorAgent(agent_config),
            "sprint_planner": SprintPlannerAgent(agent_config),
            "ticket_factory": TicketFactoryAgent(agent_config),
            "mailbox_generator": MailboxGeneratorAgent(agent_config),
            "qa_auditor": QAAuditorAgent(agent_config),
            "export_bundler": ExportBundlerAgent(agent_config),
        }

    def execute_workflow(self, resume: bool = True, clear_checkpoints: bool = False) -> Dict[str, Any]:
        """Execute the complete workflow and return results."""
        
        # Clear checkpoints if requested
        if clear_checkpoints:
            self.checkpoint_manager.clear_checkpoints()
            self.logger.info("🗑️ Cleared all checkpoints - starting fresh")
        
        # Show progress summary
        self.checkpoint_manager.print_progress()
        
        # Try to resume from checkpoint if available
        checkpoint_data = None
        if resume:
            checkpoint_data = self.checkpoint_manager.load_checkpoint_data()
            if checkpoint_data:
                self._restore_from_checkpoint(checkpoint_data)
                self.logger.info("🔄 Resuming from checkpoint")
        
        self.logger.info("🚀 Starting single team workflow execution")
        
        # Define workflow steps and their execution methods
        workflow_steps = [
            (WorkflowStep.INDUSTRY_SELECTION, self._execute_industry_selection),
            (WorkflowStep.ORG_DESIGN, self._execute_org_design),
            (WorkflowStep.PRODUCT_STRATEGY, self._execute_product_strategy),
            (WorkflowStep.SPRINT_PLANNING, self._execute_sprint_planning),
            (WorkflowStep.TICKET_GENERATION, self._execute_ticket_generation),
            (WorkflowStep.MAILBOX_GENERATION, self._execute_mailbox_generation),
            (WorkflowStep.QA_AUDIT, self._execute_qa_audit),
            (WorkflowStep.EXPORT_BUNDLER, self._execute_export),
        ]
        
        results = {}
        
        try:
            for step, execute_method in workflow_steps:
                # Skip if already completed
                if self.checkpoint_manager.can_resume_from(step):
                    print(create_step_title(step, "SKIPPED"))
                    self.logger.info(f"⏭️ Skipping {step.value} - already completed")
                    continue
                
                # Execute the step
                print(create_step_title(step, "EXECUTING"))
                self.logger.info(f"🔄 Executing {step.value}")
                
                try:
                    step_result = execute_method()
                    results[step.value] = step_result
                    
                    # Save checkpoint
                    repo_state = self._get_repo_state()
                    self.debug_logger.log_repository_state(step.value, repo_state)
                    self.checkpoint_manager.save_step_result(step, step_result, repo_state)
                    
                    print(create_step_title(step, "COMPLETED"))
                    self.logger.info(f"✅ Completed {step.value}")
                    
                except Exception as step_error:
                    error_msg = str(step_error)
                    self.checkpoint_manager.save_step_failure(step, error_msg)
                    
                    print(create_step_title(step, "FAILED"))
                    self.logger.error(f"❌ Failed {step.value}", error=error_msg)
                    
                    raise step_error
            
            # Final summary
            final_results = {
                "workflow_status": "completed",
                **results,
                "summary": {
                    "persons_created": len(self.repo.persons),
                    "tickets_created": len(self.repo.tickets),
                    "emails_generated": self._count_total_emails(),
                    "output_files": results.get("export_bundler", {}).get("files_created", []),
                    "team_members": len(self.repo.persons),
                    "files_created": len(results.get("export_bundler", {}).get("files_created", [])),
                },
                "output_directory": str(self.output_dir)
            }
            
            print("\n" + "="*60)
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"👥 Persons created: {len(self.repo.persons)}")
            print(f"🎫 Tickets created: {len(self.repo.tickets)}")
            print(f"📧 Emails generated: {self._count_total_emails()}")
            print("="*60 + "\n")
            
            self.logger.info("🎉 Workflow completed successfully", 
                           persons=len(self.repo.persons),
                           tickets=len(self.repo.tickets))
            
            return final_results
            
        except Exception as e:
            self.logger.error("❌ Workflow execution failed", error=str(e))
            print(f"\n❌ Workflow failed at step: {str(e)}")
            print("💡 You can resume from the last successful checkpoint by running the command again.")
            raise

    def _execute_industry_selection(self) -> Dict[str, Any]:
        """Execute industry selection phase."""
        self.logger.info("Executing industry selection")
        
        agent = self.agents["industry_selector"]
        task = agent.create_task(
            "Generate company context",
            {
                "industry": self.config.industry,
                "company": self.config.company
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        
        # Extract data from CrewOutput
        result_data = self._extract_crew_output(result, "industry_selection", "industry_selector")
        
        self.logger.info("Industry selection completed")
        return result_data

    def _execute_org_design(self) -> Dict[str, Any]:
        """Execute organization design phase."""
        self.logger.info("Executing organization design")
        
        agent = self.agents["org_designer"]
        task = agent.create_task(
            "Design team structure",
            {
                "org": self.config.org,
                "company_context": self.repo.company_context
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        
        # Process org data into repository
        # CrewAI returns CrewOutput object, extract content
        result_data = self._extract_crew_output(result, "org_design", "org_designer")
        persons = result_data.get("persons", []) if isinstance(result_data, dict) else []
        if isinstance(result_data, list):
            # If result is directly a list of persons
            persons = result_data
        
        for person_data in persons:
            # Convert to Person model and add to repo
            if isinstance(person_data, dict):
                from src.okg.models import Person
                try:
                    person = Person(**person_data)
                    self.repo.add_person(person)
                except Exception as e:
                    self.logger.warning("Failed to create person", person_data=person_data, error=str(e))
        
        self.logger.info("Organization design completed", person_count=len(persons))
        return result_data

    def _execute_product_strategy(self) -> Dict[str, Any]:
        """Execute product strategy phase."""
        self.logger.info("Executing product strategy")
        
        agent = self.agents["product_director"]
        task = agent.create_task(
            "Define product strategy",
            {
                "project": self.config.project,
                "company_context": self.repo.company_context,
                "time_window": self.config.time_window,
                "org": self.config.org
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        
        # Extract data from CrewOutput
        result_data = self._extract_crew_output(result, "product_strategy", "product_director")
        
        self.logger.info("Product strategy completed")
        return result_data

    def _execute_sprint_planning(self) -> Dict[str, Any]:
        """Execute sprint planning phase."""
        self.logger.info("Executing sprint planning")
        
        agent = self.agents["sprint_planner"]
        task = agent.create_task(
            "Plan sprints and ceremonies",
            {
                "project": self.config.project,
                "time_window": self.config.time_window,
                "org": self.config.org
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        
        # Store sprint data
        result_data = self._extract_crew_output(result, "sprint_planning", "sprint_planner")
        self.repo.calendar_templates = result_data.get("calendar_templates", []) if isinstance(result_data, dict) else []
        
        self.logger.info("Sprint planning completed")
        return result_data

    def _execute_ticket_generation(self) -> List[Any]:
        """Execute ticket generation phase."""
        self.logger.info("Executing ticket generation")
        
        agent = self.agents["ticket_factory"]
        task = agent.create_task(
            "Generate realistic tickets",
            {
                "volumes": self.config.volumes,
                "project": self.config.project,
                "epics": [],  # From product strategy
                "sprints": [],  # From sprint planning
                "org": self.config.org,
                "time_window": self.config.time_window
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        result_data = self._extract_crew_output(result, "ticket_generation", "ticket_factory")
        tickets = result_data if isinstance(result_data, list) else (result_data.get("tickets", []) if isinstance(result_data, dict) else [])
        
        # Add tickets to repository
        for ticket_data in tickets:
            # Convert to Ticket model and add
            if isinstance(ticket_data, dict):
                from src.okg.models import Ticket
                try:
                    # Log original ticket data for debugging
                    self.debug_logger.log_transformation_step("ticket_generation", "raw_ticket", ticket_data, None)
                    
                    # Transform AI-generated data to match our Pydantic models
                    transformed_data = self._transform_ticket_data(ticket_data)
                    
                    # Log transformed ticket data
                    self.debug_logger.log_transformation_step("ticket_generation", "transformed_ticket", ticket_data, transformed_data)
                    
                    ticket = Ticket(**transformed_data)
                    self.repo.add_ticket(ticket)
                    self.logger.info("Ticket added successfully", ticket_id=ticket.ticket_id)
                except Exception as e:
                    # Log validation error with detailed context
                    self.debug_logger.log_validation_error("ticket_generation", "Ticket", str(e), ticket_data)
                    self.logger.warning("Failed to create ticket", ticket_data=ticket_data, error=str(e))
        
        self.logger.info("Ticket generation completed", ticket_count=len(tickets))
        return tickets

    def _execute_mailbox_generation(self) -> Dict[str, List[Any]]:
        """Execute mailbox generation phase."""
        self.logger.info("Executing mailbox generation")
        
        agent = self.agents["mailbox_generator"]
        task = agent.create_task(
            "Generate email content",
            {
                "org": self.config.org,
                "persons": list(self.repo.persons.values()),
                "tickets": list(self.repo.tickets.values()),
                "volumes": self.config.volumes,
                "mail": self.config.mail,
                "time_window": self.config.time_window
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        result = crew.kickoff()
        
        # Extract data from CrewOutput
        result_data = self._extract_crew_output(result, "mailbox_generation", "mailbox_generator")
        
        # Ensure mail_data is a proper dictionary
        if isinstance(result_data, dict):
            mail_data = result_data
        else:
            self.logger.warning("Mailbox generation returned non-dict data", data_type=type(result_data), data=str(result_data)[:200])
            mail_data = {}
        
        # Add mail to repository
        if isinstance(mail_data, dict):
            for person_id, messages in mail_data.items():
                if isinstance(messages, list):
                    for i, message in enumerate(messages):
                        # Transform AI-generated message to MailMessage object
                        try:
                            # Log original email data for debugging
                            self.debug_logger.log_transformation_step("mailbox_generation", f"raw_email_{person_id}", message, None)
                            
                            mail_message = self._transform_email_data(person_id, message, i + 1)
                            
                            # Log transformed email data
                            self.debug_logger.log_transformation_step("mailbox_generation", f"transformed_email_{person_id}", message, mail_message.model_dump())
                            
                            self.repo.add_mail_message(person_id, mail_message)
                            self.logger.info("Email added successfully", person_id=person_id, msg_id=mail_message.msg_id)
                        except Exception as e:
                            # Log validation error with detailed context
                            self.debug_logger.log_validation_error("mailbox_generation", "MailMessage", str(e), message)
                            self.logger.warning("Failed to transform email message", error=str(e), person_id=person_id, message=message)
                else:
                    self.logger.warning("Expected list of messages but got", message_type=type(messages), person_id=person_id)
        else:
            self.logger.error("mail_data is not a dictionary", mail_data_type=type(mail_data))
        
        # Calculate total emails safely
        if isinstance(mail_data, dict):
            total_emails = sum(len(msgs) for msgs in mail_data.values() if isinstance(msgs, list))
        else:
            total_emails = 0
            
        self.logger.info("Mailbox generation completed", total_emails=total_emails)
        return mail_data

    def _execute_qa_audit(self) -> Dict[str, Any]:
        """Execute QA audit phase."""
        self.logger.info("Executing QA audit")
        
        # Use business rule validator
        validator = BusinessRuleValidator(self.repo)
        validation_results = validator.get_validation_summary()
        
        # Also run CrewAI QA agent for additional checks
        agent = self.agents["qa_auditor"]
        task = agent.create_task(
            "Audit data quality",
            {
                "okg_data": {
                    "persons": list(self.repo.persons.values()),
                    "tickets": list(self.repo.tickets.values()),
                    "mail_messages": dict(self.repo.mail_messages),
                    "projects": list(self.repo.projects.values()),
                    "epics": list(self.repo.epics.values()),
                    "sprints": list(self.repo.sprints.values())
                }
            }
        )
        
        crew = Crew(
            agents=[agent.agent],
            tasks=[task],
            verbose=self.settings.crew_verbose
        )
        
        agent_result = crew.kickoff()
        
        # Combine validation results
        combined_result = {
            "business_rules": validation_results,
            "agent_audit": agent_result,
            "overall_passed": validation_results["passed"] and self._extract_crew_output(agent_result).get("passed", False) if isinstance(self._extract_crew_output(agent_result), dict) else validation_results["passed"]
        }
        
        self.repo.integrity_report = combined_result
        
        self.logger.info("QA audit completed", passed=combined_result["overall_passed"])
        return combined_result

    def _execute_export(self) -> Dict[str, Any]:
        """Execute export phase."""
        self.logger.info("Executing export")
        
        export_results = {"files_created": []}
        
        # Export Jira data if requested
        if "jira" in self.config.outputs:
            if self.repo.tickets:
                jira_generator = JiraGenerator(self.config, self.output_dir)
                jira_result = jira_generator.generate({
                    "tickets": list(self.repo.tickets.values())
                })
                export_results["jira"] = jira_result
                export_results["files_created"].append(jira_result)
            else:
                self.logger.warning("No tickets available for export, skipping Jira generation")
                export_results["jira"] = {"status": "skipped", "reason": "No tickets available"}
        
        # Export email data if requested
        if "email" in self.config.outputs:
            if self.repo.mail_messages:
                email_generator = EmailGenerator(self.config, self.output_dir)
                email_result = email_generator.generate({
                    "mail_messages": dict(self.repo.mail_messages),
                    "persons": list(self.repo.persons.values())
                })
                export_results["email"] = email_result
                email_data = self._extract_crew_output(email_result)
                export_results["files_created"].extend(email_data.get("files_generated", []) if isinstance(email_data, dict) else [])
            else:
                self.logger.warning("No email messages available for export, skipping email generation")
                export_results["email"] = {"status": "skipped", "reason": "No email messages available"}
        
        # Create index file
        json_exporter = JSONExporter(self.output_dir)
        statistics = self.repo.get_statistics()
        index_result = json_exporter.create_index_file(
            export_results["files_created"],
            statistics
        )
        export_results["index"] = index_result
        export_results["files_created"].append(index_result)
        
        self.logger.info("Export completed", files_created=len(export_results["files_created"]))
        return export_results
    
    def _extract_crew_output(self, crew_result, step_name: str = "unknown", agent_name: str = "unknown") -> Any:
        """Extract usable data from CrewAI output object."""
        import json
        import re
        import ast
        
        # Extract the raw content
        content = None
        if hasattr(crew_result, 'raw'):
            content = crew_result.raw
        elif hasattr(crew_result, 'result'):
            content = crew_result.result
        elif hasattr(crew_result, 'output'):
            content = crew_result.output
        else:
            content = crew_result
            
        # Log the raw output for debugging
        self.debug_logger.log_llm_output(step_name, agent_name, content)
            
        # If content is a string, try to extract JSON/Python literal from it
        if isinstance(content, str):
            # First, try to remove code blocks (```python, ```json, etc.)
            content_cleaned = content
            
            # Extract content from code blocks first
            code_block_pattern = r'```(?:python|json|py)?\s*\n?(.*?)\n?```'
            code_blocks = re.findall(code_block_pattern, content_cleaned, flags=re.DOTALL)
            
            # If no code blocks found, use the whole content
            if not code_blocks:
                code_blocks = [content_cleaned]
            
            # Process each potential code block
            for block in code_blocks:
                # If we found MailMessage constructors, transform them first
                if "MailMessage(" in block:
                    self.debug_logger.log_llm_output(step_name, agent_name, content, None, "Found MailMessage constructors, applying transformation")
                    block = self._transform_constructor_calls_to_dict(block)
                
                # Look for JSON/dict patterns in the content
                json_pattern = r'\{.*\}|\[.*\]'
                matches = re.findall(json_pattern, block, re.DOTALL)
                
                # If we found valid patterns in this block, stop processing
                if matches:
                    content_cleaned = block
                    break
            
            for match in matches:
                # First, try to parse as JSON (double quotes)
                try:
                    # Clean up the JSON before parsing
                    cleaned_json = match.strip()
                    
                    # Remove JavaScript-style comments
                    cleaned_json = re.sub(r'//.*?(?:\n|$)', '', cleaned_json)
                    cleaned_json = re.sub(r'/\*.*?\*/', '', cleaned_json, flags=re.DOTALL)
                    
                    # Remove trailing commas before closing brackets/braces
                    cleaned_json = re.sub(r',(\s*[}\]])', r'\1', cleaned_json)
                    
                    # Handle potential Python-style string literals
                    cleaned_json = re.sub(r'(?<!["\'\\])(True|False|None)\b', lambda m: m.group(1).lower(), cleaned_json)
                    
                    # Try to parse the cleaned JSON
                    try:
                        parsed = json.loads(cleaned_json)
                        self.debug_logger.log_llm_output(step_name, agent_name, content, parsed, "Successfully parsed JSON")
                        return parsed
                    except json.JSONDecodeError as json_error:
                        self.debug_logger.log_llm_output(step_name, agent_name, content, None, f"JSON parsing failed: {json_error}, trying Python literal")
                    # Log successful JSON parsing
                    self.debug_logger.log_llm_output(step_name, agent_name, content, parsed)
                    return parsed
                except json.JSONDecodeError as e:
                    self.debug_logger.log_llm_output(step_name, agent_name, content, None, f"JSON parsing failed: {e}")
                
                # If JSON fails, try to parse as Python literal (single quotes)
                # Clean up Python literal
                cleaned_literal = match.strip()
                
                # Remove comments and clean up the literal
                cleaned_literal = re.sub(r'#.*?(?:\n|$)', '', cleaned_literal)
                cleaned_literal = re.sub(r',(\s*[}\]])', r'\1', cleaned_literal)
                
                # Handle potential string escaping issues
                cleaned_literal = cleaned_literal.replace('\\"', '"').replace("\\'", "'")
                
                try:
                    # Use ast.literal_eval for safe Python literal evaluation
                    parsed = ast.literal_eval(cleaned_literal)
                    self.debug_logger.log_llm_output(step_name, agent_name, content, parsed, "Successfully parsed Python literal")
                    return parsed
                except (ValueError, SyntaxError) as literal_error:
                    self.debug_logger.log_llm_output(step_name, agent_name, content, None, f"Python literal parsing failed: {literal_error}")
                    continue
            
            # If we get here, try one last time with the entire cleaned content
            try:
                if isinstance(content_cleaned, str):
                    parsed = ast.literal_eval(content_cleaned)
                    self.debug_logger.log_llm_output(step_name, agent_name, content, parsed, "Successfully parsed entire content as Python literal")
                    return parsed
            except (ValueError, SyntaxError):
                pass
            
            # If no valid JSON/literal found, return the string as is
            self.debug_logger.log_llm_output(step_name, agent_name, content, None, "No valid JSON/literal patterns found")
            return content
            
        # For non-string content, log and return as-is
        self.debug_logger.log_llm_output(step_name, agent_name, content, content if isinstance(content, (dict, list)) else None)
        return content
    
    def _transform_constructor_calls_to_dict(self, content: str) -> str:
        """Transform Python constructor calls like MailMessage(...) to dict format."""
        import re
        
        # Pattern to match MailMessage constructor calls
        constructor_pattern = r'MailMessage\(([^)]+)\)'
        
        def constructor_to_dict(match):
            """Convert a MailMessage constructor to dict format."""
            args_str = match.group(1)
            
            # Parse the constructor arguments
            # Simple parsing for key=value arguments
            args_dict = {}
            
            # Split by comma, but be careful with nested quotes
            current_arg = ""
            paren_depth = 0
            quote_char = None
            
            for char in args_str + ",":  # Add comma to process last arg
                if char in "\"'" and quote_char is None:
                    quote_char = char
                elif char == quote_char:
                    quote_char = None
                elif char == "(" and quote_char is None:
                    paren_depth += 1
                elif char == ")" and quote_char is None:
                    paren_depth -= 1
                elif char == "," and quote_char is None and paren_depth == 0:
                    # Process the current argument
                    if "=" in current_arg:
                        key, value = current_arg.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        args_dict[key] = value
                    current_arg = ""
                    continue
                
                current_arg += char
            
            # Convert to dict format
            dict_items = []
            for key, value in args_dict.items():
                dict_items.append(f'"{key}": {value}')
            
            return "{" + ", ".join(dict_items) + "}"
        
        # Step 1: Replace MailMessage( with {
        transformed = re.sub(r'MailMessage\s*\(', '{', content, flags=re.MULTILINE | re.DOTALL)
        
        # Step 2: Replace standalone closing parentheses with closing braces
        transformed = re.sub(r'\)\s*(?=,|\]|\}|$)', '}', transformed, flags=re.MULTILINE | re.DOTALL)
        
        # Step 3: Convert key=value to "key": value for valid dict syntax
        transformed = re.sub(r'(\w+)\s*=\s*', r'"\1": ', transformed, flags=re.MULTILINE | re.DOTALL)
        
        return transformed
    
    def _restore_from_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Restore workflow state from checkpoint data."""
        if "repo_state" in checkpoint_data:
            repo_state = checkpoint_data["repo_state"]
            
            # Restore repository state
            if "persons" in repo_state:
                self.repo.persons = repo_state["persons"]
            if "tickets" in repo_state:
                self.repo.tickets = repo_state["tickets"]
            if "company_context" in repo_state:
                self.repo.company_context = repo_state["company_context"]
                
            self.logger.info("🔄 Restored repository state from checkpoint",
                           persons=len(self.repo.persons),
                           tickets=len(self.repo.tickets))
    
    def _get_repo_state(self) -> Dict[str, Any]:
        """Get current repository state for checkpointing."""
        return {
            "persons": self.repo.persons.copy(),
            "tickets": self.repo.tickets.copy(), 
            "company_context": getattr(self.repo, "company_context", None)
        }
    
    def _count_total_emails(self) -> int:
        """Count total emails generated."""
        # Count the total number of email messages in the repository
        try:
            return sum(len(messages) for messages in self.repo.mail_messages.values())
        except Exception:
            return 0
    
    def _transform_ticket_data(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform AI-generated ticket data to match Pydantic model structure."""
        from datetime import datetime
        
        # Create a copy to avoid modifying the original
        transformed = ticket_data.copy()
        
        # Remove fields that are not part of the Pydantic model
        if "status" in transformed:
            del transformed["status"]  # Status is tracked via status_timeline only
        
        # Fix epic_id format (AI uses EPIC-0001, we need EPIC-PAY-001)
        if "epic_id" in transformed and transformed["epic_id"]:
            epic_id = transformed["epic_id"]
            if not epic_id.startswith("EPIC-PAY-"):
                # Convert EPIC-0001 to EPIC-PAY-001
                if epic_id.startswith("EPIC-"):
                    epic_num = epic_id.split("-")[-1]
                    transformed["epic_id"] = f"EPIC-PAY-{epic_num.zfill(3)}"
        
        # Transform status_timeline: convert {status, date} to {status, at}
        # Handle both status_timeline and status_history (AI variations)
        timeline_field = None
        if "status_timeline" in transformed:
            timeline_field = "status_timeline"
        elif "status_history" in transformed:
            timeline_field = "status_history"
        
        if timeline_field:
            timeline = []
            for entry in transformed[timeline_field]:
                if isinstance(entry, dict):
                    # Convert date to at and ensure proper datetime format
                    transformed_entry = {"status": entry.get("status")}
                    if "date" in entry:
                        # Convert date string to datetime
                        date_str = entry["date"]
                        if isinstance(date_str, str):
                            try:
                                # Parse date and convert to datetime with timezone
                                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                transformed_entry["at"] = dt
                            except:
                                # Fallback: use current time
                                transformed_entry["at"] = datetime.now()
                        else:
                            transformed_entry["at"] = datetime.now()
                    timeline.append(transformed_entry)
            transformed["status_timeline"] = timeline
            # Remove the original field if it was status_history
            if timeline_field == "status_history":
                del transformed["status_history"]
        
        # Transform comments: convert {date, comment} to {at, body, author_id}
        if "comments" in transformed:
            comments = []
            for comment in transformed["comments"]:
                if isinstance(comment, dict):
                    transformed_comment = {}
                    
                    # Convert comment/content/text to body
                    if "comment" in comment:
                        transformed_comment["body"] = comment["comment"]
                    elif "content" in comment:
                        transformed_comment["body"] = comment["content"]
                    elif "text" in comment:
                        transformed_comment["body"] = comment["text"]
                    
                    # Convert date to at
                    if "date" in comment:
                        date_str = comment["date"]
                        if isinstance(date_str, str):
                            try:
                                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                transformed_comment["at"] = dt
                            except:
                                transformed_comment["at"] = datetime.now()
                        else:
                            transformed_comment["at"] = datetime.now()
                    
                                        # Add author_id - convert from AI's "author" field or use fallback
                    if "author" in comment:
                        transformed_comment["author_id"] = self._normalize_person_id(comment["author"])
                    elif transformed.get("assignee_id"):
                        # Use assignee_id as fallback
                        transformed_comment["author_id"] = self._normalize_person_id(transformed["assignee_id"])
                    else:
                        transformed_comment["author_id"] = "PER-0001"  # Final fallback
                        
                    comments.append(transformed_comment)
            transformed["comments"] = comments
        
        # Transform attachments: convert various formats to Attachment objects
        if "attachments" in transformed and isinstance(transformed["attachments"], list):
            attachments = []
            for attachment in transformed["attachments"]:
                if isinstance(attachment, str):
                    # Convert string filename to Attachment object (only name and url fields allowed)
                    filename = attachment.split("/")[-1]  # Get filename from path
                    attachments.append({
                        "name": filename,
                        "url": f"https://example.com/attachments/{attachment}"
                    })
                elif isinstance(attachment, dict):
                    # Handle AI-generated format: {"type": "document", "name": "file.pdf"}
                    if "type" in attachment and "name" in attachment:
                        # AI-generated format - convert to our model format (only name and url fields)
                        filename = attachment["name"]
                        attachments.append({
                            "name": filename,
                            "url": f"https://example.com/attachments/{filename}"
                        })
                    elif "filename" in attachment:
                        # Already in our format or close to it (only keep name and url fields)
                        filename = attachment.get("filename", "unknown.file")
                        fixed_attachment = {
                            "name": attachment.get("name", filename.split("/")[-1]),
                            "url": attachment.get("url", f"https://example.com/attachments/{filename}")
                        }
                        attachments.append(fixed_attachment)
                    else:
                        # Unknown format, skip
                        self.logger.warning("Unknown attachment format", attachment=attachment)
            transformed["attachments"] = attachments
        
        # Ensure attachments field exists (required by model)
        if "attachments" not in transformed:
            transformed["attachments"] = []
        
        # Fix ID patterns to match our regex patterns
        # Convert TL-001, DEV-002 etc to PER-0001, PER-0002 format
        if "reporter_id" in transformed:
            transformed["reporter_id"] = self._normalize_person_id(transformed["reporter_id"])
        
        if "assignee_id" in transformed:
            transformed["assignee_id"] = self._normalize_person_id(transformed["assignee_id"])
        
        # Fix epic_id pattern: PAY-EPIC-1 -> EPIC-PAY-0001
        if "epic_id" in transformed and transformed["epic_id"]:
            epic_id = transformed["epic_id"]
            if isinstance(epic_id, str) and not epic_id.startswith("EPIC-"):
                # Convert PAY-EPIC-1 to EPIC-PAY-0001
                parts = epic_id.split("-")
                if len(parts) >= 3:
                    project = parts[0]  # PAY
                    num = parts[-1]     # 1
                    transformed["epic_id"] = f"EPIC-{project}-{num.zfill(4)}"
        
        return transformed
    
    def _normalize_person_id(self, person_id: str) -> str:
        """Convert various person ID formats to PER-0001 format."""
        if not isinstance(person_id, str):
            return "PER-0001"
        
        # If already in correct format, return as-is
        if person_id.startswith("PER-") and len(person_id) == 8:
            return person_id
        
        # Extract number from various formats
        import re
        match = re.search(r'(\d+)', person_id)
        if match:
            num = int(match.group(1))
            return f"PER-{num:04d}"
        
        # Fallback
        return "PER-0001"
    
    def _get_mime_type_from_extension(self, filename: str) -> str:
        """Get MIME type based on file extension."""
        extension = filename.lower().split(".")[-1] if "." in filename else ""
        
        mime_types = {
            "pdf": "application/pdf",
            "doc": "application/msword", 
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "json": "application/json",
            "xml": "application/xml",
            "log": "text/plain"
        }
        
        return mime_types.get(extension, "application/octet-stream")

    def _transform_email_data(self, person_id: str, email_data: Dict[str, Any], msg_number: int) -> Any:
        """Transform AI-generated email data to MailMessage object."""
        from src.okg.models import MailMessage, MailRefs
        from datetime import datetime
        import re
        
        # Generate unique IDs
        msg_id = f"MSG-{msg_number:03d}"
        thread_id = f"MAIL-TH-{msg_number:03d}"
        
        # Get person info for from_ field
        person = self.repo.persons.get(person_id)
        company_name = self.config.company.get('name', 'Company').lower().replace(' ', '')
        if person:
            from_email = f"{person.name.lower().replace(' ', '.')}@{company_name}.com"
        else:
            from_email = f"{person_id.lower()}@{company_name}.com"
        
        # Default to_ field (team email)
        team_name = self.config.org.get('team_name', 'Team').lower().replace(' ', '-')
        to = [f"{team_name}@{company_name}.com"]
        
        # Parse timestamp if provided, otherwise use default
        timestamp = datetime.now()
        if isinstance(email_data.get('timestamp'), str):
            try:
                # Handle various timestamp formats
                timestamp_str = email_data['timestamp']
                if '+' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = datetime.fromisoformat(timestamp_str + '+05:30')  # Add IST timezone
            except:
                timestamp = datetime.now()
        
        # Extract ticket references from subject
        subject = email_data.get('subject', 'No Subject')
        ticket_ids = []
        ticket_pattern = r'\[PAY-\d+\]'
        matches = re.findall(ticket_pattern, subject)
        for match in matches:
            ticket_id = match[1:-1]  # Remove brackets
            ticket_ids.append(ticket_id)
        
        # Create MailRefs object
        refs = MailRefs(ticket_ids=ticket_ids)
        
        # Convert body to markdown format
        body_md = email_data.get('body', '').replace('\\n', '\n')
        
        # Determine category based on content
        category = "work"  # Default category
        if 'hr' in subject.lower() or 'hr' in body_md.lower():
            category = "hr"
        elif 'corporate' in subject.lower() or 'announcement' in body_md.lower():
            category = "corporate"
        elif 'vendor' in subject.lower() or 'procurement' in body_md.lower():
            category = "vendor"
        elif 'security' in subject.lower() or 'phishing' in body_md.lower():
            category = "security"
        elif 'event' in subject.lower() or 'meeting' in body_md.lower():
            category = "event"
        elif any(word in subject.lower() for word in ['1:1', 'performance', 'review', 'feedback']):
            category = "managerial"
        
        # Handle attachments if present
        attachments = []
        if 'attachments' in email_data and isinstance(email_data['attachments'], list):
            attachments = [str(att) for att in email_data['attachments']]
        
        # Create MailMessage object
        mail_message = MailMessage(
            msg_id=msg_id,
            thread_id=thread_id,
            subject=subject,
            from_=from_email,
            to=to,
            timestamp=timestamp,
            body_md=body_md,
            attachments=attachments,
            category=category,
            refs=refs
        )
        
        return mail_message
