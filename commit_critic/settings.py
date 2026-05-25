import os
import sys
import json
from typing import Dict, List, Optional

import questionary
from anthropic import Anthropic
from openai import OpenAI
from rich.panel import Panel
from rich.prompt import Prompt

from commit_critic.utils import console, SETTINGS_FILE, PROVIDER_DEFAULTS


def load_settings() -> Dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_settings(settings: Dict) -> None:
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))


def fetch_models(provider: str, api_key: str) -> List[str]:
    try:
        if provider == "anthropic":
            client = Anthropic(api_key=api_key)
            result = client.models.list()
            return [m.id for m in result.data]
        else:
            client = OpenAI(api_key=api_key)
            result = client.models.list()
            chat_prefixes = ("gpt-4", "gpt-3.5", "o1", "o3", "o4")
            models = [
                m.id for m in result.data
                if any(m.id.startswith(p) for p in chat_prefixes) and ":" not in m.id
            ]
            return sorted(set(models), reverse=True)
    except Exception:
        return []


def interactive_setup() -> Dict:
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Commit Critic Setup[/bold cyan]\n[dim]Configure your AI provider[/dim]",
        border_style="cyan"
    ))

    provider = questionary.select(
        "Select a provider:",
        choices=[
            questionary.Choice("Anthropic (Claude)  —  claude-*", value="anthropic"),
            questionary.Choice("OpenAI (GPT)        —  gpt-4o, o1, ...", value="openai"),
        ]
    ).ask()
    if provider is None:
        sys.exit(0)

    env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"

    while True:
        api_key = questionary.password(f"Enter your {env_key}:").ask()
        if api_key is None:
            sys.exit(0)
        with console.status("[cyan]Validating key and fetching models...[/cyan]"):
            models = fetch_models(provider, api_key)
        if models:
            console.print("[green]✓ Key valid — models loaded[/green]")
            break
        console.print("[red]✗  Invalid key or connection error. Please try again.[/red]")

    choices = [
        questionary.Choice(
            f"{m}  (default)" if m == PROVIDER_DEFAULTS.get(provider) else m,
            value=m
        )
        for m in models
    ]
    selected_model = questionary.select("Select a model:", choices=choices).ask()
    if selected_model is None:
        sys.exit(0)

    settings = {"provider": provider, "model": selected_model, "api_key": api_key}

    if questionary.confirm("Save settings to settings.json for next time?", default=True).ask():
        save_settings(settings)
        console.print(f"[green]✓ Saved to {SETTINGS_FILE}[/green]")
        console.print("[dim]Tip: API key is stored in plaintext. Use an env var on shared machines.[/dim]")

    console.print()
    return settings


def resolve_config(args) -> Dict:
    settings = load_settings()

    if args.provider:
        provider = args.provider
        env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        api_key = (
            os.environ.get(env_key)
            or (settings.get("api_key") if settings.get("provider") == provider else None)
        )
        if not api_key:
            console.print(f"\n[yellow]{env_key} not set.[/yellow]")
            api_key = Prompt.ask(f"Enter your {env_key}", password=True)
        model = PROVIDER_DEFAULTS[provider]
        if settings.get("provider") == provider and settings.get("model"):
            model = settings["model"]
        return {"provider": provider, "api_key": api_key, "model": model}

    if settings:
        provider = settings["provider"]
        env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        api_key = settings.get("api_key") or os.environ.get(env_key)
        if not api_key:
            api_key = Prompt.ask(f"Enter your {env_key}", password=True)
        model = settings.get("model", PROVIDER_DEFAULTS[provider])
        console.print(f"[dim]Using saved settings: {provider} / {model}[/dim]")
        return {"provider": provider, "api_key": api_key, "model": model}

    return interactive_setup()
