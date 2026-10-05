#!/usr/bin/env python3
"""Validate the repository before it can be packaged or released.

Every check here exists because the failure it catches is silent. A malformed
description means the skill never triggers and nobody sees an error. A version
that disagrees between the changelog and the marketplace manifest installs the
wrong thing. A reference file the skill points at but does not ship leaves the
model following a dead link mid-build. A plugin folder without its own manifest
installs in Claude Code and fails in the Claude apps behind a generic sync error.
None of these break a build on their own, so the build has to be taught to care.

    python3 scripts/validate.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - the message is the point
    print("PyYAML is required: python3 -m pip install pyyaml==6.0.2", file=sys.stderr)
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())

# Agent Skills open standard.
MAX_NAME = 64
MAX_DESCRIPTION = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# OpenAI presentation metadata.
INTERFACE_KEYS = {"display_name", "short_description", "icon_small", "icon_large",
                  "brand_color", "default_prompt"}
INTERFACE_REQUIRED = {"display_name", "short_description"}
POLICY_KEYS = {"allow_implicit_invocation"}

# Anything that looks like a credential. Deliberately noisy rather than clever:
# a false positive costs one line of review, a false negative ships a key.
SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "OpenAI-style secret key"),
    (re.compile(r"\bpk_(live|test)_[A-Za-z0-9]{10,}"), "publishable key"),
    (re.compile(r"\bsa_live_[A-Za-z0-9]{10,}"), "Customer.io service-account token"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bntn_[A-Za-z0-9]{20,}"), "Notion integration token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
]
PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b|<PLACEHOLDER>", re.I)
HTTP_RE = re.compile(r"http://[^\s`\"'<>)\]]+")

errors: list[str] = []


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(ROOT))


def frontmatter(path: pathlib.Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{rel(path)}: no YAML frontmatter")
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: frontmatter is not valid YAML - {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: frontmatter is not a mapping")
        return None
    return data


def check_skills() -> None:
    if not SKILLS:
        errors.append("no skills found under skills/")
    for skill in SKILLS:
        md = skill / "SKILL.md"
        fm = frontmatter(md)
        if fm is None:
            continue

        name = fm.get("name")
        if not name:
            errors.append(f"{rel(md)}: missing `name`")
        else:
            if name != skill.name:
                errors.append(f"{rel(md)}: name `{name}` != directory `{skill.name}`")
            if len(str(name)) > MAX_NAME:
                errors.append(f"{rel(md)}: name is {len(str(name))} chars, max {MAX_NAME}")
            if not NAME_RE.match(str(name)):
                errors.append(f"{rel(md)}: name `{name}` is not lowercase-hyphen-separated")

        desc = fm.get("description")
        if not desc:
            errors.append(f"{rel(md)}: missing `description`")
        elif not isinstance(desc, str):
            errors.append(f"{rel(md)}: description must be a string")
        elif len(desc) > MAX_DESCRIPTION:
            errors.append(f"{rel(md)}: description is {len(desc)} chars, max {MAX_DESCRIPTION}")

        unknown = set(fm) - {"name", "description", "license", "allowed-tools", "metadata"}
        if unknown:
            errors.append(f"{rel(md)}: non-standard frontmatter keys {sorted(unknown)}")


def check_references_resolve() -> None:
    """Every references/<file> the skill names must actually exist.

    The skill delegates its Notion build order and its idea framework to
    reference files. A rename that misses one turns the delegation into a
    dead pointer, and the model improvises the step instead.
    """
    for skill in SKILLS:
        for md in sorted(skill.rglob("*.md")):
            for target in re.findall(r"`(references/[A-Za-z0-9_./-]+\.md)`", md.read_text(encoding="utf-8")):
                if not (skill / target).exists():
                    errors.append(f"{rel(md)}: points at {target}, which does not exist")


def check_openai_metadata() -> None:
    for skill in SKILLS:
        path = skill / "agents" / "openai.yaml"
        if not path.exists():
            errors.append(f"{skill.name}: missing agents/openai.yaml (ChatGPT presentation metadata)")
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel(path)}: not valid YAML - {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{rel(path)}: top level is not a mapping")
            continue

        interface = data.get("interface")
        if not isinstance(interface, dict):
            errors.append(f"{rel(path)}: missing `interface` mapping")
        else:
            missing = INTERFACE_REQUIRED - set(interface)
            if missing:
                errors.append(f"{rel(path)}: interface missing {sorted(missing)}")
            unknown = set(interface) - INTERFACE_KEYS
            if unknown:
                errors.append(f"{rel(path)}: unknown interface keys {sorted(unknown)}")

        policy = data.get("policy")
        if policy is not None:
            if not isinstance(policy, dict):
                errors.append(f"{rel(path)}: `policy` is not a mapping")
            elif set(policy) - POLICY_KEYS:
                errors.append(f"{rel(path)}: unknown policy keys {sorted(set(policy) - POLICY_KEYS)}")


def check_versions() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"VERSION `{version}` is not semver")
        return

    manifest = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugins = manifest.get("plugins", [])
    if not plugins:
        errors.append("marketplace.json lists no plugins")
    for plugin in plugins:
        if plugin.get("version") != version:
            errors.append(
                f"marketplace.json: {plugin.get('name')} is {plugin.get('version')}, VERSION is {version}")
        check_plugin(plugin, version)

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        errors.append(f"CHANGELOG.md has no `## [{version}]` section")


def check_plugin(entry: dict, version: str) -> None:
    """A marketplace entry must install in the Claude apps, not just Claude Code.

    Claude Code accepts a bare skill folder as a plugin, so `claude plugin
    install` succeeds on a layout the Claude apps reject: adding the marketplace
    in Cowork or claude.ai fails with only "Marketplace sync failed". Those apps
    need the plugin folder to hold .claude-plugin/plugin.json, named like the
    marketplace entry, with each skill at skills/<name>/SKILL.md beside it. A
    top-level bin/ directory stops them installing the plugin at all.
    """
    name = entry.get("name")
    source = entry.get("source")
    if not isinstance(source, str) or not source.startswith("./") or ".." in source:
        errors.append(f"marketplace.json: {name} source {source!r} is not a ./ path inside the repository")
        return
    root = (ROOT / source).resolve()

    path = root / ".claude-plugin" / "plugin.json"
    if not path.exists():
        errors.append(f"marketplace.json: {name} source {source} has no .claude-plugin/plugin.json")
        return
    try:
        plugin = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel(path)}: not valid JSON - {exc}")
        return
    if plugin.get("name") != name:
        errors.append(f"{rel(path)}: name `{plugin.get('name')}` != marketplace entry `{name}`")
    if plugin.get("version") != version:
        errors.append(f"{rel(path)}: version is {plugin.get('version')}, VERSION is {version}")

    shipped = sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))
    expected = [s.name for s in SKILLS]
    if shipped != expected:
        errors.append(f"marketplace.json: {name} ships skills {shipped}, skills/ holds {expected}")
    if (root / "bin").exists():
        errors.append(f"marketplace.json: {name} has a top-level bin/, which the Claude apps refuse")


def check_hygiene() -> None:
    # This file is excluded from its own scan: it necessarily contains literal
    # copies of every pattern it hunts for.
    self_path = pathlib.Path(__file__).resolve()
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git/" in str(path) or "/dist/" in str(path):
            continue
        if path.resolve() == self_path:
            continue
        if path.suffix not in {".md", ".yaml", ".json", ".sh", ".py", ""}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel(path)}: looks like a committed {label}")
        if path.suffix == ".md" and PLACEHOLDER_RE.search(text):
            errors.append(f"{rel(path)}: contains an unresolved placeholder (TODO/FIXME/XXX)")
        for url in HTTP_RE.findall(text):
            errors.append(f"{rel(path)}: plaintext http URL {url}")


def main() -> int:
    check_skills()
    check_references_resolve()
    check_openai_metadata()
    check_versions()
    check_hygiene()

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"ok: {len(SKILLS)} skill(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
