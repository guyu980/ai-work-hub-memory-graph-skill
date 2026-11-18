"""Find fund workpapers and formal project outputs in their owning folders."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import os
import re
from urllib.parse import unquote

FORMAL = "04_正式交付"
PROJECT_OUTPUTS = ("01_问题清单", "02_交流纪要", "03_研究与分析", FORMAL)
FORMATS = (".md", ".docx", ".pptx", ".xlsx", ".pdf", ".html", ".txt", ".eml",
           ".doc", ".ppt", ".xls", ".xlsm", ".csv", ".htm")
SKIP = {"工作区", "原始资料", "解析文本", "备份", "assets", "backup", "backups", "cache",
        "node_modules", "vendor", "scripts", "templates", "证据", "运行记录", "凭据", "credentials",
        "配置与权限", "源码", "图示", "渲染"}
PURPOSE = re.compile(r"报告|清单|纪要|访谈|问题|复核|比较|策略|募资|募資|季报|季報|简报|简報|说明书|决议|协议|邮件|预算|模型表|成稿|交付|演示|版本|材料|初稿|讨论稿|ppt|pdf|word|excel|deck|report|memo|strategy|email|budget", re.I)
FORM_REQUESTS = {ext[1:]: {ext} for ext in FORMATS}
FORM_REQUESTS.update({"word": {".doc", ".docx"}, "ppt": {".ppt", ".pptx"},
                      "powerpoint": {".ppt", ".pptx"}, "excel": {".xls", ".xlsx", ".xlsm"},
                      "markdown": {".md"}})
QUARTERS = {"一": "1", "二": "2", "三": "3", "四": "4"}
DATE = re.compile(r"(?<!\d)(20\d\d)[-年]?(\d\d)[-月]?(\d\d)(?:日)?(?!\d)")
LINK = re.compile(r"\[([^\]\n]+)\]\((?:<([^>\n]+)>|([^()\s]+))\)")
CURRENT = re.compile(r"当前|現行|现行|最新版|current\b", re.I)
HISTORICAL = re.compile(r"历史|歷史|旧版|旧稿|上一版|前版|追溯当时|previous\b|historical\b", re.I)


def normalized(value):
    value = re.sub(r"第?([一二三四])季[报報]", lambda m: "q" + QUARTERS[m[1]] + " 季报", value.casefold())
    value = re.sub(r"第?([一二三四])季度", lambda m: "q" + QUARTERS[m[1]], value)
    value = re.sub(r"[二〇零一三四五六七八九]{4}(?=年)",
                   lambda m: m[0].translate(str.maketrans("〇零一二三四五六七八九", "00123456789")), value)
    return re.sub(r"\s+", " ", value).strip()


def file_date(value):
    for match in DATE.finditer(value):
        try:
            return date(*map(int, match.groups())).isoformat()
        except ValueError:
            continue
    return ""


def read_text(path):
    try:
        if path.suffix.lower() not in {".md", ".txt"} or path.stat().st_size > 4 * 1024 * 1024:
            return ""
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return ""


def is_allowed_child(path):
    name = path.name.lower()
    return not (path.is_symlink() or name.startswith((".", "~$")) or "备份" in name or name in SKIP)


def current_links(workspace):
    """Only explicit current labels/sections in owner navigation confer current status."""
    result = {}
    for pattern in ("基金/*索引.md", "基金/*/README.md", "项目/*/README.md", "项目/归档/*/README.md"):
        for guide in workspace.glob(pattern):
            if any(p.is_symlink() for p in (guide, *guide.parents) if p != workspace and workspace in p.parents):
                continue
            current_section = False
            for line in read_text(guide).splitlines():
                if line.startswith("#"):
                    current_section = bool(CURRENT.search(line) and not HISTORICAL.search(line))
                for label, angled, plain in LINK.findall(line):
                    if HISTORICAL.search(label) or not (CURRENT.search(label) or (current_section and not HISTORICAL.search(line))):
                        continue
                    target = (guide.parent / unquote((angled or plain).split("#", 1)[0])).resolve()
                    if target.is_relative_to(workspace):
                        result[target] = label
    return result


def output_groups(workspace, scopes):
    for category, patterns in (
        ("funds", ("基金/输出文档", "基金/*/输出文档")),
        ("projects", tuple(f"{base}/输出文档/{folder}" for base in ("项目/*", "项目/归档/*")
                           for folder in PROJECT_OUTPUTS)),
    ):
        if category not in scopes:
            continue
        for pattern in patterns:
            for folder in sorted(workspace.glob(pattern)):
                if not folder.is_dir() or any(p.is_symlink() for p in (folder, *folder.parents)
                                               if p != workspace and workspace in p.parents):
                    continue
                owner = folder.parent.name if category == "funds" else folder.parent.parent.name
                for here, dirs, names in os.walk(folder):
                    directory = Path(here)
                    dirs[:] = [d for d in sorted(dirs) if is_allowed_child(directory / d)
                               and not (directory / d / ".git").exists()]
                    groups = {}
                    for name in sorted(names):
                        path = directory / name
                        if is_allowed_child(path) and path.suffix.lower() in FORMATS and path.is_file():
                            groups.setdefault(path.stem, []).append(path)
                    for paths in groups.values():
                        yield category, owner, paths


def owner_terms(terms, names):
    """Split a Chinese owner immediately followed by a quarter or document purpose."""
    parts = []
    for term in terms:
        name = next((n for n in names if n in term), "")
        if not name:
            parts.append(term.strip("的") or term)
            continue
        before, _, after = term.partition(name)
        parts.append(name)
        for rest in (before, after):
            parts.extend(re.findall(r"[a-z0-9.+-]+|[\u3400-\u9fff]+", rest.strip(" 的")))
    return parts


def output_date(package, name, body):
    for part in reversed(package):
        if value := file_date(part):
            return value, "package"
    if value := file_date(name):
        return value, "filename"
    for line in body.splitlines()[:8]:
        header = re.match(r"^\s*(?:(?:日期|报告日期|编制日期)\s*[：:]\s*)?(20\d\d[-年]\d{1,2}[-月]\d{1,2})", line)
        if header:
            try:
                return date(*map(int, re.findall(r"\d+", header[1]))).isoformat(), "document"
            except ValueError:
                continue
    return "", "unknown"


def search_outputs(workspace, query, *, scopes=("projects", "funds"), aliases=None, allowed=None):
    """Return grouped output originals and sibling formats. Office files are searched by metadata."""
    workspace = workspace.resolve()
    aliases = aliases or {}
    links = current_links(workspace)
    browse = query is None
    query = normalized(query or "")
    requested = {ext for w in re.findall(r"[a-z0-9]+", query) for ext in FORM_REQUESTS.get(w, ())}
    without_format = re.sub(r"[a-z0-9]+", lambda m: " " if m[0] in FORM_REQUESTS else m[0], query)
    words = re.sub(r"最新(?:版)?|现行|当前|请找|查找|帮我找|发给|的版本|current\b|latest\b", " ", without_format).split()
    terms = [w.strip("，。？?、") for w in words if w not in FORM_REQUESTS and w not in {"的", "版", "找"}]
    if not browse and not terms and not requested:
        return []
    results = []
    partial_results = []
    for category, owner, paths in output_groups(workspace, scopes):
        paths = [p for p in paths if allowed is None or allowed(p)]
        selected = [p for p in paths if not requested or p.suffix.lower() in requested]
        if not selected:
            continue
        best = min(selected, key=lambda p: (p not in links, FORMATS.index(p.suffix.lower())))
        relative = best.relative_to(workspace)
        is_formal = FORMAL in relative.parts
        owner_names = normalized(" ".join([owner, *aliases.get(owner, [])]))
        package = relative.parts[relative.parts.index("输出文档") + 1:-1]
        label = links.get(best) or next((links[p] for p in paths if p in links), "")
        package_name = " ".join(p for p in package if p != FORMAL)
        location = normalized(" ".join([best.stem, owner_names, package_name, label, "正式交付" if is_formal else ""]))
        body_path = next((p for p in paths if p.suffix.lower() in {".md", ".txt"}), None)
        body = read_text(body_path) if body_path else ""
        heading = re.search(r"^#\s+(.+)$", body[:6000], re.M)
        title = heading[1].strip() if heading else best.stem
        identity = normalized(best.stem + " " + title)
        period = re.search(r"(20\d{2})[年 _-]*q([1-4])", identity)
        if period:
            location += " 季报 季度报告 quarterly report"

        # A mixed entity + purpose may be typed without spaces in Chinese.
        aliases_here = [owner, *aliases.get(owner, [])]
        if category == "funds" and owner.endswith("基金") and len(owner[:-2]) >= 2:
            aliases_here.append(owner[:-2])
        aliases_here = sorted((normalized(n) for n in aliases_here if n), key=len, reverse=True)
        parts = owner_terms(terms, aliases_here)
        searchable = normalized(body)
        missing = [p for p in parts if p not in location and p not in identity and p not in searchable]
        if missing:
            # Queries combining several topics can span documents. Return clearly labelled
            # nearby files only when a named owner and a separate destination term match.
            has_owner = any(p == normalized(n) for p in parts for n in aliases_here)
            has_topic = any(p not in owner_names and (p in location or p in identity) for p in parts)
            if len(missing) != 1 or not has_owner or not has_topic or not is_formal:
                continue
        name_hits = sum(p in identity for p in parts)
        location_hits = sum(p in location for p in parts)
        # Deliverable requests favor owned artifacts. A generic company lookup still favors its judgment.
        requested_artifact = bool(requested or PURPOSE.search(query))
        score = 6 + 5 * name_hits + 3 * location_hits
        owner_query = category == "funds" and query == normalized(owner)
        if requested_artifact or owner_query:
            score += 25 * name_hits + 12 * location_hits + 15 * is_formal
            if label:
                score += 18
            if (any(p in identity and PURPOSE.search(p) for p in parts)
                    and any(p in owner_names for p in parts)):
                score += 100
            if re.search(r"清[单單]|使用[说說]明", best.stem) and any(p in package_name.casefold() for p in parts):
                score += 20
        if len(parts) > 1 and all(p in owner_names or p in identity for p in parts) and requested_artifact:
            score += 35
        version_date, date_basis = output_date(package, best.name, body)
        body_lines = body.splitlines()
        snippet = max((line for line in body_lines if line.strip() and not line.startswith("#")),
                      key=lambda line: sum(p in normalized(line) for p in parts), default="")
        bucket = partial_results if missing else results
        bucket.append({
            "type": "deliverable" if is_formal else "fund_workpaper" if category == "funds" else "project_output",
            "category": category, "owner": owner,
            "title": title, "source_path": relative.as_posix(), "unmatched_terms": missing, "source_scope": "workspace_root",
            "updated_at": version_date, "date_basis": date_basis, "package": package_name,
            "current_label": label, "reporting_period": f"{period[1]}-Q{period[2]}" if period else "",
            "other_formats": [p.relative_to(workspace).as_posix() for p in paths if p != best],
            "match_excerpt": snippet[:450] or package_name or best.name, "retrieval_score": score,
        })
    return sorted(results or partial_results, key=lambda r: (r["retrieval_score"], r["updated_at"]), reverse=True)
