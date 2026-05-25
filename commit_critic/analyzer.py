import json
from typing import Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI

from commit_critic.utils import console, PROVIDER_DEFAULTS


class CommitAnalyzer:
    """Analyze commits and suggest messages using an LLM."""

    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model or PROVIDER_DEFAULTS[self.provider]

        if self.provider == "anthropic":
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = OpenAI(api_key=self.api_key)

    def _call_llm(self, prompt: str, max_tokens: int) -> str:
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        else:
            completion = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content

    def _parse_json_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"):
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)

    def analyze_commits(self, commits: List[Dict[str, str]]) -> Dict:
        commit_text = "\n\n".join(
            f"Commit {i + 1}: {c['message']}" for i, c in enumerate(commits)
        )

        prompt = f"""Analyze these {len(commits)} git commit messages and provide detailed feedback.

Commits to analyze:
{commit_text}

For each commit, evaluate:
1. Clarity and specificity
2. Proper use of conventional commit format (if applicable)
3. Whether it explains WHAT and WHY
4. Appropriate level of detail

Respond with a JSON object with this exact structure:
{{
  "poor_commits": [
    {{
      "message": "exact commit message",
      "score": 1-10,
      "issue": "brief explanation of what's wrong",
      "better": "suggested improvement"
    }}
  ],
  "good_commits": [
    {{
      "message": "exact commit message",
      "score": 1-10,
      "why_good": "what makes this commit message effective"
    }}
  ],
  "stats": {{
    "average_score": 0.0-10.0,
    "vague_count": number,
    "one_word_count": number
  }}
}}

Only include commits scoring 1-5 in poor_commits and 8-10 in good_commits.
Be strict but fair in your scoring."""

        try:
            return self._parse_json_response(self._call_llm(prompt, max_tokens=4000))
        except Exception as e:
            console.print(f"[red]Error analyzing commits: {e}[/red]")
            return {
                "poor_commits": [],
                "good_commits": [],
                "stats": {"average_score": 0, "vague_count": 0, "one_word_count": 0},
            }

    def suggest_commit_message(self, diff: str, stats: Dict[str, int]) -> Dict:
        max_diff_length = 6000
        if len(diff) > max_diff_length:
            diff = diff[:max_diff_length] + "\n\n[... diff truncated for analysis ...]"

        prompt = f"""Based on these staged changes, return a JSON object with two fields.

Staged changes summary:
- Files changed: {stats['files']}
- Lines added: {stats['additions']}
- Lines deleted: {stats['deletions']}

Diff:
{diff}

Respond with this exact JSON structure:
{{
  "changes": [
    "short plain-English description of each logical change detected (3-6 bullets)"
  ],
  "message": "the full commit message text"
}}

For the commit message:
1. Use conventional commit format (feat/fix/refactor/docs/test/chore)
2. Clear, concise subject line (50 chars or less)
3. Body with bullet points explaining the changes
4. Explains both WHAT changed and WHY

Respond with ONLY the JSON object, no additional commentary."""

        try:
            return self._parse_json_response(self._call_llm(prompt, max_tokens=1200))
        except Exception as e:
            console.print(f"[red]Error generating commit message: {e}[/red]")
            return {}
