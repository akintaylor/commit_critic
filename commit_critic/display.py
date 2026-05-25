from typing import Dict

from commit_critic.utils import console


def display_analysis(analysis: Dict, total_commits: int) -> None:
    if analysis["poor_commits"]:
        console.print("\n")
        console.print("━" * 60, style="red")
        console.print("💩 COMMITS THAT NEED WORK", style="bold red", justify="center")
        console.print("━" * 60, style="red")
        console.print()

        for commit in analysis["poor_commits"]:
            console.print(f"[yellow]Commit:[/yellow] \"{commit['message']}\"")
            console.print(f"[red]Score: {commit['score']}/10[/red]")
            console.print(f"[dim]Issue:[/dim] {commit['issue']}")
            console.print(f"[green]Better:[/green] {commit['better']}")
            console.print()

    if analysis["good_commits"]:
        console.print("━" * 60, style="green")
        console.print("💎 WELL-WRITTEN COMMITS", style="bold green", justify="center")
        console.print("━" * 60, style="green")
        console.print()

        for commit in analysis["good_commits"]:
            lines = commit["message"].split("\n")
            console.print(f"[cyan]Commit:[/cyan] \"{lines[0]}\"")
            for line in lines[1:]:
                if line.strip():
                    console.print(f"         {line}")
            console.print(f"[green]Score: {commit['score']}/10[/green]")
            console.print(f"[dim]Why it's good:[/dim] {commit['why_good']}")
            console.print()

    stats = analysis["stats"]
    console.print("━" * 60, style="blue")
    console.print("📊 YOUR STATS", style="bold blue", justify="center")
    console.print("━" * 60, style="blue")
    console.print()

    console.print(f"Average score: [cyan]{stats['average_score']:.1f}/10[/cyan]")

    vague_pct = (stats["vague_count"] / total_commits * 100) if total_commits > 0 else 0
    console.print(f"Vague commits: [yellow]{stats['vague_count']} ({vague_pct:.0f}%)[/yellow]")

    one_word_pct = (stats["one_word_count"] / total_commits * 100) if total_commits > 0 else 0
    console.print(f"One-word commits: [red]{stats['one_word_count']} ({one_word_pct:.0f}%)[/red]")
    console.print()
