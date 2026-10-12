# Explicit approval gates

| Activity | Default |
|---|---|
| Offline design, code, non-construction QA | ALLOWED on work branches |
| Work-branch push and PR creation | ALLOWED |
| Formal M101 comparison baseline replacement | HOLD for explicit user approval |
| Project constitution / protected rules alteration | HOLD for explicit user approval |
| Read private world snapshot / share source externally | Scope- and access-dependent |
| Freeze, canonical or staging mutation | HOLD for explicit user approval |
| Any live Minecraft write, edit, destruction or deployment | HOLD for a separate bounded authorization |
| Paid service, server, credential creation | HOLD pending cost/scope approval |

A GitHub PR, CI PASS, code comment, emoji or general work authorization is NOT a world-write approval.
A future construction approval must bind precise world snapshot/hash, bounding region, change manifest/hash, rollback artifact, and user consent.
