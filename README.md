# Commit Message Critic

An AI-powered terminal tool that analyzes Git commit message quality and helps developers write better commits using Claude AI (Anthropic) or GPT-4o (OpenAI).

## Features

- **📊 Analyze Mode**: Review your recent commits with AI-generated critique
  - Analyzes local or remote repositories
  - Configurable number of commits to review (default: 50, max: 100)
  - Filter by date range (`--start-date`, `--end-date`)
  - Filter by branch (`--branch`)
  - Scores each commit (1-10)
  - Categorizes commits into "needs work" and "well-written"
  - Provides specific suggestions for improvement
  - Shows statistics (average score, vague commits, one-word commits)

- **✍️ Interactive Mode**: AI-assisted commit message writing
  - Analyzes your staged changes
  - Shows a plain-English summary of detected changes
  - Suggests well-formatted commit messages
  - Uses conventional commit format
  - Explains both WHAT and WHY
  - Interactive prompt to accept or modify

## Requirements

- Python 3.8 or higher
- Git installed and available in PATH
- An API key for your chosen provider (Anthropic or OpenAI)

## Installation

1. Clone or download this repository

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key for your chosen provider:

**Anthropic (default):**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**OpenAI:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

To make a key persistent, add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
# Anthropic
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc

# OpenAI
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc

source ~/.zshrc
```

## Usage

### Help

View all available options at any time:
```bash
python commit_critic --help
```

```
usage: python commit_critic [-h] [--analyze] [--write] [--url URL] [--n NUM]
                             [--provider {anthropic,openai}] [--reconfigure]
                             [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
                             [--branch BRANCH]

AI-powered Git commit message analyzer and writer

options:
  -h, --help            show this help message and exit
  --analyze             Analyze existing commits in the repository
  --write               Interactive mode to write a new commit message
  --url URL             URL of remote repository to analyze (requires --analyze)
  --n NUM               Number of last commits to analyze (default: 50, max: 100)
  --provider {anthropic,openai}
                        LLM provider: 'anthropic' or 'openai' (omit to use
                        saved settings or interactive setup)
  --reconfigure         Re-run provider and model setup, overwriting saved settings
  --start-date YYYY-MM-DD
                        Only analyze commits after this date (requires --analyze)
  --end-date YYYY-MM-DD
                        Only analyze commits before this date (requires --analyze)
  --branch BRANCH       Branch to analyze (requires --analyze, defaults to
                        current branch)
```

### Analyze Mode

**Analyze commits in current repository:**
```bash
python commit_critic --analyze
```

**Analyze a specific number of commits:**
```bash
python commit_critic --analyze --n 10
```

**Analyze commits from a remote repository:**
```bash
python commit_critic --analyze --url="https://github.com/username/repo"
```

**Analyze using OpenAI instead of Anthropic:**
```bash
python commit_critic --analyze --provider openai
```

**Filter by date range:**
```bash
python commit_critic --analyze --start-date 2024-01-01 --end-date 2024-06-01
```

**Analyze a specific branch:**
```bash
python commit_critic --analyze --branch feature/auth
```

**Combine options — last 20 commits on a branch from a remote repo:**
```bash
python commit_critic --analyze --url="https://github.com/username/repo" --n 20 --branch main
```

**Example output:**
```
Analyzing last 10 commits...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💩 COMMITS THAT NEED WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "fixed bug"
Score: 2/10
Issue: Too vague - which bug? What was the impact?
Better: "fix(auth): resolve token expiration handling"

Commit: "wip"
Score: 1/10
Issue: No information about what's in progress
Better: Describe what you're working on

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 WELL-WRITTEN COMMITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "feat(api): add Redis caching layer
         - Implement cache for read endpoints
         - Add TTL configuration
         - Improves response time by 200ms"
Score: 9/10
Why it's good: Clear scope, specific changes, measurable impact

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 YOUR STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average score: 4.2/10
Vague commits: 34 (68%)
One-word commits: 12 (24%)
```

### Interactive Mode

**Get AI help writing a commit message:**
```bash
# First, stage your changes
git add .

# Then run the tool (Anthropic by default)
python commit_critic --write

# Or use OpenAI
python commit_critic --write --provider openai
```

**Example output:**
```
Analyzing staged changes... (12 files changed, +247 -89 lines)

Changes detected:
  - Modified authentication logic
  - Added error handling for token expiration
  - Updated unit tests to cover edge cases

Suggested commit message:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
refactor(auth): improve error handling

- Add specific error types for auth failures
- Extract validation into separate methods
- Update tests to cover edge cases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Enter to accept, or type your own message:
>
```

## Settings

On first run (without `--provider`), the tool walks you through an interactive setup:

1. Choose a provider — **Anthropic** or **OpenAI**
2. Enter your API key (validated live against the provider)
3. Pick from the list of available models fetched from the API
4. Optionally save everything to `settings.json` for future runs

On subsequent runs the saved settings are used automatically. To change provider or model, run:
```bash
python commit_critic --reconfigure
```

**settings.json format:**
```json
{
  "provider": "anthropic",
  "model": "claude-opus-4-7",
  "api_key": "sk-ant-..."
}
```

> **Note:** `settings.json` stores your API key in plaintext. Add it to `.gitignore` and avoid committing it. For shared or CI environments, use environment variables (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`) instead.

## How It Works

### Analysis Mode
1. Fetches the last N commits from your repository (default 50, configurable via `--n`, max 100)
2. Applies any date range or branch filters
3. Sends commit messages to the configured LLM (Anthropic or OpenAI) for analysis
4. The model evaluates each commit based on:
   - Clarity and specificity
   - Conventional commit format
   - Whether it explains WHAT and WHY
   - Appropriate level of detail
5. Returns structured feedback with scores and suggestions

### Interactive Mode
1. Reads your staged changes using `git diff --staged`
2. Sends the diff to the configured LLM with context
3. The model returns a plain-English summary of detected changes and a well-formatted commit message:
   - Conventional commit format (feat/fix/refactor/etc.)
   - Clear, concise subject line
   - Detailed body with bullet points
   - Explains both changes and reasoning
4. Presents the suggestion for you to accept or modify
