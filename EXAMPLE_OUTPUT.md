# Example Output

## Analysis Mode Example

```
$ python commit_critic --analyze

Analyzing last 50 commits...

Found 50 commits. Sending to anthropic (claude-sonnet-4-20250514) for analysis...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💩 COMMITS THAT NEED WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "fixed bug"
Score: 2/10
Issue: Too vague - which bug? What was the impact? What component was affected?
Better: "fix(auth): resolve token expiration causing logout loops"

Commit: "wip"
Score: 1/10
Issue: No information about what's in progress. Commit messages should be complete even during development.
Better: "feat(api): add initial Redis caching layer (WIP)"

Commit: "updates"
Score: 2/10
Issue: Generic and uninformative. What was updated and why?
Better: "refactor(database): update schema to support multi-tenancy"

Commit: "fix"
Score: 1/10
Issue: One-word commit with no context. What was fixed?
Better: "fix(ui): correct alignment in mobile navigation menu"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 WELL-WRITTEN COMMITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit: "feat(api): add Redis caching layer
         - Implement cache for read endpoints
         - Add TTL configuration (default 5min)
         - Improves response time by 200ms average"
Score: 9/10
Why it's good: Uses conventional commit format, clear scope (api), specific changes listed, includes measurable impact

Commit: "refactor(auth): extract validation into middleware

         Previously validation was scattered across route handlers.
         This centralizes it and makes it easier to test and maintain.

         - Created validateToken middleware
         - Created validatePermissions middleware
         - Updated all protected routes to use middleware
         - Added unit tests for each validator"
Score: 10/10
Why it's good: Perfect structure with type, scope, clear subject. Body explains the why (context), what changed, and includes testing information

Commit: "fix(database): prevent race condition in user creation

         Issue: Multiple concurrent signups could create duplicate users
         Solution: Added unique constraint + proper error handling"
Score: 9/10
Why it's good: Identifies the problem clearly, explains the solution, includes context about when this occurs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 YOUR STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Average score: 4.8/10
Vague commits: 28 (56%)
One-word commits: 8 (16%)
```

## Interactive Mode Example

```
$ git add .
$ python commit_critic --write

Analyzing staged changes... (5 files changed, +187 -43 lines)

Changes detected:
  - Modified authentication logic in token handler
  - Added specific error types for auth failures
  - Extracted validation into a separate module
  - Updated unit tests to cover new error cases

Suggested commit message:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
refactor(auth): improve error handling and validation

- Add specific error types for different auth failures
  * InvalidTokenError for malformed tokens
  * ExpiredTokenError for expired sessions
  * PermissionDeniedError for authorization issues
- Extract validation logic into separate validator module
- Update all auth routes to use new error types
- Add comprehensive unit tests for edge cases
- Improves debugging by providing clearer error messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Enter to accept, or type your own message:
> [User presses Enter]

✓ Commit created successfully!
[main a3f2b8c] refactor(auth): improve error handling and validation
 5 files changed, 187 insertions(+), 43 deletions(-)
 create mode 100644 src/validators/auth.js
```

## Remote Repository Analysis Example

```
$ python commit_critic --analyze --url="https://github.com/facebook/react"

Cloning repository from https://github.com/facebook/react...

Analyzing last 50 commits...

Found 50 commits. Sending to anthropic (claude-sonnet-4-20250514) for analysis...

[... analysis output ...]
```

## Date Range Analysis Example

```
$ python commit_critic --analyze --start-date 2024-01-01 --end-date 2024-06-01

Analyzing commits from 2024-01-01 → 2024-06-01 (up to 50)...

Found 42 commits. Sending to anthropic (claude-sonnet-4-20250514) for analysis...

[... analysis output ...]
```

## Branch Analysis Example

```
$ python commit_critic --analyze --branch feature/auth --n 20

Analyzing last 20 commits on feature/auth...

Found 20 commits. Sending to anthropic (claude-sonnet-4-20250514) for analysis...

[... analysis output ...]
```
