"""
Enhanced CLI interface for LinkedIn AI Agent.

Interactive command-line tool with real-time agent thought display.
Shows detailed output from each agent as they execute.
"""

import asyncio
import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.tree import Tree

from src.orchestration import (
    run_generation_with_tracking,
    continue_generation_with_tracking,
    get_tracker,
    remove_tracker,
    AgentEvent,
)

console = Console()

# Emoji indicators for each agent
AGENT_EMOJIS = {
    "validator": "🔍",
    "strategist": "📋",
    "writer": "✍️",
    "visual": "🎨",
    "optimizer": "📊",
    "system": "⚙️",
}

# Colors for each agent
AGENT_COLORS = {
    "validator": "cyan",
    "strategist": "magenta",
    "writer": "green",
    "visual": "yellow",
    "optimizer": "blue",
    "system": "white",
}


def display_agent_output(agent_name: str, output: dict, summary: str):
    """Display agent output in a formatted panel."""
    emoji = AGENT_EMOJIS.get(agent_name, "🤖")
    color = AGENT_COLORS.get(agent_name, "white")
    
    # Create the content
    content = Text()
    content.append(f"{summary}\n\n", style="bold")
    
    # Add specific details based on agent type
    if agent_name == "validator":
        decision = output.get("decision", "UNKNOWN")
        decision_color = "green" if decision == "APPROVE" else "yellow" if decision == "REFINE" else "red"
        content.append(f"Decision: ", style="dim")
        content.append(f"{decision}\n", style=f"bold {decision_color}")
        content.append(f"Quality Score: ", style="dim")
        content.append(f"{output.get('quality_score', 0)}/10\n", style="bold")
        content.append(f"Brand Alignment: ", style="dim")
        content.append(f"{output.get('brand_alignment_score', 0)}/10\n", style="bold")
        
        if output.get("concerns"):
            content.append("\nConcerns:\n", style="dim italic")
            for concern in output.get("concerns", []):
                content.append(f"  • {concern}\n", style="yellow")
        
        if output.get("refinement_suggestions"):
            content.append("\nSuggestions:\n", style="dim italic")
            for suggestion in output.get("refinement_suggestions", []):
                content.append(f"  → {suggestion}\n", style="cyan")
    
    elif agent_name == "strategist":
        content.append(f"Format: ", style="dim")
        content.append(f"{output.get('recommended_format', 'text')}\n", style="bold cyan")
        content.append(f"Structure: ", style="dim")
        content.append(f"{output.get('structure_type', 'unknown')}\n", style="bold")
        content.append(f"Tone: ", style="dim")
        content.append(f"{output.get('tone', 'conversational')}\n", style="bold")
        
        if output.get("psychological_triggers"):
            content.append("\nPsychological Triggers:\n", style="dim italic")
            for trigger in output.get("psychological_triggers", []):
                content.append(f"  🧠 {trigger}\n", style="magenta")
        
        if output.get("hook_types"):
            content.append("\nHook Types:\n", style="dim italic")
            for hook in output.get("hook_types", []):
                content.append(f"  🪝 {hook}\n", style="green")
    
    elif agent_name == "writer":
        hooks = output.get("hooks", [])
        content.append(f"Generated {len(hooks)} hook variations:\n\n", style="dim")
        
        for i, hook in enumerate(hooks[:3], 1):
            score = hook.get("score", 0)
            score_color = "green" if score >= 8 else "yellow" if score >= 6 else "red"
            content.append(f"Hook {i} ", style="bold")
            content.append(f"(Score: {score}/10)\n", style=score_color)
            content.append(f'  "{hook.get("text", "")}"\n\n', style="italic")
        
        content.append(f"Hashtags: ", style="dim")
        hashtags = output.get("hashtags", [])
        content.append(f"{' '.join('#' + h for h in hashtags)}\n", style="blue")
    
    elif agent_name == "visual":
        specs = output if "total_slides" in output else output.get("visual_specs", {})
        content.append(f"Total Slides: ", style="dim")
        content.append(f"{specs.get('total_slides', 0)}\n", style="bold")
        content.append(f"Style: ", style="dim")
        content.append(f"{specs.get('overall_style', 'default')}\n", style="bold")
        
        if specs.get("slides"):
            content.append("\nSlide Headlines:\n", style="dim italic")
            for slide in specs.get("slides", [])[:5]:  # Show first 5
                content.append(f"  {slide.get('slide_number')}. {slide.get('headline')}\n", style="yellow")
    
    elif agent_name == "optimizer":
        decision = output.get("decision", "UNKNOWN")
        decision_color = "green" if decision == "APPROVE" else "yellow"
        content.append(f"Decision: ", style="dim")
        content.append(f"{decision}\n", style=f"bold {decision_color}")
        content.append(f"Quality Score: ", style="dim")
        content.append(f"{output.get('quality_score', 0)}/10\n", style="bold")
        content.append(f"Brand Consistency: ", style="dim")
        content.append(f"{output.get('brand_consistency_score', 0)}/10\n", style="bold")
        
        pred_min = output.get("predicted_impressions_min", 0)
        pred_max = output.get("predicted_impressions_max", 0)
        content.append(f"\nPredicted Impressions: ", style="dim")
        content.append(f"{pred_min:,} - {pred_max:,}\n", style="bold green")
        
        engagement = output.get("predicted_engagement_rate", 0)
        content.append(f"Predicted Engagement: ", style="dim")
        content.append(f"{engagement * 100:.1f}%\n", style="bold green")
        
        if output.get("suggestions"):
            content.append("\nImprovement Suggestions:\n", style="dim italic")
            for suggestion in output.get("suggestions", []):
                content.append(f"  💡 {suggestion}\n", style="cyan")
    
    panel = Panel(
        content,
        title=f"{emoji} {agent_name.upper()} Agent",
        border_style=color,
        expand=False,
    )
    console.print(panel)


