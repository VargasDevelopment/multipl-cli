# Private Dispatch Scheduler

`multipl private dispatch-once` is a domain-neutral, single-shot scheduler for the Multipl private
work API. It does not use the generated public client and does not contain producer-specific task
logic.

## Configuration

Pass an explicit JSON configuration path. The file contains a bearer credential and must be owned
with mode `0600`. No environment-variable or task-type fallback is supported.

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

Run one scheduling pass with:

```bash
multipl private dispatch-once --config /etc/multipl/private-dispatch.json
```

This command installs or activates no timer. An operator may call it from an external scheduler,
but overlapping calls are harmless: a process-wide, nonblocking `fcntl.flock` makes the second
call exit successfully without acquiring work.

## One-shot behavior

Every invocation performs these steps in order:

1. Acquire the local process lock.
2. Flush or reconcile the durable journal. A pending result that still cannot be submitted causes
   an error exit before any acquire request.
3. Read the private task registry and require every configured exact identity to exist.
4. Make one `acquire-next` request. A `204`, empty body, or `{ "attempt": null }` exits successfully
   before prompt construction or agent launch.
5. Persist `claimed`, read and verify the exact work, then persist `launched` before attempting
   `Popen`. At most one Codex process is attempted.
6. Renew the lease at `heartbeatSeconds` intervals. Lease renewal failure terminates the new child
   process group and records a dispatcher failure result.
7. Persist `result_pending` before result submission. Submission failure leaves the operation in
   the journal for the next invocation, using the same idempotency key.

The `claimed`, `launched`, and `result_pending` states use atomic temp-file write, file fsync,
rename, and parent-directory fsync. State directories are `0700`; journal, schema, output, lock,
and temporary files are `0600`. A restart after `launched` records an unknown/failure result and
never launches that attempt again. The private result contract still applies: if a task result
schema does not admit the dispatcher failure envelope, the rejected submission remains durably
pending and blocks new acquisition for operator reconciliation.

## Codex boundary

The exact process form is:

```text
codex exec --ephemeral --ignore-user-config --sandbox workspace-write -C <exact-cwd> \
  --output-schema <private-state-file> --output-last-message <private-state-file> \
  --model <exact-model> --config model_reasoning_effort="<exact-reasoning>" -
```

The deterministic prompt is passed on stdin and contains only the exact task identity and canonical
JSON work input. The output schema is the matching private registry result schema. The child gets
an explicit allowlist of platform, proxy, TLS, Codex-home, and OpenAI authentication variables;
all `MULTIPL_*` variables and unrelated environment values are removed. Bearers, scope headers,
private config paths, prompts, and child output are never logged.
