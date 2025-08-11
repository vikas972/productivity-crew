"""CLI interface for the productivity crew application."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..app.settings import load_settings, load_config
from ..app.logging import configure_logging, get_logger
from ..workflows.single_team_manager import SingleTeamWorkflowManager

app = typer.Typer(
    name="productivity-crew",
    help="Production-ready multi-agent CrewAI application for generating synthetic Jira tickets and emails"
)
console = Console()
logger = get_logger(__name__)


@app.command()
def generate(
    config: str = typer.Option(
        "configs/single_team_fintech.yaml",
        "--config",
        "-c",
        help="Path to YAML configuration file"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--out",
        "-o",
        help="Output directory (default: from config or 'out')"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate configuration without generating data"
    ),
    no_resume: bool = typer.Option(
        False,
        "--no-resume",
        help="Start fresh without resuming from checkpoints"
    ),
    clear_checkpoints: bool = typer.Option(
        False,
        "--clear-checkpoints",
        help="Clear all checkpoints and start fresh"
    )
) -> None:
    """Generate synthetic Jira tickets and emails for a team."""
    
    try:
        # Load settings
        settings = load_settings()
        
        # Override output directory if provided
        if output_dir:
            settings.output_dir = output_dir
        
        # Configure logging
        log_level = "DEBUG" if verbose else settings.log_level
        configure_logging(log_level, settings.log_format)
        
        logger.info(
            "Starting productivity crew generation",
            config_file=config,
            output_dir=settings.output_dir,
            dry_run=dry_run
        )
        
        # Load and validate configuration
        config_path = Path(config)
        if not config_path.exists():
            console.print(f"❌ Configuration file not found: {config}", style="red")
            raise typer.Exit(1)
        
        try:
            config_obj = load_config(str(config_path))
        except Exception as e:
            console.print(f"❌ Error loading configuration: {e}", style="red")
            raise typer.Exit(1)
        
        # Validate configuration
        validation_errors = config_obj.validate_config()
        if validation_errors:
            console.print("❌ Configuration validation failed:", style="red")
            for error in validation_errors:
                console.print(f"  • {error}", style="red")
            raise typer.Exit(1)
        
        console.print("✅ Configuration loaded and validated", style="green")
        
        if dry_run:
            console.print("🔍 Dry run mode - configuration is valid", style="blue")
            _display_config_summary(config_obj)
            return
        
        # Execute workflow
        workflow_manager = SingleTeamWorkflowManager(config_obj, settings)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("Generating synthetic data...", total=None)
            
            try:
                # Configure resume/checkpoint options
                resume = not no_resume
                result = workflow_manager.execute_workflow(
                    resume=resume,
                    clear_checkpoints=clear_checkpoints
                )
                progress.remove_task(task)
                
                # Display results
                _display_results(result)
                
                # Check for validation failures
                integrity_report = result.get("integrity_report", {})
                if not integrity_report.get("overall_passed", False):
                    console.print("⚠️  Data validation warnings detected", style="yellow")
                    _display_validation_issues(integrity_report)
                
                console.print("✅ Generation completed successfully!", style="green")
                
            except Exception as e:
                progress.remove_task(task)
                console.print(f"❌ Generation failed: {e}", style="red")
                logger.error("Workflow execution failed", error=str(e))
                raise typer.Exit(1)
                
    except KeyboardInterrupt:
        console.print("\n⏹️  Generation cancelled by user", style="yellow")
        raise typer.Exit(130)
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        console.print(f"❌ Unexpected error: {e}", style="red")
        raise typer.Exit(1)


def _display_config_summary(config) -> None:
    """Display configuration summary."""
    table = Table(title="Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Industry", config.industry)
    table.add_row("Company", config.company["name"])
    table.add_row("Team", config.org["team_name"])
    table.add_row("Project Key", config.project["key"])
    table.add_row("Time Window", f"{config.time_window['start']} to {config.time_window['end']}")
    table.add_row("Outputs", ", ".join(config.outputs))
    
    # Volume estimates
    ticket_range = config.volumes["jira_tickets_in_window"]
    email_range = config.volumes["emails_per_person_per_week"]
    table.add_row("Tickets", f"{ticket_range['min']}-{ticket_range['max']}")
    table.add_row("Emails/person/week", f"{email_range['min']}-{email_range['max']}")
    
    console.print(table)


def _display_results(result: dict) -> None:
    """Display generation results."""
    table = Table(title="Generation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="white", justify="right")
    
    table.add_row("Team Members", str(result.get("org_data", {}).get("person_count", 0)))
    table.add_row("Tickets Generated", str(result.get("tickets_generated", 0)))
    table.add_row("Emails Generated", str(result.get("emails_generated", 0)))
    table.add_row("Files Created", str(len(result.get("export_results", {}).get("files_created", []))))
    
    console.print(table)
    
    # Display file list
    files_created = result.get("export_results", {}).get("files_created", [])
    if files_created:
        console.print("\n📁 Generated Files:", style="bold")
        for file_info in files_created:
            filename = file_info.get("filename", "unknown")
            size_kb = file_info.get("file_size_bytes", 0) / 1024
            console.print(f"  • {filename} ({size_kb:.1f} KB)")


def _display_validation_issues(integrity_report: dict) -> None:
    """Display validation issues if any."""
    business_rules = integrity_report.get("business_rules", {})
    
    if business_rules.get("detailed_errors"):
        console.print("\n⚠️  Validation Issues:", style="yellow")
        
        for category, errors in business_rules["detailed_errors"].items():
            if errors:
                console.print(f"\n{category.replace('_', ' ').title()}:", style="bold yellow")
                for error in errors[:5]:  # Show max 5 errors per category
                    console.print(f"  • {error}")
                if len(errors) > 5:
                    console.print(f"  ... and {len(errors) - 5} more")


@app.command()
def status() -> None:
    """Show current workflow progress and checkpoint status."""
    from ..workflows.checkpoint import CheckpointManager
    
    checkpoint_manager = CheckpointManager()
    checkpoint_manager.print_progress()
    
    # Show next step info
    next_step = checkpoint_manager.get_next_step()
    if next_step:
        console.print(f"\n📋 Next step to execute: {next_step.value.replace('_', ' ').title()}", style="blue")
    else:
        console.print("\n🎉 All workflow steps completed!", style="green")


@app.command()
def clear() -> None:
    """Clear all checkpoints and start fresh."""
    from ..workflows.checkpoint import CheckpointManager
    
    checkpoint_manager = CheckpointManager()
    checkpoint_manager.clear_checkpoints()
    console.print("🗑️ All checkpoints cleared. Next run will start fresh.", style="green")


@app.command()
def debug() -> None:
    """Show debug session summary and LLM output logs."""
    from ..utils.debug_logger import DebugLogger
    
    debug_logger = DebugLogger()
    summary = debug_logger.get_session_summary()
    
    console.print("\n📝 DEBUG SESSION SUMMARY", style="bold blue")
    console.print("=" * 60)
    console.print(summary)
    console.print("=" * 60)
    console.print("\n💡 Tip: Check the debug log files for detailed LLM outputs and transformation steps.", style="yellow")


@app.command()
def validate(
    config: str = typer.Option(
        "configs/single_team_fintech.yaml",
        "--config",
        "-c",
        help="Path to YAML configuration file"
    )
) -> None:
    """Validate configuration file without generating data."""
    generate(config=config, dry_run=True)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("Productivity Crew v1.0.0", style="bold blue")
    console.print("Production-ready multi-agent CrewAI application")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
