#!/usr/bin/env python3
"""Mechanical checks for a drafted PR title and body (pr-authoring skill).

Standard library only. Exit code 1 when any ERROR is found, else 0.
This validates form, not truth: claims still need manual evidence review.
"""
import argparse
import re
import sys

TYPES = "feat|fix|perf|refactor|docs|test|build|ci|chore|style|revert"
TITLE_RE = re.compile(rf"^({TYPES})(\([A-Za-z0-9._/-]+\))?!?: \S.*$")
CJK_RE = re.compile(r"[㐀-鿿　-〿＀-￯]")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕️‍]")
ZH_HEADING = "## 中文摘要"
PLACEHOLDERS = [
    re.compile(r"\b(BEFORE|AFTER)_ASSET\b"),
    re.compile(r"\[[A-Z][A-Z _/-]{3,}\]"),
    re.compile(r"\[(What|Mechanism|Actual|Measured|Verified|Explain|Review|Replace|Embed|Area|Metric|Describe)\b[^\]]*\]"),
    re.compile(r"\[(精简翻译|实现和行为|真实结果|如适用)[^\]]*\]"),
    re.compile(r"(?i)\b(lorem ipsum|TODO|TBD|FIXME)\b"),
    re.compile(r"(?i)\b(Closes|Fixes|Resolves|Related to)\s+#(123|0|1234|XXX)\b"),
]
LOCAL_PATH_RE = re.compile(
    r"([A-Za-z]:\\|file://|(?<![\w/.-])/(tmp|home|mnt|Users|var)/|\blocalhost\b|127\.0\.0\.1|\[::1\])"
)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]*)")
FOOTER_RE = re.compile(r"(?i)generated with|co-authored-by|assisted-by|disclosure")


