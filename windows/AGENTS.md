# Desktop pet update and delivery rules

- The user requires every future project update to be synchronized to `C:/Users/yumin/OneDrive/Documents/GitHub/Desktop-Pet/windows`.
- The authoritative project is `C:/Users/yumin/OneDrive/Desktop/其他/桌面寵物`. Make edits there, including when working from the GitHub copy, then synchronize the complete project.
- After changing source, assets, translations, documentation, build scripts, EXE, or installer, run `sync-to-github.ps1` from the authoritative project before reporting completion.
- For executable releases, run `build-release.ps1`; it rebuilds the EXE and installer and synchronizes only after both builds succeed.
- Verify the synchronized files match the authoritative project. Do not commit or push unless requested. Preserve the GitHub repository's root files and Git metadata.
- Keep transparent, draggable, always-on-top behavior, mouse gaze, automatic menu language, and placement at the absolute screen bottom. Manual dragging must not force the pet back above the taskbar.

