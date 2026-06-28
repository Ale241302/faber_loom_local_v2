"""FaberLoom desktop installer (SL4).

Provides a terminal-free, double-click installer for dogfood internal builds.
When packaged with PyInstaller it embeds ``FaberLoom.exe`` and installs it to the
user's local programs directory, creating Start Menu and desktop shortcuts.

For production distribution replace the self-signed executable signature with a
real Authenticode certificate (PRC-05) and optionally switch the installer
backend to NSIS/Inno Setup; the interface in ``build.py`` stays the same.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


APP_NAME = "FaberLoom"
SELF_SIGNED_WARNING = (
    "This is an internal dogfood build signed with a self-signed certificate. "
    "Windows may show a SmartScreen warning. For external distribution the build "
    "must be signed with a real Authenticode certificate (PRC-05)."
)


def _is_frozen() -> bool:
    """Return True when running inside a PyInstaller bundle."""

    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_embedded_executable() -> Path | None:
    """Return the path to the bundled FaberLoom executable, if any."""

    if _is_frozen():
        return Path(sys._MEIPASS) / "FaberLoom.exe"  # type: ignore[literal-required]
    return None


def get_default_install_dir(app_name: str = APP_NAME) -> Path:
    """Return the default per-user install directory.

    Using ``%LOCALAPPDATA%\\Programs`` avoids requiring administrator privileges.
    """

    local_appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(local_appdata) / "Programs" / app_name


def get_start_menu_dir() -> Path:
    """Return the user's Start Menu programs folder."""

    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def get_desktop_dir() -> Path:
    """Return the user's Desktop folder."""

    return Path(os.path.expanduser("~")) / "Desktop"


def create_shortcut(lnk_path: Path, target: Path, description: str = "") -> bool:
    """Create a Windows ``.lnk`` shortcut using PowerShell.

    Returns ``True`` if the shortcut was created.  If PowerShell is unavailable
    the function fails gracefully and returns ``False``.
    """

    if sys.platform != "win32":
        return False

    ps = (
        f"$WshShell = New-Object -comObject WScript.Shell; "
        f"$Shortcut = $WshShell.CreateShortcut('{lnk_path.as_posix()}'); "
        f"$Shortcut.TargetPath = '{target.as_posix()}'; "
        f"$Shortcut.WorkingDirectory = '{target.parent.as_posix()}'; "
        f"$Shortcut.Description = '{description}'; "
        "$Shortcut.Save()"
    )
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return lnk_path.exists()
    except Exception:
        return False


def install_app(
    source_exe: Path,
    install_dir: Path,
    *,
    app_name: str = APP_NAME,
    create_desktop_shortcut: bool = True,
) -> dict[str, Any]:
    """Install *source_exe* into *install_dir* and create shortcuts.

    Returns a dict with the installed executable path and shortcut paths.
    Raises ``RuntimeError`` if the source executable cannot be copied.
    """

    source_exe = Path(source_exe).resolve()
    if not source_exe.exists():
        raise FileNotFoundError(f"Source executable not found: {source_exe}")

    install_dir = Path(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)

    installed_exe = install_dir / f"{app_name}.exe"
    shutil.copy2(source_exe, installed_exe)

    # Write a tiny uninstall helper batch (no terminal required because it is
    # launched from the Start Menu shortcut as a GUI action).
    uninstall_bat = install_dir / "uninstall.bat"
    uninstall_bat.write_text(
        f"@echo off\nrmdir /s /q \"{install_dir}\"\n",
        encoding="utf-8",
    )

    start_menu = get_start_menu_dir()
    start_menu.mkdir(parents=True, exist_ok=True)
    start_lnk = start_menu / f"{app_name}.lnk"
    start_ok = create_shortcut(start_lnk, installed_exe, description=app_name)

    desktop_lnk: Path | None = None
    desktop_ok = False
    if create_desktop_shortcut:
        desktop_lnk = get_desktop_dir() / f"{app_name}.lnk"
        desktop_ok = create_shortcut(desktop_lnk, installed_exe, description=app_name)

    return {
        "installed_exe": str(installed_exe),
        "install_dir": str(install_dir),
        "start_menu_shortcut": str(start_lnk) if start_ok else None,
        "desktop_shortcut": str(desktop_lnk) if desktop_ok else None,
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FaberLoom terminal-free installer",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Install without showing the GUI (requires --install-dir).",
    )
    parser.add_argument(
        "--install-dir",
        type=Path,
        help="Target installation directory (used with --silent).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Path to FaberLoom.exe (defaults to bundled executable).",
    )
    return parser.parse_args(argv)


