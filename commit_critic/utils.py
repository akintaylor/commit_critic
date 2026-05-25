from pathlib import Path
from rich.console import Console
from rich import box

console = Console()

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

PROVIDER_DEFAULTS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}
