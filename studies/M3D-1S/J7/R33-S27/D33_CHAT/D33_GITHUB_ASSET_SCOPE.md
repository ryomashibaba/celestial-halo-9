# D33 GitHub evidence and binary archive scope

Research source only; not official art or construction authorization. **TECH LIMITED PASS / ART REJECT / formal adoption 0 / Minecraft HOLD**.

- Chat artifact ZIP: `HALO9_D33_CHAT_RESEARCH.zip`
- ZIP SHA256: `7091d990b58bbf31e7c55b0ff8898e334d7b11956c8779893c2265a8713780ac`
- ZIP contains 44 files and passed complete SHA256 manifest and ZIP CRC checks.
- GitHub research branch saves Python creators/editor/auditor/tests, native HTML, offline vendor generation script, control cages, README, review and lightweight JSON evidence.
- **GitHub intentionally does not contain actual `.glb` geometry files, generated VTK `.png` renderings, comparison `.jpg` images, browser test screenshots, or the third-party `plotly.min.js` distribution**. These are in the ZIP.
- For rebuilding on a new machine, install declared dependencies and run `python d33_setup_vendor.py` then `python d33_sculpt.py` and `python d33_render.py`. Blender is not required for this technical experiment, but Blender-native direct art sculpt is not demonstrated.
- Chromium in isolated container cannot directly access localhost and lacks WebGL. UI was tested with an actual Chromium browser using a FastAPI TestClient transport shim and a **working actual-GLB VTK six-view fallback**. Do not claim real WebGL rotation or actual browser-localhost transport verified.
- Original city master / `main` / M247-C formal geometry / world not modified; no Work.