def strip_fences(lines):
    """Return (prose_lines_with_index, fence_open_at_end, fences)."""
    out, fence, fences = [], None, []
    for i, line in enumerate(lines):
        m = re.match(r"^\s*(```+|~~~+)\s*([\w-]*)", line)
        if m:
            if fence is None:
                fence = (m.group(1)[:3], m.group(2), i)
            elif line.strip().startswith(fence[0]):
                fences.append((fence[1], fence[2], i))
                fence = None
            continue
        if fence is None:
            out.append((i, line))
    return out, fence, fences


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("body", help="Markdown body file")
    ap.add_argument("--title", help="PR title to check")
    ap.add_argument("--upstream-english-only", action="store_true",
                    help="Target forbids Chinese: no CJK allowed in body")
    ap.add_argument("--allow-local-paths", action="store_true",
                    help="Pre-upload body that references --attach inputs")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    errors, warns = [], []
    err = lambda m: errors.append(m)
    warn = lambda m: warns.append(m)

    if args.title is not None:
        t = args.title
        if not TITLE_RE.match(t):
            err("title: expected '<type>(<scope>): <summary>' with type in " + TYPES.replace("|", "/")
                + " (skip only if upstream defines another format)")
        if t.endswith("."):
            err("title: no final period")
        if CJK_RE.search(t):
            err("title: must be English only")
        if EMOJI_RE.search(t):
            err("title: no emoji")
        if len(t) > 100:
            err(f"title: {len(t)} chars, keep under 100")
        elif len(t) > 72:
            warn(f"title: {len(t)} chars, prefer 50-72")

    text = open(args.body, encoding="utf-8").read()
    lines = text.splitlines()
    prose, open_fence, fences = strip_fences(lines)
    if open_fence:
        err(f"line {open_fence[2] + 1}: unclosed code fence")

    for i, line in prose:
        if re.match(r"^# \S", line):
            err(f"line {i + 1}: no '# ' title heading in body, use '##'")

    zh_idx = next((i for i, l in prose if l.strip() == ZH_HEADING), None)
    if args.upstream_english_only:
        if zh_idx is not None:
            err("Chinese section present but upstream is English-only")
        if CJK_RE.search(text):
            err("CJK text present but upstream is English-only")
        en_end, zh_lines = len(lines), []
    elif zh_idx is None:
        err(f"missing '{ZH_HEADING}' section (use --upstream-english-only if upstream forbids Chinese)")
        en_end, zh_lines = len(lines), []
    else:
        en_end = zh_idx
        later = [l for i, l in prose if i > zh_idx and l.startswith("## ")]
        if later:
            err("Chinese summary must be the last '##' section")
        zh_lines = lines[zh_idx + 1:]
        # attribution footer: last '---' followed only by footer-ish lines
        for j in range(len(zh_lines) - 1, -1, -1):
            if zh_lines[j].strip() == "---":
                tail = [x for x in zh_lines[j + 1:] if x.strip()]
                if tail and all(FOOTER_RE.search(x) for x in tail):
                    zh_lines = zh_lines[:j]
                elif tail:
                    warn("content after final '---' is not a recognised attribution footer")
                break
        zh_text = "\n".join(zh_lines)
        if len(zh_text.strip()) == 0:
            err("Chinese section is empty")
        elif not CJK_RE.search(zh_text):
            err("Chinese section contains no Chinese text")
        if EMOJI_RE.search(zh_text):
            err("Chinese section: no emoji")
        if re.search(r"!\[|<img|<video|<picture|<svg|<details|<summary", zh_text, re.I):
            err("Chinese section: no images, video or collapsible HTML")
        if re.search(r"^\s*\|.*\|\s*$", zh_text, re.M):
            err("Chinese section: no tables")
        if re.search(r"```|~~~", zh_text):
            err("Chinese section: no code fences or diagrams")
        if re.search(r"^\s*[-*] \[[ xX]\]", zh_text, re.M):
            err("Chinese section: no checklist widgets")
        if re.search(r"https?://", zh_text):
            warn("Chinese section: avoid duplicating links; keep them in English")
        if re.search(r"(?i)\b(closes|fixes|resolves)\s+#\d+", zh_text):
            err("Chinese section: closing keywords belong in English only")
        if zh_text.strip() and len(zh_text.strip()) > 1500:
            warn("Chinese section is long; a concise translation is expected")

    en_text = "\n".join(lines[:en_end])
    if not args.upstream_english_only and CJK_RE.search("\n".join(l for i, l in prose if i < en_end)):
        err("English section contains CJK text")
    emoji_in_headings = [l for i, l in prose if i < en_end and l.startswith("#") and EMOJI_RE.search(l)]
    if len(emoji_in_headings) > 6:
        warn(f"{len(emoji_in_headings)} emoji headings; budget is about 3-6")
    for l in emoji_in_headings:
        if len(re.findall("[🌀-🫿☀-➿⭐⭕]", l)) > 1:
            warn(f"more than one emoji in heading: {l.strip()}")

    for pat in PLACEHOLDERS:
        for i, l in prose:
            if pat.search(l):
                err(f"line {i + 1}: placeholder or example text: {pat.search(l).group(0)}")
    for i, l in prose:
        m = LOCAL_PATH_RE.search(l)
        if m and not args.allow_local_paths:
            err(f"line {i + 1}: local path or host in body: {m.group(0)}")
    for i, l in prose:
        for alt, url in IMG_RE.findall(l):
            if not alt.strip():
                err(f"line {i + 1}: image without alt text")
            if not re.match(r"https://", url) and not args.allow_local_paths:
                err(f"line {i + 1}: image URL is not https: {url}")
            if re.search(r"(?i)(token=|X-Amz-|Expires=|sig=)", url):
                err(f"line {i + 1}: expiring or tokenised URL in body")

    if any(lang.lower() == "mermaid" for lang, _, _ in fences):
        for lang, start, end in fences:
            if lang.lower() == "mermaid":
                block = "\n".join(lines[start + 1:end])
                if not re.match(r"\s*(flowchart|graph|sequenceDiagram|stateDiagram|classDiagram|erDiagram|gantt|journey|timeline)\b", block):
                    err(f"line {start + 1}: mermaid block lacks a diagram type")
                nodes = len(set(re.findall(r"\b([A-Za-z]\w*)\s*[\[\(\{]", block)))
                if nodes > 12:
                    warn(f"line {start + 1}: mermaid has about {nodes} nodes; prefer 3-8")

    if re.search(r"^\s*[-*] \[[xX]\]", en_text, re.M):
        warn("checked checklist items present: confirm each is verified, not assumed")

    for m in errors:
        print("ERROR:", m)
    for m in warns:
        print("WARN: ", m)
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
