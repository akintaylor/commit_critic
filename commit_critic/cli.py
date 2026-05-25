import sys
import datetime
import subprocess
import shutil
import argparse
from typing import Optional

from rich.prompt import Prompt

from commit_critic.utils import console
from commit_critic.settings import interactive_setup, resolve_config
from commit_critic.git_ops import GitOperations
from commit_critic.analyzer import CommitAnalyzer
from commit_critic.display import display_analysis


def analyze_mode(
    url: Optional[str] = None,
    n: int = 50,
    provider: str = "anthropic",
    api_key: str = "",
    model: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    branch: Optional[str] = None,
) -> None:
    git_ops = GitOperations()
    repo_path = "."
    temp_dir = None

    if url:
        temp_dir = git_ops.clone_repo(url, depth=n)
        if not temp_dir:
            return
        repo_path = temp_dir
    elif not git_ops.is_git_repo():
        console.print("[red]Error: Not a git repository. Use --url to analyze a remote repo.[/red]")
        return

    try:
        branch_label = f" on [bold]{branch}[/bold]" if branch else ""
        if start_date or end_date:
            date_range = f"{start_date or '...'} → {end_date or 'now'}"
            console.print(f"\n[cyan]Analyzing commits from {date_range}{branch_label} (up to {n})...[/cyan]\n")
        else:
            console.print(f"\n[cyan]Analyzing last {n} commits{branch_label}...[/cyan]\n")

        commits = git_ops.get_commits(
            repo_path, limit=n, start_date=start_date, end_date=end_date, branch=branch
        )

        if not commits:
            console.print("[yellow]No commits found to analyze.[/yellow]")
            return

        console.print(f"[dim]Found {len(commits)} commits.[/dim]\n")

        analyzer = CommitAnalyzer(provider=provider, api_key=api_key, model=model)
        with console.status(f"[cyan]Sending to {provider} ({model}) for analysis...[/cyan]"):
            analysis = analyzer.analyze_commits(commits)

        display_analysis(analysis, len(commits))

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


def write_mode(
    provider: str = "anthropic",
    api_key: str = "",
    model: Optional[str] = None,
) -> None:
    git_ops = GitOperations()

    if not git_ops.is_git_repo():
        console.print("[red]Error: Not a git repository.[/red]")
        return

    diff = git_ops.get_staged_diff()
    if not diff:
        console.print("[yellow]No staged changes found. Stage your changes with 'git add' first.[/yellow]")
        return

    stats = git_ops.get_diff_stats()
    console.print("\n[cyan]Analyzing staged changes...[/cyan] ", end="")
    console.print(f"[dim]({stats['files']} files changed, +{stats['additions']} -{stats['deletions']} lines)[/dim]\n")

    analyzer = CommitAnalyzer(provider=provider, api_key=api_key, model=model)
    with console.status("[cyan]Generating commit message...[/cyan]"):
        result = analyzer.suggest_commit_message(diff, stats)

    if not result:
        return

    changes = result.get("changes", [])
    suggested_message = result.get("message", "")

    if changes:
        console.print("[bold]Changes detected:[/bold]")
        for change in changes:
            console.print(f"  [dim]-[/dim] {change}")
        console.print()

    console.print("[green]Suggested commit message:[/green]")
    console.print("━" * 60)
    console.print(suggested_message)
    console.print("━" * 60)
    console.print()

    user_input = Prompt.ask(
        "[yellow]Press Enter to accept, or type your own message[/yellow]",
        default="",
    )
    final_message = user_input if user_input.strip() else suggested_message

    try:
        proc = subprocess.run(
            ["git", "commit", "-m", final_message],
            capture_output=True, check=True, text=True,
        )
        console.print("\n[green]✓ Commit created successfully![/green]")
        console.print(f"[dim]{proc.stdout}[/dim]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Error creating commit: {e.stderr}[/red]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI-powered Git commit message analyzer and writer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze existing commits in the repository")
    parser.add_argument("--write", action="store_true",
                        help="Interactive mode to write a new commit message")
    parser.add_argument("--url", type=str,
                        help="URL of remote repository to analyze (requires --analyze)")
    parser.add_argument("--n", type=int, default=50, metavar="NUM",
                        help="Number of last commits to analyze (default: 50, max: 100)")
    parser.add_argument("--provider", type=str, default=None,
                        choices=["anthropic", "openai"],
                        help="LLM provider: 'anthropic' or 'openai' (omit to use saved settings or interactive setup)")
    parser.add_argument("--reconfigure", action="store_true",
                        help="Re-run provider and model setup, overwriting saved settings")
    parser.add_argument("--start-date", type=str, default=None, metavar="YYYY-MM-DD",
                        help="Only analyze commits after this date (requires --analyze)")
    parser.add_argument("--end-date", type=str, default=None, metavar="YYYY-MM-DD",
                        help="Only analyze commits before this date (requires --analyze)")
    parser.add_argument("--branch", type=str, default=None, metavar="BRANCH",
                        help="Branch to analyze (requires --analyze, defaults to current branch)")
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.n > 100:
        console.print("[red]Error: --n cannot exceed 100[/red]")
        sys.exit(1)

    if not args.analyze and not args.write:
        parser.print_help()
        console.print("\n[yellow]Please specify either --analyze or --write[/yellow]")
        sys.exit(1)

    if args.url and not args.analyze:
        console.print("[red]Error: --url can only be used with --analyze[/red]")
        sys.exit(1)

    if args.analyze and args.write:
        console.print("[red]Error: Cannot use --analyze and --write together[/red]")
        sys.exit(1)

    if (args.start_date or args.end_date) and not args.analyze:
        console.print("[red]Error: --start-date and --end-date can only be used with --analyze[/red]")
        sys.exit(1)

    if args.branch and not args.analyze:
        console.print("[red]Error: --branch can only be used with --analyze[/red]")
        sys.exit(1)

    for flag, value in [("--start-date", args.start_date), ("--end-date", args.end_date)]:
        if value:
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                console.print(f"[red]Error: {flag} must be in YYYY-MM-DD format[/red]")
                sys.exit(1)

    if args.start_date and args.end_date and args.start_date > args.end_date:
        console.print("[red]Error: --start-date must be before --end-date[/red]")
        sys.exit(1)


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.reconfigure:
        interactive_setup()
        sys.exit(0)

    validate_args(args, parser)
    config = resolve_config(args)

    if args.analyze:
        analyze_mode(
            url=args.url, n=args.n,
            start_date=args.start_date, end_date=args.end_date,
            branch=args.branch, **config,
        )
    elif args.write:
        write_mode(**config)
