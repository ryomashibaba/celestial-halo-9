# GitHub管理者が行う一度限りの保護設定

1. Settings → General で Private を確認。
2. Settings → Rules → Rulesets（利用可能なら）で main に PR必須、force-push禁止、削除禁止を設定。
3. このDraft PRの Actions 成功確認後、required status check に governance-and-tests を追加。
4. GitHub Actions の default GITHUB_TOKEN は read-only を維持。自動mergeは禁止。
5. CODEOWNERS はセルフレビューを完全に阻止する機能ではない。保護・管理者バイパス条件を理解して運用する。
6. Free private repository で ruleset が制限される場合は、機械的強制を保証しない。mainは承認後だけ更新し、未承認案をDraft PRのまま保持。
7. 実ワールドの書き込み権限・認証情報をGitHub Actionsに与えない。

このリポジトリの正式比較基準はM101。憲法は2026-10-12にユーザー承認済み。基準昇格と施工は別の承認が必要です。
