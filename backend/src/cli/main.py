"""
CLI interface for LinkedIn AI Agent.

Interactive command-line tool for generating LinkedIn posts.
Supports both basic mode and enhanced mode with agent thought tracking.
"""

import asyncio
import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.orchestration import run_generation, continue_generation

console = Console()


async def main_basic():
    """Basic CLI entry point (original behavior)."""
    console.print(Panel.fit(
        "[bold blue]LinkedIn AI Agent[/bold blue]\n"
        "Transform your ideas into viral LinkedIn posts",
        border_style="blue"
    ))
    
    # Get idea from user
    idea = Prompt.ask("\n[bold]Enter your post idea[/bold]")
    
    if not idea:
        console.print("[red]No idea provided. Exiting.[/red]")
        return
    
    console.print("\n[yellow]🔄 Processing your idea...[/yellow]")
    
    # Run initial generation
    state = await run_generation(raw_idea=idea)
    
    # Check for rejection
    validator_out = state.get("validator_output", {})
    if validator_out.get("decision") == "REJECT":
        console.print(Panel(
            f"[red]Idea Rejected[/red]\n\n"
            f"Reason: {validator_out.get('reasoning')}\n\n"
            f"Suggestions:\n" + "\n".join(f"• {s}" for s in validator_out.get('refinement_suggestions', [])),
            title="❌ Validation Failed",
            border_style="red"
        ))
        return
    
    # Show clarifying questions
    questions = state.get("clarifying_questions", [])
    if questions:
        console.print("\n[bold cyan]📝 Please answer these questions:[/bold cyan]\n")
        
        answers = {}
        for q in questions:
            console.print(f"[dim]{q.get('rationale', '')}[/dim]")
            answer = Prompt.ask(f"[bold]{q['question']}[/bold]")
            answers[q['question_id']] = answer
            console.print()
        
        console.print("[yellow]🔄 Generating content...[/yellow]")
        state = await continue_generation(state, answers)
    
    # Show final post
    final_post = state.get("final_post", {})
    
    if final_post:
        hook = final_post.get("hook", {})
        body = final_post.get("body", "")
        cta = final_post.get("cta", "")
        
        full_content = f"{hook.get('text', '')}\n\n{body}\n\n{cta}"
        
        console.print(Panel(
            full_content,
            title="✨ Your LinkedIn Post",
            border_style="green"
        ))
        
        # Show stats
        optimizer = state.get("optimizer_output", {})
        console.print(f"\n[bold]Quality Score:[/bold] {optimizer.get('quality_score', 0)}/10")
        console.print(f"[bold]Predicted Impressions:[/bold] {optimizer.get('predicted_impressions_min', 0):,} - {optimizer.get('predicted_impressions_max', 0):,}")
        
        # Show hashtags
        hashtags = final_post.get("hashtags", [])
        if hashtags:
            console.print(f"\n[bold]Hashtags:[/bold] {' '.join('#' + h for h in hashtags)}")
        
        # Save option
        if Prompt.ask("\n[bold]Save to file?[/bold]", choices=["y", "n"], default="n") == "y":
            filename = f"linkedin_post_{state.get('post_id', 'output')}.txt"
            with open(filename, "w") as f:
                f.write(full_content)
            console.print(f"[green]✓ Saved to {filename}[/green]")
    
    console.print("\n[dim]Thank you for using LinkedIn AI Agent![/dim]")


def run():
    """Run the CLI with mode selection."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--enhanced", "-e"]:
            from src.cli.enhanced import run as run_enhanced
            run_enhanced()
            return
        elif sys.argv[1] in ["--help", "-h"]:
            console.print(Panel.fit(
                "[bold]LinkedIn AI Agent CLI[/bold]\n\n"
                "[cyan]Usage:[/cyan]\n"
                "  python -m src.cli.main           Run in basic mode\n"
                "  python -m src.cli.main --enhanced  Run with agent thoughts display\n"
                "  python -m src.cli.main -e         Shortcut for enhanced mode\n\n"
                "[cyan]Modes:[/cyan]\n"
                "  [green]Basic Mode[/green] - Simple, fast output\n"
                "  [magenta]Enhanced Mode[/magenta] - See what each agent is thinking",
                border_style="blue"
            ))
            return
    
    # Interactive mode selection
    console.print(Panel.fit(
        "[bold blue]LinkedIn AI Agent[/bold blue]\n"
        "Transform your ideas into viral LinkedIn posts",
        border_style="blue"
    ))
    
    console.print("\n[bold]Select mode:[/bold]")
    console.print("  [1] [green]Basic Mode[/green] - Simple and fast")
    console.print("  [2] [magenta]Enhanced Mode[/magenta] - See agent thoughts in real-time")
    
    choice = Prompt.ask("\n[bold]Enter choice[/bold]", choices=["1", "2"], default="2")
    
    if choice == "2":
        from src.cli.enhanced import run as run_enhanced
        run_enhanced()
    else:
        asyncio.run(main_basic())


if __name__ == "__main__":
    run()

