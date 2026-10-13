# M116 — distinguish world copies before any construction (NON-CONSTRUCTION)

The user tentatively believes the screenshot came from the review copy. This is **not a verified world identity** or any permission to modify a save.

## Why
Two CurseForge SKYTREE_3500 saves have the SAME in-game LevelName = imagine:
- save folder CH9_D6D_REVIEW_COPY (M115 level.dat SHA ca9410..., 4,476 black concrete/quartz construction blocks in 13 probed chunks)
- save folder imagine (M115 level.dat SHA 5bde40..., only stone in same 13 selected chunks)
Distinct directory names matter. LastPlayed, LevelName and screenshot similarity are supporting evidence, not authoritative identity.

## Direct, user-friendly game UI check
1. On Minecraft Java main menu click Singleplayer.
2. Select the world that shows the user's existing old dark/white buildings.
3. Click Edit, then Open World Folder.
4. Inspect the **last folder name in Windows Explorer**; report whether it is CH9_D6D_REVIEW_COPY, imagine or some other save.
No need to reveal the entire Windows username or private absolute path.

## Software guard added as a defensive reference utility
- survey/identity/M116_world_candidates.json identifies both known candidates using folder tail, last observed level.dat SHA256, and explicit unconfirmed READ-ONLY roles.
- tools/m116_world_identity_guard.py performs read-only path+snapshot comparison. Example:
  python tools/m116_world_identity_guard.py --mode inspect --world "C:\\path\\to\\saves\\CH9_D6D_REVIEW_COPY"
- This tool does NOT parse raw Minecraft blocks. It never writes any world file.
- The --mode construct entry point ALWAYS returns blocked; no construction token is issued.
- Any changed level.dat hash is NOT interpreted as an incorrect save: gameplay can update level.dat. Reconfirmation is required. A cloned save can share a hash, so it is never globally unique identity proof.
- Neither record is formally selected as a live construction target; approved pilot area remains null, world writes disabled under existing separate governance.
- This is an additional **advisory/preflight utility**. It is not automatically wired to every third-party WorldEdit or existing builder, and GitHub CI does not control Minecraft launchers. Before future real construction, every writing pipeline must explicitly integrate and independently enforce an approved-world identity check plus user-signed region, protected masks, and release approval.

## Safety and limitations
No edits to the existing governance constitution, release gate, main or legacy saves. No automatic merge and no current-world construction. No confidence claim that CH9_D6D_REVIEW_COPY is the user's active save. Full geometry / world Y still UNKNOWN.

## Next
When the user has verified the Explorer path of the world they viewed, label screenshot source accordingly. Keep review copy for read-only surveys; identify original authoritative master separately before any later construction.
