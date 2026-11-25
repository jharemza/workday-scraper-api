# Task 2.4 release note — durable scraper outcomes

## Compatibility change

`run_scrape()` now returns a machine-readable object instead of `None`:

```json
{
  "success": true,
  "institutions": []
}
```

Every selected institution is conservatively required. A failed required
institution sets top-level `success` to `false`; callers must not treat the run
as publication-safe. An optional-institution policy has not been introduced.

## Per-institution fields

- `metadata_ids_found`: distinct authoritative listing identifiers; this is a
  candidate count, not a database-write count.
- `detail_fetch_succeeded`: uniquely identified detail records fetched before
  persistence.
- `failed_detail`: required detail records missing or invalid before persistence.
- `actual_inserted`, `actual_deleted`, `actual_updated`: SQL changes returned
  only after the per-institution transaction commits. Updates are currently
  always zero because the scraper has no update mutation path.
- `institution_complete`, `status`, and `error`: durable success/failure state.

## CLI and HTTP behavior

- `run.py scrape` emits the JSON result and exits `0` only when every selected
  institution completes; it exits `1` for any required-institution failure.
- `POST /jobs/scrape` returns the same JSON payload with `200` on complete
  success and `503` when one or more required institutions fail.

## Task 4.1 release gate

Do not resume publication or production scheduling until the result reports
`success: true`, every institution has `institution_complete: true`, and the
operational validation required by Task 4.1 is complete.
