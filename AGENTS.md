# Agent Guide for STqdm

## Project Mission

This is the package for STqdm, a library that integrates `tqdm` inside Streamlit using Streamlit's native `.progress` widget.

The goal is to make progress bars in Streamlit as easy and familiar as `tqdm`, while staying useful to the widest possible part of the community. We try to maintain compatibility with as many versions of Streamlit and `tqdm` as practical, and we try to support as many `tqdm` features as possible.

## Priorities

- Preserve the simple public API: users should be able to use STqdm almost like `tqdm`.
- Prefer compatibility over clever rewrites. Changes should avoid breaking older supported Streamlit or `tqdm` combinations unless there is a clear reason.
- Treat `tqdm` behavior as the reference when possible. STqdm should adapt that behavior to Streamlit rather than inventing unrelated progress semantics.
- Keep documentation small and useful. The main documentation is `README.md`, supported by Streamlit demo apps and examples.
- Keep examples runnable and focused on real user workflows.

## Testing

This package must be tested across multiple Streamlit and `tqdm` versions. We use `nox` for that compatibility matrix.

When changing behavior:

- Add or update focused pytest tests for the changed behavior.
- Use nox when the change may affect version compatibility.
- Pay special attention to frontend rendering, `tqdm` formatting options, unknown totals, `leave` behavior, backend output, and scoped/default configuration.
- Streamlit demo apps are part of the documentation surface, so update them when user-facing behavior changes.

## Repository Landmarks

- `stqdm/`: library code.
- `tests/`: unit and integration tests.
- `examples/`: small examples for users.
- `demo/`: Streamlit demo/documentation apps.
- `README.md`: primary documentation.
- `noxfile.py`: compatibility test sessions.

## Agent Rules

- Before editing, check the working tree and preserve local user changes.
- Read the nearby implementation and tests before making changes.
- Keep changes scoped to the request.
- Do not update generated artifacts, lock files, or release files unless the task requires it.
- If you run tests or checks, report which ones you ran and the result.
