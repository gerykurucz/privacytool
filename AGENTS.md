## Operating principles

- Working code only. Plausibility is not correctness; verify before reporting
  done.
- Never fabricate file paths, APIs, commit hashes, command output, or test
  results. Read the file, run the command, or say what is unknown.
- Say when a premise appears wrong before implementing around it.
- Ask before proceeding only when a request has multiple plausible
  interpretations and the choice materially affects the result.
- Touch only what the task requires. Avoid drive-by refactors, formatting, or
  cleanup.
- Keep communication direct and concise. Skip flattery, filler, ceremonial
  openings, and emoji.
- Try to write short answers always and focus on only the task.
- Prefer zero comments in code.

## Command execution

- Prefer running code, tests, linters, and type checks over guessing.
- Read complete errors, logs, and stack traces before fixing them.
- Always test the code & review the full picture of the project.

## Before editing

- State the plan or success criteria before editing. For non-trivial work,
  include the verification you expect to run.
- Read the files you will touch and the nearby callers, consumers, or docs that
  define their behavior.
- Match existing project patterns, naming, layout, and style even if a different
  approach would be appealing in a new project.
- Resolve ambiguity by reading code or running commands when practical; surface
  assumptions out loud when they affect the result.
- Run the smallest meaningful verification during iteration and the requested or
  relevant final verification before reporting done.
- If verification fails, fix the cause instead of weakening the check.
- For UI or visual changes, verify visually with screenshots or equivalent
  rendered output.

## TODO after any task

- Step 1: Review the the entire project focusing on logical errors, bugs, things makes no sense, false connection between settings/options etc, everything.
- Step 2: See the implementented after-task changes in the full picture.
- Step 3: Resolve all found issues & clean up all files.
- Step 4: Run tests and verify the code is working as it should.
