# Demo Surface

This page lists the main `stqdm` behaviors we want the Streamlit demo app and test suite to cover.

## Basic Usage

- Main area loop with an explicit total
- Sidebar target via `st.sidebar`
- Column placement
- Multiple independent bars in columns
- Nested bars with cleanup
- Iterables without a known length
- Generator-style iteration
- Manual `while` loop updates

## Configuration Behavior

- Frontend-only versus backend-only output
- `leave`
- `bar_format`
- `stqdm.scope(...)`
- Process-safe locking for consecutive bars
- Patching `tqdm.auto.tqdm`

## Integration Patterns

- Stop-and-retry comparison with plain Streamlit widgets
- Async iteration and `asyncio.gather()`
- `stqdm.pandas()`
- Caching plus batched processing
- Session-state lock reuse

## Regression Cases

- Consecutive bar rendering after lock setup
- Unknown total and no-length handling
- Nested cleanup via `st_clear()`
- Layout placement in sidebar and columns

## What We Test

- Progress percent and rendered text
- Sidebar and column placement
- Nested bar cleanup
- Configuration isolation
- Pandas hook behavior
- Async iteration and async gather behavior
- Patching behavior
- A small set of full app navigation checks
