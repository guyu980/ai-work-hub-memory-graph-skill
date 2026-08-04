# Advanced Deployment

Read this reference only for explicit organization storage, migration,
cross-runtime handoff, or bridge requests. A Feishu document used as a source
does not trigger this mode.

## Trigger Routing

- Normal BP, transcript, datapack, news, or Feishu-link intake: keep the local
  project and Memory Graph canonical.
- Simple document upload to Feishu: deliver the requested artifact without
  changing the canonical knowledge store.
- Canonical Feishu storage, local/organization synchronization, Context
  Registry export, another Agent taking over, migration, or a bridge: activate
  the adapter workflow below.

## Organization Profile

Read `context-storage-contract.md`. Preserve the same project, sector, technical,
person, and resource semantics while an adapter resolves locators, permissions,
queries, and writeback.

- Keep full evidence in the canonical project or event object.
- Use a Context Registry as a retrieval index, not a duplicate document store.
- In hybrid mode, declare one canonical write target and visible sync status.
- Never hardcode tenant IDs, folder tokens, Base fields, or permission groups.

## Portable Export

Export and validate a portable Registry delta with:

```bash
python3 <skill_dir>/scripts/export_context_registry.py \
  --workspace-root "<workspace_root>" \
  --output "<output_context_package.json>"
python3 <skill_dir>/scripts/validate_context_package.py \
  "<output_context_package.json>"
```

Upsert by `context_id`; do not create duplicate projects or records for each
runtime. Preserve source, version, visibility, and last-verified metadata, and
never expand the caller's permissions.