def display_execution_summary(tracker):
    """Display a summary table of all agent executions."""
    table = Table(title="🔄 Execution Summary", show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Time (ms)", justify="right")
    table.add_column("Result", style="dim")
    
    for event in tracker.events:
        if event.event_type == "agent_complete":
            table.add_row(
                f"{AGENT_EMOJIS.get(event.agent_name, '🤖')} {event.agent_name.capitalize()}",
                "✅ Complete",
                str(event.execution_time_ms),
                event.data.get("summary", "")[:50] + "..." if len(event.data.get("summary", "")) > 50 else event.data.get("summary", ""),
            )
    
    console.print(table)


async def run_with_live_output():
    """Run the CLI with live agent output display."""
    console.print(Panel.fit(
        "[bold blue]LinkedIn AI Agent[/bold blue] - [italic]Enhanced Mode[/italic]\n"
        "Transform your ideas into viral LinkedIn posts\n"
        "[dim]With real-time agent thought display[/dim]",
        border_style="blue"
    ))
    
    # Get idea from user
    idea = Prompt.ask("\n[bold]Enter your post idea[/bold]")
    
    if not idea:
        console.print("[red]No idea provided. Exiting.[/red]")
        return
    
    # Show verbose output option
    verbose = Confirm.ask("[dim]Show detailed agent outputs?[/dim]", default=True)
    
    console.print("\n")
    
    # Generate a post ID
    import uuid
    post_id = str(uuid.uuid4())
    
    # Create progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing idea...", total=100)
        
        # Collect events for display
        events_collected = []
        
        async def event_callback(event: AgentEvent):
            events_collected.append(event)
            progress.update(task, completed=event.progress_percent, description=f"[cyan]{event.message}")
        
        # Get tracker and register callback
        tracker = get_tracker(post_id)
        tracker.on_event(event_callback)
        
        # Run initial generation
        state, tracker = await run_generation_with_tracking(
            raw_idea=idea,
            post_id=post_id,
        )
    
    console.print()
    
    # Display agent outputs if verbose
    if verbose:
        console.print("\n[bold cyan]═══ Agent Thought Process ═══[/bold cyan]\n")
        
        for name, output in tracker.agent_outputs.items():
            summary = tracker._generate_summary(name, output)
            display_agent_output(name, output, summary)
            console.print()
    
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
        remove_tracker(post_id)
        return
    
    # Show clarifying questions
    questions = state.get("clarifying_questions", [])
    if questions:
        console.print(Panel.fit(
            "[bold]The strategist has prepared some questions to help create better content.[/bold]",
            border_style="magenta"
        ))
        console.print()
        
        answers = {}
        for i, q in enumerate(questions, 1):
            console.print(f"[dim italic]Why this matters: {q.get('rationale', '')}[/dim italic]")
            required_tag = "[red]*[/red] " if q.get("required", True) else ""
            answer = Prompt.ask(f"{required_tag}[bold cyan]Q{i}:[/bold cyan] {q['question']}")
            answers[q['question_id']] = answer
            console.print()
        
        console.print()
        
        # Continue generation with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Generating content...", total=100)
            
            async def continue_callback(event: AgentEvent):
                progress.update(task, completed=event.progress_percent, description=f"[green]{event.message}")
            
            # Re-register callback
            tracker = get_tracker(post_id)
            tracker.on_event(continue_callback)
            
            state, tracker = await continue_generation_with_tracking(
                state=state,
                user_answers=answers,
                post_id=post_id,
            )
        
        console.print()
        
        # Display remaining agent outputs if verbose
        if verbose:
            console.print("\n[bold green]═══ Content Generation ═══[/bold green]\n")
            
            for name in ["writer", "visual", "optimizer"]:
                if name in tracker.agent_outputs:
                    output = tracker.agent_outputs[name]
                    summary = tracker._generate_summary(name, output)
                    display_agent_output(name, output, summary)
                    console.print()
    
    # Display execution summary
    display_execution_summary(tracker)
    console.print()
    
    # Show final post
    final_post = state.get("final_post", {})
    
    if final_post:
        hook = final_post.get("hook", {})
        body = final_post.get("body", "")
        cta = final_post.get("cta", "")
        hashtags = final_post.get("hashtags", [])
        
        full_content = f"{hook.get('text', '')}\n\n{body}\n\n{cta}"
        if hashtags:
            full_content += f"\n\n{' '.join('#' + h for h in hashtags)}"
        
        console.print(Panel(
            full_content,
            title="✨ Your LinkedIn Post",
            border_style="green",
            expand=False,
        ))
        
        # Show stats in a nice table
        optimizer = state.get("optimizer_output", {})
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Quality Score", f"{optimizer.get('quality_score', 0)}/10")
        stats_table.add_row("Brand Consistency", f"{optimizer.get('brand_consistency_score', 0)}/10")
        stats_table.add_row(
            "Predicted Impressions", 
            f"{optimizer.get('predicted_impressions_min', 0):,} - {optimizer.get('predicted_impressions_max', 0):,}"
        )
        stats_table.add_row(
            "Predicted Engagement",
            f"{optimizer.get('predicted_engagement_rate', 0) * 100:.1f}%"
        )
        
        console.print(Panel(stats_table, title="📊 Performance Predictions", border_style="blue"))
        
        # Show all hook variations
        if verbose:
            writer_output = state.get("writer_output", {})
            hooks = writer_output.get("hooks", [])
            if len(hooks) > 1:
                console.print("\n[bold]Alternative Hook Variations:[/bold]")
                for i, h in enumerate(hooks[1:], 2):
                    console.print(f"\n[dim]Hook {i} (Score: {h.get('score', 0)}/10)[/dim]")
                    console.print(f'  [italic]"{h.get("text", "")}"[/italic]')
        
        # Save option
        console.print()
        if Confirm.ask("[bold]Save to file?[/bold]", default=False):
            filename = f"linkedin_post_{post_id[:8]}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_content)
                f.write("\n\n---\n")
                f.write(f"Quality Score: {optimizer.get('quality_score', 0)}/10\n")
                f.write(f"Generated by LinkedIn AI Agent\n")
            console.print(f"[green]✓ Saved to {filename}[/green]")
        
        # Export execution log option
        if verbose:
            if Confirm.ask("[dim]Export execution log?[/dim]", default=False):
                log_filename = f"execution_log_{post_id[:8]}.json"
                with open(log_filename, "w", encoding="utf-8") as f:
                    json.dump(tracker.get_execution_summary(), f, indent=2, default=str)
                console.print(f"[green]✓ Execution log saved to {log_filename}[/green]")
    
    # Cleanup
    remove_tracker(post_id)
    
    console.print("\n[dim]Thank you for using LinkedIn AI Agent![/dim]")


def run():
    """Run the enhanced CLI."""
    asyncio.run(run_with_live_output())


if __name__ == "__main__":
    run()
