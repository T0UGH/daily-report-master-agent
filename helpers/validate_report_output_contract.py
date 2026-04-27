from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


FIXED_SECTION_ORDER = [
    "weather-watch",
    "x-feed",
    "x-following",
    "reddit-watch",
    "hacker-news-watch",
    "hacker-news-search-watch",
    "claude-code-watch",
    "codex-watch",
    "openclaw-watch",
    "github-ai-projects",
    "github-trending-weekly",
    "product-hunt-watch",
    "polymarket-watch",
]

FIXED_SECTION_TITLES = {
    "x-feed": "X 推荐流",
    "x-following": "X 关注流",
    "reddit-watch": "Reddit 社区",
    "hacker-news-watch": "Hacker News 热榜",
    "hacker-news-search-watch": "Hacker News 搜索",
    "claude-code-watch": "Claude Code",
    "codex-watch": "Codex",
    "openclaw-watch": "OpenClaw",
    "github-ai-projects": "GitHub AI 项目",
    "github-trending-weekly": "GitHub 趋势项目",
    "product-hunt-watch": "Product Hunt 新品",
    "polymarket-watch": "Polymarket 市场",
    "weather-watch": "天气",
}

READER_SECTION_ORDER = [FIXED_SECTION_TITLES[lane] for lane in FIXED_SECTION_ORDER]
READER_SECTION_SET = set(READER_SECTION_ORDER)
LEGACY_MARKERS = ("今日要点", "## 正文", "编辑结论", "### Sources")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
MARKDOWN_LINK_INLINE_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
PLAIN_URL_RE = re.compile(r"https?://[^\s)>]+")
CITATION_WRAPPER_PATTERNS = (
    re.compile(r"<\s*/?\s*citation\b", re.IGNORECASE),
    re.compile(r"```+\s*citation\b", re.IGNORECASE),
    re.compile(r":::\s*citation\b", re.IGNORECASE),
)
BULLET_ITEM_RE = re.compile(r"^[-*+]\s+\S")
BULLET_CONTINUATION_RE = re.compile(r"^(?: {2,}|\t+)\S")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
ENGLISH_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+./_-]*")
LONG_ENGLISH_PHRASE_RE = re.compile(r"\b(?:[A-Za-z][A-Za-z0-9+./_-]*\s+){5,}[A-Za-z][A-Za-z0-9+./_-]*\b")
PLACEHOLDER_COUNT_COPY_RE = re.compile(
    r"(?:该|本|此)栏目(?:共)?(?:收录|整理|汇总|包含)\s*\d+\s*条(?:有用)?(?:内容|信息|信号|动态|更新)(?:[。！!？?]|$)"
)
GENERIC_SOURCE_FALLBACK_RE = re.compile(
    r"原文围绕.+(?:展开|讨论|介绍|说明)[，,].*(?:具体变化|详细变化|具体内容|更多细节).*(?:见来源|见原文|详见来源|详见原文)(?:[。！!？?]|$)"
)
GENERIC_GITHUB_FALLBACK_RE = re.compile(
    r"(?:项目|仓库|README|readme|项目说明|仓库说明)(?:主要)?(?:在讲|介绍)(?:它的)?"
    r"[^。]*(?:定位|目标定位)[^。]*(?:工作流|workflow)[^。]*(?:使用场景|场景)[^。]*(?:[。！!？?]|$)"
)
GENERIC_HN_FILLER_RE = re.compile(
    r"(?:这条 HN 热榜讨论|搜索词「[^」]+」命中的这条 HN 讨论|这条 HN 搜索命中)"
    r"[^。]*(?:不是泛聊概念，而是在(?:追|讲)更具体的工程做法)(?:[。！!？?]|$)"
)
EMPTY_COMMUNITY_JUDGMENT_RE = re.compile(
    r"(?:这说明|值得关注|这条有用是因为|读者可以把它当作|生态继续演进|更像真实工作流|值得保留)"
)
HYBRID_ENGLISH_TAIL_PREFIX_RE = re.compile(
    r"(?:提到|写明了|记录里写到|主打的是|定位很直接[:：]?|摘要里写到|改动主要是|主要更新是|更新是)\s*",
    re.IGNORECASE,
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_report_markdown(
    markdown: str,
    *,
    report_date: str,
    expected_section_titles: list[str] | None = None,
    expected_sources: dict[str, list[str]] | None = None,
) -> None:
    lines = markdown.splitlines()
    first_content_line = next((line.strip() for line in lines if line.strip()), "")
    title_line = f"# AI Agent 日报（{report_date}）"

    require(markdown.startswith(title_line), "标题必须从响应开头开始，第一行必须是 AI Agent 日报（YYYY-MM-DD）")
    require(first_content_line == title_line, "标题必须固定为 AI Agent 日报（YYYY-MM-DD）")

    for marker in LEGACY_MARKERS:
        require(marker not in markdown, f"最终 Markdown 不得包含旧结构: {marker}")

    validate_no_citation_wrappers(markdown)

    appendix_index = find_line_index(lines, "## 来源")
    require(appendix_index is not None, "最终 Markdown 必须包含统一的 ## 来源")

    body_lines = lines[1:appendix_index]
    appendix_lines = lines[appendix_index + 1 :]
    require(not any(line.startswith("### ") for line in body_lines), "正文栏目内不得再嵌套 ### 小节")

    body_sections = parse_h2_sections(body_lines)
    actual_section_titles = [title for title, _ in body_sections]
    expected_titles = expected_section_titles or actual_section_titles
    validate_section_titles(actual_section_titles, expected_titles)

    body_sources = extract_body_sources(body_sections)
    appendix_sources = parse_appendix_sources(appendix_lines)

    expected_sources = expected_sources or body_sources
    require(list(appendix_sources) == list(expected_sources), "文末来源分组顺序必须与预期栏目顺序一致")

    for section_title, urls in expected_sources.items():
        require(section_title in actual_section_titles, f"文末来源引用了正文不存在的栏目: {section_title}")
        require(body_sources.get(section_title, []) == urls, f"{section_title} 的正文段落尾引用与预期不一致")
        require(appendix_sources.get(section_title, []) == urls, f"{section_title} 的文末来源列表与预期不一致")


def validate_fixture_case(case_path: Path, case_data: dict[str, Any]) -> None:
    require(isinstance(case_data, dict), f"{case_path.name} 必须是 object")

    report_date = case_data.get("report_date")
    report_markdown = case_data.get("report_markdown")
    expected_section_titles = case_data.get("expected_section_titles")
    expected_sources = case_data.get("expected_sources")

    require(isinstance(report_date, str) and report_date, f"{case_path.name} 缺少 report_date")
    require(isinstance(report_markdown, str) and report_markdown, f"{case_path.name} 缺少 report_markdown")
    require(isinstance(expected_section_titles, list) and expected_section_titles, f"{case_path.name} 缺少 expected_section_titles")
    require(isinstance(expected_sources, dict) and expected_sources, f"{case_path.name} 缺少 expected_sources")

    expected_titles = [validate_reader_section_title(title, field_name="expected_section_titles") for title in expected_section_titles]
    validate_section_titles(expected_titles, expected_titles)

    normalized_sources: dict[str, list[str]] = {}
    for section_title, urls in expected_sources.items():
        normalized_title = validate_reader_section_title(section_title, field_name="expected_sources")
        require(isinstance(urls, list) and urls, f"{case_path.name}: {section_title} 必须给出非空 URL 列表")
        normalized_urls = validate_url_list(urls, label=f"{case_path.name}: {section_title}")
        normalized_sources[normalized_title] = normalized_urls

    validate_report_markdown(
        report_markdown,
        report_date=report_date,
        expected_section_titles=expected_titles,
        expected_sources=normalized_sources,
    )


def validate_section_titles(actual_titles: list[str], expected_titles: list[str]) -> None:
    require(actual_titles == expected_titles, "正文栏目必须是固定顺序下的非空栏目子序列")

    previous_index = -1
    for title in actual_titles:
        validate_reader_section_title(title, field_name="section_title")
        current_index = READER_SECTION_ORDER.index(title)
        require(current_index > previous_index, "正文栏目顺序必须符合固定顺序")
        previous_index = current_index


def validate_reader_section_title(title: Any, *, field_name: str) -> str:
    require(isinstance(title, str) and title in READER_SECTION_SET, f"{field_name} 只能使用 reader-facing 中文栏目名")
    return title


def validate_url_list(urls: list[Any], *, label: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for url in urls:
        require(isinstance(url, str) and url.startswith(("http://", "https://")), f"{label} 包含非法来源 URL")
        require(url not in seen, f"{label} 不允许重复 URL")
        seen.add(url)
        normalized.append(url)
    return normalized


def find_line_index(lines: list[str], needle: str) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == needle:
            return index
    return None


def parse_h2_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_title is not None:
                finalize_section(sections, current_title, current_lines)
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)
        else:
            require(not line.strip(), "标题后必须直接进入第一个正文栏目，不允许状态、导语或其他前置文本")

    if current_title is not None:
        finalize_section(sections, current_title, current_lines)

    require(sections, "正文必须至少包含一个非空栏目")
    return sections


def finalize_section(sections: list[tuple[str, list[str]]], title: str, lines: list[str]) -> None:
    validate_reader_section_title(title, field_name="section_title")
    require(any(line.strip() for line in lines), f"{title} 不能为空栏目")
    validate_section_body_lines(title, lines)
    sections.append((title, lines))


def validate_no_citation_wrappers(markdown: str) -> None:
    for pattern in CITATION_WRAPPER_PATTERNS:
        require(
            pattern.search(markdown) is None,
            "最终 Markdown 不得包含 citation 样式标签或代码块包裹",
        )


def validate_section_body_lines(title: str, lines: list[str]) -> None:
    saw_bullet_item = False
    inside_bullet_item = False

    for raw_line in lines:
        if not raw_line.strip():
            continue
        if BULLET_ITEM_RE.match(raw_line):
            saw_bullet_item = True
            inside_bullet_item = True
            validate_body_line_content_quality(title, raw_line)
            continue
        require(
            inside_bullet_item and BULLET_CONTINUATION_RE.match(raw_line) is not None,
            f"{title} 的正文必须使用 bullet-style reader items，不允许散文段落",
        )
        validate_body_line_content_quality(title, raw_line)

    require(saw_bullet_item, f"{title} 的正文必须使用 bullet-style reader items，不允许散文段落")


def validate_body_line_content_quality(title: str, raw_line: str) -> None:
    normalized_line = normalize_body_line_for_quality(raw_line)
    if not normalized_line:
        return

    require(
        PLACEHOLDER_COUNT_COPY_RE.search(normalized_line) is None,
        f"{title} 的正文条目不得使用占位统计文案",
    )
    require(
        GENERIC_SOURCE_FALLBACK_RE.search(normalized_line) is None,
        f"{title} 的正文条目不得使用“围绕 X 展开，具体变化见来源”式兜底句",
    )
    require(
        GENERIC_GITHUB_FALLBACK_RE.search(normalized_line) is None,
        f"{title} 的正文条目不得使用 GitHub/README 泛化兜底句",
    )
    require(
        GENERIC_HN_FILLER_RE.search(normalized_line) is None,
        f"{title} 的正文条目不得使用 HN 泛化 filler",
    )
    require(
        EMPTY_COMMUNITY_JUDGMENT_RE.search(normalized_line) is None,
        f"{title} 的正文条目不得使用空泛判断句，必须复述原帖事实链",
    )
    require(
        not is_product_hunt_raw_english_tagline_leakage(normalized_line),
        f"{title} 的正文条目不得使用 Product Hunt 英文 tagline 泄漏",
    )
    require(
        not is_english_heavy_explanatory_leakage(normalized_line),
        f"{title} 的正文条目存在英文解释泄漏，必须用中文交代核心信息",
    )


def normalize_body_line_for_quality(raw_line: str) -> str:
    line = raw_line
    if BULLET_ITEM_RE.match(line):
        line = re.sub(r"^[-*+]\s+", "", line)
    else:
        line = line.lstrip()

    line = re.sub(r"[*_~]+", " ", line)
    line = INLINE_CODE_RE.sub(" ", line)
    line = MARKDOWN_LINK_INLINE_RE.sub(" ", line)
    line = PLAIN_URL_RE.sub(" ", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_english_heavy_explanatory_leakage(line: str) -> bool:
    if LONG_ENGLISH_PHRASE_RE.search(line) is None:
        return False

    chinese_char_count = len(CHINESE_CHAR_RE.findall(line))
    english_word_count = len(ENGLISH_WORD_RE.findall(line))
    if english_word_count >= 8 and chinese_char_count < 8:
        return True

    prefix_match = HYBRID_ENGLISH_TAIL_PREFIX_RE.search(line)
    if prefix_match is None:
        return False

    english_tail = normalize_body_line_for_quality(line[prefix_match.end() :])
    if not english_tail:
        return False

    english_tail_word_count = len(ENGLISH_WORD_RE.findall(english_tail))
    english_tail_chinese_count = len(CHINESE_CHAR_RE.findall(english_tail))
    return english_tail_word_count >= 10 and english_tail_word_count > english_tail_chinese_count * 2


def is_product_hunt_raw_english_tagline_leakage(line: str) -> bool:
    if "Product Hunt" not in line:
        return False

    match = re.search(r"(?:定位很直接|主打的是)[:：]\s*(.+?)(?:[。！!？?]|$)", line)
    if not match:
        return False

    tail = normalize_body_line_for_quality(match.group(1))
    if not tail:
        return False

    english_word_count = len(ENGLISH_WORD_RE.findall(tail))
    chinese_char_count = len(CHINESE_CHAR_RE.findall(tail))
    return english_word_count >= 4 and chinese_char_count < 4


def extract_body_sources(sections: list[tuple[str, list[str]]]) -> dict[str, list[str]]:
    body_sources: dict[str, list[str]] = {}
    for section_title, section_lines in sections:
        if section_is_explicit_no_info(section_lines):
            continue
        urls = unique_preserving_order(MARKDOWN_LINK_RE.findall("\n".join(section_lines)))
        require(urls, f"{section_title} 的正文条目必须带段落尾外链引用")
        body_sources[section_title] = validate_url_list(urls, label=f"{section_title} 正文引用")
    return body_sources


def section_is_explicit_no_info(section_lines: list[str]) -> bool:
    content_lines = [line.strip() for line in section_lines if line.strip()]
    return content_lines == ["- 无"]


def parse_appendix_sources(lines: list[str]) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {}
    current_title: str | None = None
    current_urls: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            if current_title is not None:
                sources[current_title] = validate_url_list(current_urls, label=f"{current_title} 来源附录")
            current_title = validate_reader_section_title(line[4:].strip(), field_name="appendix_section")
            current_urls = []
            continue
        require(current_title is not None, "## 来源 后必须直接进入 ### 栏目名 分组")
        if line.startswith("## "):
            raise ValueError("## 来源 后不允许再出现正文二级栏目")
        urls = PLAIN_URL_RE.findall(line)
        require(urls, f"{current_title} 来源附录条目必须包含原始外链 URL")
        current_urls.extend(urls)

    require(current_title is not None, "## 来源 下必须至少包含一个栏目分组")
    sources[current_title] = validate_url_list(current_urls, label=f"{current_title} 来源附录")
    return sources


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def iter_fixture_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.glob("*.json") if path.is_file())


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: uv run python helpers/validate_report_output_contract.py <fixture-dir-or-json>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    try:
        fixture_files = iter_fixture_files(root)
        require(fixture_files, "没有找到 report-output-contract fixture")
        for fixture_file in fixture_files:
            validate_fixture_case(fixture_file, load_json(fixture_file))
            print(f"[validate_report_output_contract] 通过: {fixture_file.name}")
    except Exception as error:  # noqa: BLE001
        print(f"[validate_report_output_contract] 失败: {error}", file=sys.stderr)
        return 1

    print(f"[validate_report_output_contract] 共验证 {len(fixture_files)} 个 fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
