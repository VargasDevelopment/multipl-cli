# Private Dispatch Scheduler

`multipl private dispatch-once` is a domain-neutral, single-shot scheduler for the Multipl private
work API. It does not use the generated public client and does not contain producer-specific task
logic. It installs or activates no timer, systemd unit, or cron job.

## Dependencies And Configuration

The dispatcher requires Linux namespaces, `/usr/bin/bwrap` (Bubblewrap), and an installed `codex`
executable. Bubblewrap must be able to create a mount and PID namespace. The command fails closed
if any of those prerequisites or sandbox mounts cannot be established.

Pass an explicit JSON configuration path. The file contains a bearer credential, must be a regular
file owned by the current effective user, and must have mode `0600`. No environment-variable or
task-type fallback is supported.

```json
{
  "baseUrl": "https://private.multipl.example",
  "bearer": "replace-with-private-bearer",
  "scopeHeaders": {
    "x-multipl-namespace": "example-namespace",
    "x-multipl-lane": "agent-workers"
  },
  "heartbeatSeconds": 20,
  "worktrees": {
    "example.registry/repository.change@1": {
      "cwd": "/srv/worktrees/repository-change",
      "model": "gpt-5.6-codex",
      "reasoning": "high"
    }
  }
}
```

Each `worktrees` key must be the full `registryId/typeId@positive-version`. The configured value is
the complete launch policy for that identity: an existing absolute working directory, model, and
reasoning effort. The scheduler sends exactly those identities in `taskAllowlist`; it never falls
back from an unknown identity to a task type or default worktree.

The resolved config file and derived `dispatch-state` directory must be outside every allowed task
cwd. This check also follows symlinks. Keep the config and state in a separate operator-controlled
directory so a worktree mount cannot expose the bearer, journal, or scope headers.

Run one scheduling pass with:

```bash
multipl private dispatch-once --config /etc/multipl/private-dispatch.json
```

Overlapping calls are harmless: a process-wide, nonblocking `fcntl.flock` makes the second call
exit successfully without acquiring work.

## Durable State And Remote Operations

Every remote ownership transition is write-ahead journaled with atomic temp-file write, file fsync,
rename, and parent-directory fsync. State directories are `0700`; journal, exchange, process,
schema, output, lock, and temporary files are `0600`.

The pass proceeds in this order:

1. Acquire the local process lock.
2. Replay a pending terminal outcome, result, acquire, or renew operation. A failed replay blocks
   the pass before any new acquire.
3. Read the private task registry and require every configured exact identity to exist.
4. Write `acquire_intent` with the exact allowlist and an idempotency key, then make exactly one
   `POST /private/v1/attempts/acquire-next`. The response is persisted as `acquire_response`
   before `claimed` or an empty-queue transition.
5. Read and verify the exact work, then persist `launched` before attempting Codex. At most one
   Codex process is attempted.
6. Before each renew, persist `renew_intent` with the exact current lease and stable key. An
   ambiguous response or restart replays that same request; the returned generation is journaled
   before any later state.
7. Persist the terminal operation before sending it. Successful agent output is submitted as a
   result; failures and unknowns use the terminal outcome endpoint below.

Lease expiry timestamps are parsed as authoritative UTC times. The first and later renewals use a
safety margin based on remaining authority; `heartbeatSeconds` is only a maximum cadence. The
renew HTTP timeout is no longer than the remaining lease. The dispatcher does not launch when the
lease is expired or too close to expiry.

## Terminal Outcomes

Failures never use a producer result envelope. The scheduler sends:

```text
PUT /private/v1/work/<workId>/attempts/<attemptId>/outcome
Idempotency-Key: <stable-key>
```

```json
{
  "lease": {"leaseId": "...", "generation": 3},
  "outcome": "failed",
  "code": "invalid_agent_output"
}
```

`outcome` is `failed` for invalid output, nonzero exit, lease loss, isolation failure, and other
bounded dispatcher failures. `outcome` is `unknown` when the scheduler cannot know what happened,
including restart after launch. Terminal records are retried before any acquire and are never
converted into runnable producer results. A rejected or unavailable terminal submission remains
spooled and blocks new work.

Successful output alone uses:

```text
PUT /private/v1/work/<workId>/result
```

with the producer payload and the current lease.

## Codex Isolation And Process Lifetime

Codex runs under Bubblewrap with `--die-with-parent`, a new PID namespace, a private `/proc`, a
private `/tmp`, and the host network namespace retained for Codex itself. The inner Codex command
still uses `--sandbox workspace-write`.

The namespace exposes only:

- the exact configured worktree at `/workspace`, read-write;
- required system runtime paths and selected DNS/TLS files, read-only;
- `/codex-home/auth.json`, read-only, when present;
- a per-attempt `/exchange` containing only the output schema and output-last-message file.

The dispatcher config, bearer, scope headers, state parent, unrelated home files, and host `/proc`
are not mounted or passed through. The child receives an explicit environment allowlist for Codex,
OpenAI authentication, proxies, TLS, locale, and networking; `MULTIPL_*` and unrelated variables
are removed. The prompt contains only the exact task identity and canonical work input.

The wrapper PID, process-group ID, `/proc` start time, and command hash are durably recorded around
launch. Startup reconciliation and terminal-unknown handling terminate a matching process group
with PID-reuse guards. Normal exceptions and SIGTERM run cleanup in `finally`; SIGKILL containment
relies on Bubblewrap's kernel parent-death setting.
