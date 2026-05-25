# Quick Start Guide

Get started with Commit Critic in 3 minutes!

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 2: Get an API Key

You need a key from one of these providers:

- **Anthropic (Claude)** — [console.anthropic.com](https://console.anthropic.com/)
- **OpenAI (GPT-4o)** — [platform.openai.com](https://platform.openai.com/)

You don't need to set anything yet — the tool will ask for it interactively on first run.

## Step 3: Run It!

**Option A: Analyze your commits**
```bash
python commit_critic --analyze
```
On first run, you'll be guided through provider selection, API key entry, and model selection. Settings are saved to `settings.json` for next time.

**Option B: Get help writing a commit**
```bash
git add .
python commit_critic --write
```

**Option C: Analyze any public GitHub repo**
```bash
python commit_critic --analyze --url="https://github.com/torvalds/linux"
```

## That's it! 🎉

The tool will:
- Score your commits 1-10
- Show what's good and what needs work
- Give specific suggestions for improvement
- Help you write better commits going forward

## Common Issues

**"Invalid key or connection error"**
→ Double-check your API key at the provider's dashboard and try again

**Want to switch providers or models?**
→ Run `python commit_critic --reconfigure` to go through setup again

**"Not a git repository"**
→ Run in a git repo, or use `--url` to analyze remote repos
