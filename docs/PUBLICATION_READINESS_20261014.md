# CELESTIAL HALO-9 — publication readiness (2026-10-14)

**STATE: PRIVATE / FINAL VISIBILITY CONVERSION NOT AUTHORIZED.** This checklist is explanatory, not a permit to change repository settings, protected baselines, CI governance, or Minecraft worlds.

## Audited and accepted

- The owner chose to pursue **public release of the existing repository**, including user-created city 3D design models and the M117 read-only old-city material atlas.
- The owner **explicitly accepted public exposure of historic personal Gmail author metadata across 18 commits and the Windows username in the local Work setup report**. Do not rewrite public history solely to mask those accepted facts. No actual email address or username is reproduced here.
- Security pre-publication scan examined 13 branches; 18 reachable authored commits; 121 tracked files (Git tree verified); 12 existing Draft PRs; 20 Issue/PR threads and 13 Issue comments; 2 historically deleted files. Common token/private-key/credential regex checks found no confirmed leaked secrets in those inspected surfaces. Detection is not a proof that all possible secrets are absent.
- GitHub Actions: 43 runs, 42 successful run logs inspected for common secrets/home paths/emails/webhooks with **zero indicated matches**; the latest failure had 0 runner steps, inaccessible log, so it is not claimed screened. Workflow checked for `permissions: contents: read`, `persist-credentials: false`, and no Minecraft deploy.
- GitHub repo is still Private. Existing `main` and the stacked Draft PRs remain untouched by this public-facing preparation.

## Still requires owner decision/action

1. **License policy:** retain no license (default all-rights-reserved except GitHub terms) OR owner chooses an explicit permissive/copyleft license. No license has been added by this proposal.
2. **Public visibility:** require an explicit, separate instruction such as *「既存のcelestial-halo-9をPublicに変更してよい」*. Previous acceptance only approved release of certain personal identifiers and the public-release preparation process.
3. **Landing page / integration:** `main` is an intentionally minimal bootstrap; M108–M121 research remains stacked, Draft and unmerged, so the latest integrated README here is not automatically the default-branch README. Any merge/base change requires its own review, policy compliance and explicit approval where applicable.
4. **Actions on public:** standard GitHub-hosted public runners are normally provided free of private-minute billing; still review account/action settings. Visibility change may disable push rulesets, so inspect protections before and after. Do not mark the currently failing private CI run as passed.
5. **External PR security:** `pull_request` can run third-party contributor code in CI. Current permissions read-only; keep them least-privileged, avoid `pull_request_target` execution of untrusted code, and separately review action version pinning.

## Public information intentionally disclosed

- Historical authorship metadata and Work setup path, as the owner explicitly accepted.
- Offline Minecraft building material coordinates, world name and review-folder suffix/hashes, architectural sketches and procedural 3D research source.
- Draft design ideas and unresolved conflict checks. Design candidate B is **not** an approved or construction-ready scheme.

## Non-actions

No changes to visibility, account data, secrets, `main`, previous PRs, governance, `.github/`, freezes, Canonical/Staging, or Minecraft saves. No license inserted and no design promotion.
