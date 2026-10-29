#!/usr/bin/env python3
"""
Mechanical checks that the documentation still matches the code. Standard library only, no Tk, no network.

What it checks (each check has a name; `--only NAME` runs one):

  links       every relative link and #anchor in every markdown file resolves
  labels      every **bold** phrase in the guides and the README that is clearly a reference to something on the screen (after press, click, tick, choose, open and
              similar, before "button", "tab" and similar, or alone in a table cell) appears somewhere in the code's strings, or is listed in docs/doc_terms.txt
              (names that belong to the game, Discord, EDMC or another service). A button renamed in the code but not in the guides fails here.
  paths       every "Settings -> WFMT -> A -> B" path in the guides starts with real tab names (the tab names come from the code)
  files       every `name.py` in the docs exists, every `wfmt_*` setting key named in the docs exists in the code, and every `name.json` is a data file the code knows
  comments    every `identifier` or `name.py` named in a docstring or comment of plugin/ exists
  version     the version in plugin/__init__.py, package.json and the newest CHANGELOG heading agree, and the example versions in the guides are the current one

Run it from the repository root (`python scripts/check_docs.py`); it exits 1 when anything fails. tests/test_docs_current.py runs it with the tests, and
.githooks/pre-commit runs it before a commit. Names that are legitimately not in the code are added to docs/doc_terms.txt, one per line, with a comment
saying why: that file is the only place a mismatch can be excused, so every excuse is visible in a review.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sys
import tokenize
import warnings
from typing import Dict, Iterable, List, Set, Tuple

warnings.simplefilter("ignore", SyntaxWarning)       # parsing source files: an odd escape in a string is not this tool's business
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
USER_DOCS = ["README.md"] + [os.path.join("docs", "guide", n) for n in sorted(os.listdir(os.path.join(ROOT, "docs", "guide"))) if n.endswith(".md")]
SKIP_DIRS = {"node_modules", "dist", ".git", "tests", "plugin", "scripts", "images", "docker", "__pycache__"}
TERMS_FILE = os.path.join(ROOT, "docs", "doc_terms.txt")
ARROW = "→"


# --- reading the code ------------------------------------------------------------------------------------------------------------------

def _py_files(folder: str) -> List[str]:
    found = []
    for base, dirs, names in os.walk(os.path.join(ROOT, folder)):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        found += [os.path.join(base, n) for n in names if n.endswith(".py")]
    return sorted(found)


def _norm(text: str) -> str:
    text = text.replace("…", "").replace("...", "").replace(" ", " ").replace("’", "'")
    text = re.sub(r"[`*_]", "", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


_cache: Dict[str, object] = {}


def code_text() -> str:
    """Every string in plugin/ (normalized and joined): what a label in the docs may be found in."""
    if "text" not in _cache:
        parts: List[str] = []
        for path in _py_files("plugin"):
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    parts.append(_norm(node.value))
        _cache["text"] = "\n".join(parts)
    return str(_cache["text"])


def raw_code_text() -> str:
    if "raw" not in _cache:
        chunks = []
        for path in _py_files("plugin"):
            with open(path, encoding="utf-8") as handle:
                chunks.append(handle.read())
        _cache["raw"] = "\n".join(chunks)
    return str(_cache["raw"])


def defined_names() -> Set[str]:
    """Every name the code defines or uses as an attribute, a keyword or a string key: a function, a class, a constant, a method, a parameter, a module."""
    if "names" not in _cache:
        names: Set[str] = set()
        for folder in ("plugin", "tests", "scripts"):
            for path in _py_files(folder):
                names.add(os.path.splitext(os.path.basename(path))[0])
                try:
                    with open(path, encoding="utf-8") as handle:
                        tree = ast.parse(handle.read())
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        names.add(node.name)
                        if not isinstance(node, ast.ClassDef):
                            for arg in node.args.args + node.args.kwonlyargs:
                                names.add(arg.arg)
                    elif isinstance(node, ast.Name):
                        names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        names.add(node.attr)
                    elif isinstance(node, ast.keyword) and node.arg:
                        names.add(node.arg)
                    elif isinstance(node, ast.alias):
                        names.add((node.asname or node.name).split(".")[-1])
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", node.value):
                        names.add(node.value)       # a journal event, a dictionary key, a config key
        _cache["names"] = names
    return _cache["names"]  # type: ignore[return-value]


def allowed_terms() -> Set[str]:
    if "terms" not in _cache:
        terms: Set[str] = set()
        if os.path.exists(TERMS_FILE):
            with open(TERMS_FILE, encoding="utf-8") as handle:
                for line in handle:
                    line = line.split("#", 1)[0].strip()
                    if line:
                        terms.add(_norm(line))
        _cache["terms"] = terms
    return _cache["terms"]  # type: ignore[return-value]


def known_file_names() -> Set[str]:
    """Names of files the code knows: the modules, the scripts, the files shipped in plugin/, and every file name written as a string in the code."""
    if "files" not in _cache:
        found = {os.path.basename(p) for f in ("plugin", "tests", "scripts") for p in _py_files(f)}
        found |= set(os.listdir(os.path.join(ROOT, "scripts")))
        found |= {n for n in os.listdir(os.path.join(ROOT, "plugin"))}
        for folder in ("plugin", "docs", "docker", ".github", ".githooks"):
            for _base, _dirs, names in os.walk(os.path.join(ROOT, folder)):
                found |= set(names)
        found |= set(os.listdir(ROOT))
        found |= set(re.findall(r"[\"']([A-Za-z0-9_\-]+(?:\.[A-Za-z0-9]+)+)[\"']", raw_code_text()))
        _cache["files"] = found
    return _cache["files"]  # type: ignore[return-value]


# --- reading the docs ------------------------------------------------------------------------------------------------------------------

def markdown_files() -> List[str]:
    found = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        found += [os.path.join(base, n) for n in names if n.endswith(".md")]
    return sorted(found)


def _open(path: str):
    return open(path if os.path.isabs(path) else os.path.join(ROOT, path), encoding="utf-8")


def doc_lines(path: str) -> Iterable[Tuple[int, str]]:
    """The lines of a markdown file outside fenced code blocks, with inline code removed."""
    in_code = False
    with _open(path) as handle:
        for number, line in enumerate(handle, start=1):
            if line.startswith("```"):
                in_code = not in_code
                continue
            if not in_code:
                yield number, re.sub(r"`[^`]*`", "", line)


def doc_lines_with_code(path: str) -> Iterable[Tuple[int, str]]:
    """The lines outside fenced code blocks, with inline code kept."""
    in_code = False
    with _open(path) as handle:
        for number, line in enumerate(handle, start=1):
            if line.startswith("```"):
                in_code = not in_code
                continue
            if not in_code:
                yield number, line


def _slug(heading: str) -> str:
    text = re.sub(r"`", "", heading.strip().lower())
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def _anchors(path: str) -> Set[str]:
    found: Set[str] = set()
    counts: Dict[str, int] = {}
    for _number, line in doc_lines_with_code(path):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if match:
            slug = _slug(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", match.group(2)))
            seen = counts.get(slug, 0)
            counts[slug] = seen + 1
            found.add(slug if seen == 0 else f"{slug}-{seen}")
        found.update(re.findall(r'<a id="([^"]+)"', line))
    return found


# --- the checks ------------------------------------------------------------------------------------------------------------------------

def check_links() -> List[str]:
    problems: List[str] = []
    cache: Dict[str, Set[str]] = {}
    for path in markdown_files():
        rel = os.path.relpath(path, ROOT)
        for number, line in doc_lines(path):
            for target in re.findall(r"\]\(([^)\s]+)\)", line):
                if re.match(r"^(https?:|mailto:)", target):
                    continue
                file_part, _, anchor = target.partition("#")
                dest = path if not file_part else os.path.normpath(os.path.join(os.path.dirname(path), file_part))
                if file_part and not os.path.exists(dest):
                    problems.append(f"{rel}:{number}: the link {target} points to a file that does not exist")
                elif anchor and dest.endswith(".md"):
                    if dest not in cache:
                        cache[dest] = _anchors(dest)
                    if anchor.lower() not in cache[dest]:
                        problems.append(f"{rel}:{number}: the link {target} points to a heading that does not exist")
    return problems


# Where a **bold** phrase is a reference to something on the screen and not plain emphasis: after a verb that acts on a control, before a word that names a kind of
# control, or alone in a table cell. Emphasis (**once a minute**, **Worked example.**) is not checked, so a doc can use bold freely without having to excuse it.
_ACTION = r"(?:press|pressing|click|clicking|tick|untick|ticking|choose|choosing|pick|picking|open|opening|select|selecting|switch|turn|use|using|set|toggle|hit)(?:\s+(?:on|off|to))?(?:\s+the)?"
_KIND = r"(?:button|buttons|box|menu|tab|tabs|drop-down|dropdown|window|checkbox|column|page|section|row|dialog|icon|list|setting)"
_UI_CONTEXTS = [
    re.compile(r"\b" + _ACTION + r"\s+\*\*([^*]{2,60}?)\*\*", re.I),
    re.compile(r"\*\*([^*]{2,60}?)\*\*\s+" + _KIND + r"\b", re.I),
]
_CELL = re.compile(r"^\|\s*\*\*([^*|]{2,60}?)\*\*\s*\|")
_CONTROL_HEADER = re.compile(r"button|control|checkbox|setting|menu|tab\b|label|shortcut|key\b", re.I)


def _ui_references(rel: str) -> Iterable[Tuple[int, str]]:
    """(line number, phrase) for every bold phrase in a guide that is clearly a reference to something on the screen."""
    header_is_controls = False
    previous = ""
    for number, line in doc_lines(rel):
        if line.startswith("|") and not previous.startswith("|"):
            header_is_controls = bool(_CONTROL_HEADER.search(line.split("|")[1] if "|" in line[1:] else line))
        previous = line
        for pattern in _UI_CONTEXTS:
            for found in pattern.findall(line):
                yield number, found
        if header_is_controls:
            for found in _CELL.findall(line):
                yield number, found


def check_labels() -> List[str]:
    blob = code_text()
    allowed = allowed_terms()
    problems: List[str] = []
    reported: Set[Tuple[str, str]] = set()
    for rel in USER_DOCS:
        for number, found in _ui_references(rel):
            raw = found.strip()
            phrase = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", raw).strip()
            key = _norm(phrase)
            if not key or ARROW in phrase or key.isdigit() or re.fullmatch(r"[\d,.%+\- ]+", key) or len(phrase.split()) > 8:
                continue
            pieces = [_norm(p) for p in re.split(r"\s*/\s*|\s*,\s*", phrase)] if re.search(r"\s/\s|,", phrase) else [key]
            for piece in pieces:
                if piece and piece not in blob and piece not in allowed and (rel, piece) not in reported:
                    reported.add((rel, piece))
                    problems.append(f"{rel}:{number}: **{raw}** is not a string anywhere in the code (renamed or removed? if it is not on a WFMT screen add it to docs/doc_terms.txt)")
    return problems


def tab_names() -> Set[str]:
    """The Settings tab names, from the code: what notebook.add and the group and page helpers are given."""
    text = raw_code_text()
    names: Set[str] = set()
    for match in re.finditer(r"notebook\.add\([^,]+,\s*text=\"([^\"]+)\"", text):
        names.add(_norm(match.group(1)))
    for match in re.finditer(r"_settings_group\(tabs,\s*\"([^\"]+)\"", text):
        names.add(_norm(match.group(1)))
    for match in re.finditer(r"_stacked_page\(\"([^\"]+)\"", text):
        names.add(_norm(match.group(1)))
    for match in re.finditer(r"lead=\(([^)]*)\)", text):
        names.update(_norm(m) for m in re.findall(r"\"([^\"]+)\"", match.group(1)))
    return names


_PATH = re.compile(r"Settings\s*(?:" + ARROW + r"|->)\s*WFMT\s*(?:" + ARROW + r"|->)\s*([^*`|\n]{1,60})")


def check_paths() -> List[str]:
    """Every Settings path in the guides (Settings -> WFMT -> tab -> sub-tab -> control) starts with a real tab: the text after WFMT must begin with a tab name from the code."""
    tabs = tab_names()
    allowed = allowed_terms()
    problems: List[str] = []
    for rel in USER_DOCS:
        for number, line in doc_lines_with_code(rel):
            for match in _PATH.finditer(re.sub(r"\*\*", "", line)):
                text = _norm(match.group(1))
                if any(text.startswith(tab) and (len(text) == len(tab) or not text[len(tab)].isalnum()) for tab in tabs | allowed):
                    continue
                problems.append(f"{rel}:{number}: the Settings path names '{match.group(1).strip()[:40]}' first, which is not a Settings tab in the code")
    return problems


def check_files() -> List[str]:
    problems: List[str] = []
    files = known_file_names()
    keys = set(re.findall(r"[\"'](wfmt_[a-z0-9_]+)[\"']", raw_code_text()))
    keys |= {n for n in defined_names() if n.startswith("wfmt_")}
    allowed = allowed_terms()
    for path in markdown_files():
        rel = os.path.relpath(path, ROOT)
        if os.path.basename(path) in ("CHANGELOG.md", "ATTRIBUTIONS.md", "THIRD-PARTY-NOTICES.md", "STATUS.md"):
            continue            # history and credits name files that are gone, other projects' files and old setting keys on purpose
        for number, line in doc_lines_with_code(path):
            for name in re.findall(r"`([A-Za-z0-9_./\-]+\.(?:py|json|csv|txt|mjs))`", line):
                base = os.path.basename(name)
                if base not in files and _norm(base) not in allowed and _norm(name) not in allowed:
                    problems.append(f"{rel}:{number}: `{name}` is not a file the code knows (renamed or removed? if it belongs to another project or the game add it to docs/doc_terms.txt)")
            for key in re.findall(r"`(wfmt_[a-z0-9_]+)`", line):
                if key not in keys and not any(k.startswith(key) for k in keys) and _norm(key) not in allowed:
                    problems.append(f"{rel}:{number}: the setting key `{key}` is not in the code")
    return problems


def _comment_texts(path: str) -> List[Tuple[int, str]]:
    """Every docstring and comment of a Python file, with its line number."""
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    found: List[Tuple[int, str]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc and node.body and isinstance(node.body[0], ast.Expr):
                found.append((node.body[0].lineno, doc))
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            found.append((token.start[0], token.string[1:]))
    return found


_STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
_EXTERNAL = {"EDMC", "Tk", "tk", "True", "False", "None", "self", "cls", "json", "os", "sys", "re", "str", "int", "float", "bool", "list", "dict", "set", "tuple", "bytes", "object",
             "print", "len", "min", "max", "sum", "any", "all", "sorted", "open", "range", "zip", "map", "filter", "type", "isinstance", "getattr", "setattr", "hasattr"}
_FILE_SUFFIXES = (".py", ".json", ".csv", ".txt", ".gz", ".part", ".md", ".mjs", ".png", ".ttf", ".tmp", ".zip")


def check_comments() -> List[str]:
    """Identifiers and file names in `backticks` in docstrings and comments of plugin/ that exist nowhere in the code (a renamed or removed function, constant or module)."""
    names = defined_names()
    files = known_file_names()
    allowed = allowed_terms()
    problems: List[str] = []
    for path in _py_files("plugin"):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        for number, text in _comment_texts(path):
            for token in re.findall(r"`([^`\n]{2,80})`", text):
                if " " in token.strip() or token.startswith(("-", "/", "#", "<", "{", "$", "%", "\\")) or "=" in token or "'" in token or '"' in token:
                    continue
                token = token.strip().rstrip("()").rstrip(",.;:")
                if token.endswith(_FILE_SUFFIXES):
                    if os.path.basename(token) not in files and _norm(token) not in allowed and not token.endswith("__init__.py"):
                        problems.append(f"{rel}:{number}: `{token}` is not a file the code knows")
                    continue
                parts = [p for p in re.split(r"[.:]+", token) if p]
                if not parts or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", p) for p in parts):
                    continue
                if not any(("_" in p or re.search(r"[a-z][A-Z]", p)) for p in parts):
                    continue      # plain words and short names are too ambiguous to judge
                if all(p in names or p in _EXTERNAL or p in _STDLIB for p in parts) or _norm(token) in allowed:
                    continue
                missing = [p for p in parts if p not in names and p not in _EXTERNAL and p not in _STDLIB]
                problems.append(f"{rel}:{number}: `{token}` names '{missing[0]}', which is not defined anywhere in the code")
    return problems


def check_version() -> List[str]:
    problems: List[str] = []
    with open(os.path.join(ROOT, "plugin", "__init__.py"), encoding="utf-8") as handle:
        init = re.search(r"__version__\s*=\s*[\"']([^\"']+)[\"']", handle.read())
    with open(os.path.join(ROOT, "package.json"), encoding="utf-8") as handle:
        package = json.load(handle).get("version")
    with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as handle:
        heading = re.search(r"^## (\d+\.\d+\.\d+)", handle.read(), re.M)
    version = init.group(1) if init else "?"
    if package != version:
        problems.append(f"package.json says {package} but plugin/__init__.py says {version}")
    if not heading or heading.group(1) != version:
        problems.append(f"the newest CHANGELOG.md heading is {heading.group(1) if heading else 'missing'} but the version is {version}")
    for rel in ("docs/INSTALL.md", "docs/guide/getting-started.md", "docs/guide/reporting-problems.md", "docs/LINUX_TESTING.md", "docs/TECHNICAL.md"):
        with _open(rel) as handle:
            for number, line in enumerate(handle, start=1):
                for found in re.findall(r"Plugin: v(\d+\.\d+\.\d+)\b(?! \(downloading)|WFMT: (\d+\.\d+\.\d+)|\[(\d+\.\d+\.\d+)\] |WFMT/(\d+\.\d+\.\d+) \(", line):
                    stated = next((f for f in found if f), "")
                    if stated and stated != version:
                        problems.append(f"{rel}:{number}: the example version {stated} is not the current version {version}")
    return problems


_LABEL_LINE = re.compile(r"^\*\*[^*]+\*\*")
_NOT_A_LEAD = re.compile(r"^\*\*(status|author|work in progress)", re.I)


def check_headers() -> List[str]:
    """Every page opens the same way: one # title, then a lead paragraph saying what the page is.

    A status or author note comes after the lead (as bullets), never as bold lines run together above it, and a page never goes straight from
    the title to a ## section. README.md opens with its logo, so only its title is checked.
    """
    problems: List[str] = []
    docs = ["README.md"] + sorted(
        os.path.join(base, n)[len(ROOT) + 1:] for folder in ("docs",) for base, _d, names in os.walk(os.path.join(ROOT, folder)) for n in names if n.endswith(".md")
    )
    for rel in docs:
        with _open(rel) as handle:
            lines = handle.read().splitlines()
        titles = [i for i, line in enumerate(lines) if line.startswith("# ")]
        if not titles:
            problems.append(f"{rel}:1: no # title")
            continue
        top = titles[0]
        if rel == "README.md":
            continue
        if any(line.strip() for line in lines[:top]):
            problems.append(f"{rel}:1: the # title must be the first line")
        after = [(i, line) for i, line in enumerate(lines[top + 1:], start=top + 1) if line.strip()]
        if not after:
            problems.append(f"{rel}:{top + 1}: nothing after the title")
            continue
        first_index, first = after[0]
        if first.startswith("#"):
            problems.append(f"{rel}:{first_index + 1}: a lead paragraph (what this page is, who it is for) must come between the title and '{first.strip()[:40]}'")
        elif _NOT_A_LEAD.match(first):
            problems.append(f"{rel}:{first_index + 1}: open with a lead paragraph; put the status or author note after it as a bullet")
        for (i, a), (j, b) in zip(after, after[1:]):
            if j > first_index + 12:
                break
            if j == i + 1 and _LABEL_LINE.match(a) and _LABEL_LINE.match(b):
                problems.append(f"{rel}:{j + 1}: two bold label lines in a row run together into one paragraph; make them bullets")
    return problems


CHECKS = {"links": check_links, "labels": check_labels, "paths": check_paths, "files": check_files, "comments": check_comments, "version": check_version, "headers": check_headers}


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Check that the documentation matches the code.")
    parser.add_argument("--only", choices=sorted(CHECKS), help="run one check")
    parser.add_argument("--summary", action="store_true", help="print only how many problems each check found")
    args = parser.parse_args(argv)
    failed = 0
    for name in ([args.only] if args.only else list(CHECKS)):
        problems = CHECKS[name]()
        failed += len(problems)
        print(f"{name}: {len(problems)} problem{'s' if len(problems) != 1 else ''}")
        if not args.summary:
            for problem in problems:
                print("  " + problem)
    return 1 if failed else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
