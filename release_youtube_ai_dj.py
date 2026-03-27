from __future__ import annotations

import datetime as dt
import os
import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
INDEX_PATH = ROOT / "index.html"
README_PATH = ROOT / "README.md"
ROADMAP_PATH = ROOT / "ROADMAP.md"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
BACKUPS_DIR = ROOT / "backups"
TIMEZONE_LABEL = "America/Chicago"


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: pathlib.Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n")
    literal_path = str(path).replace("'", "''")
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$inputData = [Console]::In.ReadToEnd(); Set-Content -LiteralPath '{literal_path}' -Value $inputData -Encoding UTF8",
        ],
        input=normalized,
        text=True,
        encoding="utf-8",
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def bump_patch(version: str) -> str:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Unsupported version format: {version}")
    major, minor, patch = map(int, match.groups())
    return f"v{major}.{minor}.{patch + 1}"


def extract_version(readme_text: str) -> str:
    match = re.search(r"Version:\s*`(v\d+\.\d+\.\d+)`", readme_text)
    if not match:
        raise ValueError("Could not find version in README.md")
    return match.group(1)


def replace_required(pattern: str, repl: str, text: str, label: str) -> str:
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Could not update {label}")
    return updated


def make_backup(stamp: str) -> pathlib.Path:
    backup_dir = BACKUPS_DIR / stamp
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"New-Item -ItemType Directory -Path '{backup_dir}' -Force | Out-Null",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for path in (INDEX_PATH, README_PATH, ROADMAP_PATH, CHANGELOG_PATH):
        if path.exists():
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Copy-Item -LiteralPath '{path}' -Destination '{backup_dir / path.name}' -Force",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    return backup_dir


def prompt_release_note(version: str) -> str:
    print()
    print(f"New version: {version}")
    note = input("Enter a short release note: ").strip()
    if not note:
        raise ValueError("Release note is required.")
    return note


def update_index(text: str, new_version: str) -> str:
    text = replace_required(
        r"<title>YouTube AI DJ v\d+\.\d+\.\d+</title>",
        f"<title>YouTube AI DJ {new_version}</title>",
        text,
        "index title",
    )
    text = replace_required(
        r"Version v\d+\.\d+\.\d+\.",
        f"Version {new_version}.",
        text,
        "setup version text",
    )
    text = replace_required(
        r"AI</span> DJ <span style=\"color:var\(--text3\);font-weight:500;\">v\d+\.\d+\.\d+</span>",
        f"AI</span> DJ <span style=\"color:var(--text3);font-weight:500;\">{new_version}</span>",
        text,
        "header version text",
    )
    return text


def update_readme(text: str, new_version: str, note: str, backup_rel: str) -> str:
    text = replace_required(
        r"Version:\s*`v\d+\.\d+\.\d+`",
        f"Version: `{new_version}`",
        text,
        "README version",
    )
    text = replace_required(
        r"Latest release note:\s*`v\d+\.\d+\.\d+\s*-\s*[^`]+`",
        f"Latest release note: `{new_version} - {note}`",
        text,
        "README latest release note",
    )
    text = replace_required(
        r"- Timestamped local backup saved at `[^`]+`",
        f"- Timestamped local backup saved at `{backup_rel}`",
        text,
        "README backup path",
    )
    return text


def update_roadmap(text: str, new_version: str) -> str:
    return replace_required(
        r"Current version:\s*`v\d+\.\d+\.\d+`",
        f"Current version: `{new_version}`",
        text,
        "ROADMAP version",
    )


def update_changelog(existing_text: str, new_version: str, note: str, now: dt.datetime) -> str:
    header = "# YouTube AI DJ Changelog\n\nLatest first.\n"
    body = existing_text.strip()
    if not body.startswith("# YouTube AI DJ Changelog"):
        body = header
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n\n## {new_version} - {timestamp} {TIMEZONE_LABEL}\n\n"
        f"- {note.strip().rstrip('.') }.\n"
    )
    if body.startswith(header.strip()):
        remainder = body[len(header.strip()):].lstrip()
        return header + entry.strip() + ("\n\n" + remainder if remainder else "") + "\n"
    return body + entry + "\n"


def run_git(note: str, version: str) -> None:
    root = str(ROOT)
    subprocess.run(["git", "-C", root, "add", "."], check=True)
    subprocess.run(["git", "-C", root, "commit", "-m", f"{version}: {note}"], check=True)
    subprocess.run(["git", "-C", root, "push", "origin", "HEAD"], check=True)


def git_has_changes() -> bool:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return bool(result.stdout.strip())


def choose_mode(current_version: str) -> str:
    print(f"Current version: {current_version}")
    print("1. New release")
    print("2. Commit/push existing changes only")
    choice = input("Choose mode [1/2]: ").strip()
    if choice == "2":
        return "commit_only"
    return "release"


def commit_only_flow(current_version: str) -> int:
    if not git_has_changes():
        print("No uncommitted changes found.")
        return 0

    note = input("Enter a short git note for the current changes: ").strip()
    if not note:
        raise ValueError("Git note is required.")

    run_git(note, current_version)
    print("GitHub update complete.")
    print("Done.")
    return 0


def main() -> int:
    try:
        readme_text = read_text(README_PATH)
        current_version = extract_version(readme_text)
        mode = choose_mode(current_version)
        if mode == "commit_only":
            return commit_only_flow(current_version)

        new_version = bump_patch(current_version)

        now = dt.datetime.now()
        stamp = now.strftime("%Y%m%d-%H%M%S")
        backup_dir = make_backup(stamp)
        backup_rel = backup_dir.relative_to(ROOT).as_posix() + "/"

        note = prompt_release_note(new_version)

        write_text(INDEX_PATH, update_index(read_text(INDEX_PATH), new_version))
        write_text(README_PATH, update_readme(readme_text, new_version, note, backup_rel))
        write_text(ROADMAP_PATH, update_roadmap(read_text(ROADMAP_PATH), new_version))

        changelog_text = read_text(CHANGELOG_PATH) if CHANGELOG_PATH.exists() else "# YouTube AI DJ Changelog\n\nLatest first.\n"
        write_text(CHANGELOG_PATH, update_changelog(changelog_text, new_version, note, now))

        print()
        print(f"Backup created: {backup_dir}")
        print("Files updated:")
        print("- index.html")
        print("- README.md")
        print("- ROADMAP.md")
        print("- CHANGELOG.md")
        print()

        should_push = input("Commit and push to GitHub now? [Y/n]: ").strip().lower()
        if should_push in ("", "y", "yes"):
            run_git(note, new_version)
            print("GitHub update complete.")
        else:
            print("Skipped git commit/push.")

        print("Done.")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
