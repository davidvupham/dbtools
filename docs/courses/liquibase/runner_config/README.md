# Runner Configuration Directory

This directory contains an example environment file for the Liquibase tutorial self-hosted GitHub Actions runner.

## Files

- `runner.env.example` – Template with placeholder values. Safe to commit.

## Recommended Local Usage

Copy the example to a non-committed filename that holds your real (ephemeral) registration token.

```bash
cp docs/courses/liquibase/runner_config/runner.env.example docs/courses/liquibase/runner_config/runner.env.local
nano docs/courses/liquibase/runner_config/runner.env.local
```

Then load and export variables before starting the runner:

```bash
source docs/courses/liquibase/runner_config/runner.env.local
export RUNNER_NAME RUNNER_WORKDIR RUNNER_TOKEN REPO_URL RUNNER_LABELS RUNNER_GROUP
cd docs/courses/liquibase/docker
docker-compose --profile runner up -d github_runner
```

## Security Notes

- Never commit a file containing a real `RUNNER_TOKEN`.
- Registration tokens expire (1 hour) – regenerate via GitHub UI when needed.
- Personal Access Tokens (PATs) are NOT used for runner registration.

## Alternative Placement

You may also store the live `runner.env` outside the repository (e.g. `/data/github-runner-config/runner.env`) and keep only the example here.