def _run_silent_install(args: argparse.Namespace) -> int:
    source = args.source or get_embedded_executable()
    if source is None:
        print("error: no source executable provided and none bundled", file=sys.stderr)
        return 1

    install_dir = args.install_dir or get_default_install_dir()
    result = install_app(source, install_dir)
    print(f"installed={result['installed_exe']}")
    print(f"start_menu={result['start_menu_shortcut']}")
    print(f"desktop={result['desktop_shortcut']}")
    return 0


def _run_gui() -> int:
    """Run the tkinter installer GUI."""

    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:  # pragma: no cover - GUI unavailable
        print(f"error: tkinter is required for the GUI installer: {exc}", file=sys.stderr)
        return 1

    source = get_embedded_executable()

    root = tk.Tk()
    root.title(f"{APP_NAME} Installer")
    root.geometry("520x280")
    root.resizable(False, False)

    install_dir = tk.StringVar(value=str(get_default_install_dir()))
    status = tk.StringVar(value="Ready to install.")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=f"Install {APP_NAME}", font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)

    warning = ttk.Label(
        frame,
        text=SELF_SIGNED_WARNING,
        wraplength=480,
        foreground="#555",
        justify=tk.LEFT,
    )
    warning.pack(anchor=tk.W, pady=(10, 10))

    dir_frame = ttk.Frame(frame)
    dir_frame.pack(fill=tk.X, pady=(0, 10))
    ttk.Label(dir_frame, text="Install to:").pack(side=tk.LEFT)
    ttk.Entry(dir_frame, textvariable=install_dir, width=40).pack(side=tk.LEFT, padx=(5, 5))

    def browse() -> None:
        path = filedialog.askdirectory(initialdir=install_dir.get())
        if path:
            install_dir.set(path)

    ttk.Button(dir_frame, text="Browse...", command=browse).pack(side=tk.LEFT)

    progress = ttk.Progressbar(frame, mode="indeterminate")

    def do_install() -> None:
        target = Path(install_dir.get())
        src = source
        if src is None or not src.exists():
            messagebox.showerror(
                "Error",
                "No FaberLoom executable found. Run the installer from a packaged build.",
            )
            return

        status.set("Installing...")
        progress.pack(fill=tk.X, pady=(10, 10))
        progress.start()
        root.update()

        try:
            result = install_app(src, target)
            progress.stop()
            progress.pack_forget()
            status.set(f"Installed to {result['install_dir']}")
            messagebox.showinfo(
                "Installation complete",
                f"{APP_NAME} has been installed.\n\n"
                f"Start Menu shortcut: {result['start_menu_shortcut'] or 'not created'}\n"
                f"Desktop shortcut: {result['desktop_shortcut'] or 'not created'}",
            )
            root.destroy()
        except Exception as exc:  # pragma: no cover
            progress.stop()
            progress.pack_forget()
            status.set("Installation failed.")
            messagebox.showerror("Installation failed", str(exc))

    ttk.Button(frame, text=f"Install {APP_NAME}", command=do_install).pack(anchor=tk.W, pady=(10, 5))
    ttk.Label(frame, textvariable=status).pack(anchor=tk.W)

    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.silent:
        return _run_silent_install(args)
    return _run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
