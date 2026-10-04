# Goal

## Workspace

Harness directory:

```text
{{WORKSPACE}}
```

Target working directory:

```text
{{TARGET_CWD}}
```

## Objective

{{OBJECTIVE}}

## Allowed Changes

- {{ALLOWED_CHANGE_1}}

## Constraints

- Do not delete user files unless the goal explicitly says deletion is allowed.
- Do not run `git init`, `git add`, `git commit`, `git gc`, or `git repack` inside `706-knowledge`.
- Before editing, inspect the relevant files and current state.
- Keep changes scoped to the target working directory unless this goal explicitly allows another path.

## Done When

- {{DONE_WHEN_1}}
- `bash checks.sh` exits with status 0.

## Check Commands

The runner will execute:

```bash
bash checks.sh
```

## Stop Conditions

- Stop when `checks.sh` passes.
- Stop after `MAX_TURNS` turns.
- Stop if the Claude CLI command fails.
- Stop if the task requires a risky decision not covered by this goal.
