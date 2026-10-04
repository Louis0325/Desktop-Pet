# Desktop-Pet

A Windows desktop companion that brings a character from [PhyFriends](https://rareone0602.github.io/phy_friends/) to your desktop. The pet appears in a transparent, borderless window, stays above other windows, and responds to mouse interactions.

## Made with Codex

All development work on this project was carried out using **Codex**. Codex was used to create and refine the desktop application, implement its interactions and animation playback, prepare the character assets for desktop use, and build the executable and installer.

This development credit refers to the desktop application and its implementation. It does not claim that Codex created the original PhyFriends characters or artwork.

## Character Credits and Permission

All characters featured in this project come from **PhyFriends**:

**Original website:** [https://rareone0602.github.io/phy_friends/](https://rareone0602.github.io/phy_friends/)

The characters are used **with permission from the creator of the PhyFriends website**. Thank you to the website creator for allowing these characters to be adapted into a desktop companion.

The original character designs and artwork are credited to their respective creator. This project adapts those existing character assets for a Windows desktop experience; it does not present them as original artwork created for this repository.

Permission to use the characters in this project should not be interpreted as a blanket license for other projects. If you want to reuse, redistribute, or adapt the original character assets separately, contact the original creator for permission.

## Features

- **Transparent, borderless display:** The character appears directly on your desktop without a conventional window frame.
- **Always on top:** The pet remains visible above other windows.
- **Drag to reposition:** Move the pet with the left mouse button. It stays at the position where you release it rather than walking back to a fixed home location.
- **Mouse tracking:** The character's eyes and head follow the mouse pointer.
- **Animated reactions:** Idle animation, blinking, and a greeting reaction make the character feel lively.
- **Adjustable size:** Choose small, medium, or large using the mouse wheel or context menu.
- **Optional taskbar alignment:** Toggle taskbar alignment from the context menu. Dragging the pet releases this alignment.
- **Saved preferences:** The application remembers its position, size, and taskbar alignment settings.
- **Display-change handling:** The application adjusts its position to keep it within the visible desktop area when the monitor layout changes.

## Getting Started

The Windows application files are located in `windows/dist/` when available in your checkout or downloaded package.

### Run Without Installing

Launch `windows/dist/PhyDesktopPet.exe` to start the desktop pet. The packaged executable does not require a separate Python installation.

### Install the Application

Launch `windows/dist/PhyDesktopPet-Setup.exe` and follow the installer instructions. The installer adds a Start menu shortcut and an uninstall entry, with an optional desktop shortcut.

The current installer and application context menu use Traditional Chinese. This README is written in English.

The application does not automatically configure itself to run at Windows startup.

## Controls

| Action | Result |
| --- | --- |
| Hold the left mouse button and drag | Move the pet to a new position. |
| Move the mouse pointer | Let the character follow the pointer with its eyes and head. |
| Double-click the pet | Play a short greeting reaction. |
| Scroll the mouse wheel over the pet | Switch between the available sizes. |
| Right-click the pet | Open the context menu for size, taskbar alignment, and exit. |

To close the application, right-click the pet and choose the exit option at the bottom of the menu. There is no standard title bar or close button.

## Settings and Diagnostics

The application stores its settings and diagnostic logs in:

```text
%APPDATA%\PhyDesktopPet```

- `settings.json`: Saved position, size, and taskbar alignment preferences.
- `pet.log`: Application activity and diagnostic messages.
- `crash.log`: Low-level fault diagnostics, when available.

If the pet is not visible, launch the application again. When an existing instance is detected, the application attempts to bring that pet back into view near the mouse pointer.

If you need to investigate an unexpected shutdown, check the diagnostic logs in the folder above.

## Build from Source

The implementation uses Python, Tkinter, and Pillow. Character frames are generated from the vendored PhyFriends definitions using Node.js and Playwright, then packaged into a Windows executable with PyInstaller.

### Prerequisites

- Windows with Python and Tkinter available.
- Node.js available on your system path.
- The Python packages `Pillow`, `playwright`, and `pyinstaller`.
- Microsoft Edge installed, because the asset-generation script uses Playwright's `msedge` browser channel.
- Inno Setup, if you also want to build the installer.

The existing build instructions use Python 3.14. Run the following commands from the repository root:

```powershell
cd windows
py -3.14 -m pip install Pillow playwright pyinstaller
py -3.14 build_assets.py
py -3.14 -m PyInstaller --noconfirm --clean --onefile --windowed --name PhyDesktopPet --icon assets/phy.ico --add-data "assets;assets" phy_pet.py
```

The executable is written to `windows/dist/PhyDesktopPet.exe`.

To build the installer, run the following from the `windows` directory with the Inno Setup compiler available on your system path:

```powershell
ISCC.exe PhyDesktopPet.iss
```

The installer is written to `windows/dist/PhyDesktopPet-Setup.exe`.

## Project Layout

| Path | Purpose |
| --- | --- |
| `windows/phy_pet.py` | Desktop application, interactions, settings, and process supervision. |
| `windows/generate_frames.js` | Generates SVG animation frames from the original character definitions. |
| `windows/build_assets.py` | Renders the SVG frames into transparent PNG assets. |
| `windows/vendor/` | Vendored PhyFriends character and animation code. |
| `windows/assets/` | Character frames and application icon used by the desktop application. |
| `windows/PhyDesktopPet.iss` | Inno Setup configuration for the Windows installer. |
| `windows/dist/` | Output directory for the executable and installer. |

## Acknowledgments

Thank you to the creator of [PhyFriends](https://rareone0602.github.io/phy_friends/) for the original characters and for granting permission to use them in this project.

This desktop application was made using **Codex**, while the original character identity and artwork remain credited to PhyFriends.
