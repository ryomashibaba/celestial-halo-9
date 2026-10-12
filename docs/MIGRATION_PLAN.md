# Non-construction migration plan

1. Preserve M107 cumulative ZIP unchanged outside Git. Original 1,217 archive members have their SHA-256 hashes in the previously generated M108 full bootstrap ZIP.
2. Keep the cumulative archive and potential copyrighted source data out of the default Git history; import only inventoried, approved development sources.
3. Source provenance currently PINNED but the exact per-file M107 manifest is not yet mirrored into GitHub.
4. Register exact Minecraft world coordinates and absolute Y only from a read-only snapshot; model-relative H does not qualify.
5. Generate each new candidate independently from its chosen verified parent (M83/M101); NEVER blend multiple unapproved alternatives implicitly.
6. Promote a new formal masterplan only with user approval, image comparisons, safe geometry audit and decision record.
7. Never deploy through the CI workflow. One bounded pilot requires separate explicit authorization and backup/rollback.

Current migration milestone: first wave of private GitHub governance and read-only CI. Full M108 legacy artifact migration is pending, not complete.
