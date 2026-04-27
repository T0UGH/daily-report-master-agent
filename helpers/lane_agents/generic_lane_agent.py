from __future__ import annotations

import re
from typing import Any

from helpers.lane_agent_contracts import validate_agent_lane_input, validate_agent_lane_output
from helpers.lane_contracts import validate_lane_output_artifact
from helpers.validate_report_output_contract import FIXED_SECTION_TITLES


KEYWORD_LABELS = {
    "claude code": "Claude Code 工作流",
    "codex": "Codex 工具链",
    "openclaw": "OpenClaw 运行细节",
    "mcp": "MCP 工具调用",
    "agent": "agent 工作流",
    "agents": "agent 工作流",
    "agentic": "agent 工作流",
    "openai": "OpenAI 生态",
    "anthropic": "Anthropic 生态",
    "llm": "大模型应用",
    "workflow": "工作流",
    "github": "开源项目",
    "product hunt": "新品发布",
    "polymarket": "市场预测",
    "weather": "天气背景",
    "hacker news": "Hacker News 讨论",
}
LANE_TOPIC_FALLBACKS = {
    "weather-watch": "天气和出行背景",
    "x-feed": "X 推荐流中的 agent 相关讨论",
    "x-following": "X 关注流中的 agent 相关讨论",
    "reddit-watch": "Reddit 社区讨论",
    "hacker-news-watch": "Hacker News 热门讨论",
    "hacker-news-search-watch": "Hacker News 搜索结果",
    "claude-code-watch": "Claude Code 变化",
    "codex-watch": "Codex 变化",
    "openclaw-watch": "OpenClaw 变化",
    "github-ai-projects": "GitHub AI 项目发现",
    "product-hunt-watch": "Product Hunt 新品",
    "polymarket-watch": "Polymarket 市场变化",
}


def build_generic_lane_agent_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_agent_lane_input(lane_input)
    lane_name = lane_input["lane"]
    raw_candidates = [candidate for candidate in lane_input.get("raw_candidates", []) if isinstance(candidate, dict)]
    raw_corpus_status = str(lane_input.get("raw_corpus_status") or "")
    if raw_corpus_status == "blocked_raw_corpus_missing":
        return _blocked_output(lane_input, reason=raw_corpus_status)
    if raw_corpus_status == "degraded/no_own_raw_corpus" and not raw_candidates:
        return _degraded_no_own_corpus_output(lane_input)
    if not raw_candidates:
        return _blocked_output(lane_input, reason="blocked_raw_corpus_missing")

    target_count = _target_count(lane_input)
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    seen_source_urls: set[str] = set()

    for candidate in raw_candidates:
        title = _candidate_title(candidate)
        source_url = str(candidate.get("source_url") or "").strip()
        snippet = str(candidate.get("source_snippet") or "").strip()
        if not source_url:
            rejected.append(_rejected(candidate, title=title, reason="缺少 source_url，无法给正文段落提供来源"))
            continue
        if not snippet:
            rejected.append(_rejected(candidate, title=title, reason="缺少可读 source_snippet"))
            continue
        if len(selected) >= target_count:
            rejected.append(_rejected(candidate, title=title, reason="超出本 lane item budget"))
            continue
        summary = _summary_for_candidate(lane_name=lane_name, title=title, snippet=snippet)
        selected_item = {
            "id": str(candidate.get("id") or title),
            "title": title,
            "why_selected": summary,
            "sources": [source_url],
        }
        selected.append(selected_item)
        items.append(
            {
                "id": selected_item["id"],
                "title": title,
                "url": source_url,
                "summary": summary,
                "why_today": summary,
                "source_urls": [source_url],
            }
        )
        if source_url not in seen_source_urls:
            sources.append({"label": title, "url": source_url})
            seen_source_urls.add(source_url)

    markdown = _render_markdown(
        section_title=_section_title(lane_input),
        items=items,
    )
    status = "ok" if items else "empty"
    output = _base_output(
        lane_input,
        status=status,
        markdown=markdown,
        items=items,
        sources=sources,
        selected_items=selected,
        rejected_items=rejected,
        reasoning_notes=[
            f"selected {len(selected)} of {len(raw_candidates)} raw candidates",
            "generic migration shim used raw_candidates only",
        ],
        quality={
            "item_count": len(items),
            "rejected_count": len(rejected),
            "warnings": [] if items else ["no_renderable_raw_candidates"],
        },
        validation_status="passed" if items else "empty",
    )
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output


def _target_count(lane_input: dict[str, Any]) -> int:
    value = lane_input.get("target_item_count")
    if isinstance(value, int) and value > 0:
        return value
    return 3


def _section_title(lane_input: dict[str, Any]) -> str:
    title = lane_input.get("lane_title")
    if isinstance(title, str) and title.strip():
        return title
    return FIXED_SECTION_TITLES.get(str(lane_input.get("lane")), str(lane_input.get("lane") or "Lane"))


def _candidate_title(candidate: dict[str, Any]) -> str:
    return str(candidate.get("title") or candidate.get("id") or "untitled").strip()


def _rejected(candidate: dict[str, Any], *, title: str, reason: str) -> dict[str, str]:
    return {
        "id": str(candidate.get("id") or title),
        "title": title,
        "reason": reason,
    }


def _summary_for_candidate(*, lane_name: str, title: str, snippet: str) -> str:
    del title
    chinese_fact = _first_chinese_fact(snippet)
    keywords = _keyword_labels(snippet)
    if not keywords:
        keywords = [LANE_TOPIC_FALLBACKS.get(lane_name, "本 lane 原始信号")]
    if chinese_fact:
        return f"{chinese_fact} 这条原始信号给出的可核验信息集中在{'、'.join(keywords[:3])}。"
    return f"这条原始信号给出的可核验信息集中在{'、'.join(keywords[:3])}，适合作为今日该栏目的迁移期素材。"


def _first_chinese_fact(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text) is None:
        return ""
    first = re.split(r"[。！？!?]\s*", text.strip(), maxsplit=1)[0].strip()
    first = re.sub(r"\s+", " ", first)
    if len(first) > 96:
        first = first[:95].rstrip() + "…"
    return first.rstrip("。！？!?") + "。"


def _keyword_labels(text: str) -> list[str]:
    lower = text.lower()
    labels: list[str] = []
    for needle, label in KEYWORD_LABELS.items():
        if needle in lower and label not in labels:
            labels.append(label)
    if re.search(r"智能体|代理|工具调用|大模型|工作流|编程", text):
        labels.append("中文 agent 生态信号")
    return labels


def _render_markdown(*, section_title: str, items: list[dict[str, Any]]) -> str:
    lines = [f"## {section_title}", ""]
    if not items:
        lines.append("- 无")
        return "\n".join(lines)
    for item in items:
        url = item["source_urls"][0]
        lines.append(f"- **{item['title']}**：{item['summary']} [来源]({url})")
    return "\n".join(lines)


def _base_output(
    lane_input: dict[str, Any],
    *,
    status: str,
    markdown: str,
    items: list[dict[str, Any]],
    sources: list[dict[str, str]],
    selected_items: list[dict[str, Any]],
    rejected_items: list[dict[str, Any]],
    reasoning_notes: list[str],
    quality: dict[str, Any],
    validation_status: str,
) -> dict[str, Any]:
    return {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": lane_input["report_date"],
        "lane": lane_input["lane"],
        "agent_first": True,
        "status": status,
        "section_title": _section_title(lane_input),
        "markdown": markdown,
        "items": items,
        "sources": sources,
        "selected_items": selected_items,
        "rejected_items": rejected_items,
        "reasoning_notes": reasoning_notes,
        "agent_runtime": {
            "kind": "migration_shim",
            "implementation": "generic_lane_agent",
            "maturity": "migration_shim",
        },
        "quality": quality,
        "validation": {"status": validation_status, "errors": []},
    }


def _blocked_output(lane_input: dict[str, Any], *, reason: str) -> dict[str, Any]:
    markdown = _render_markdown(section_title=_section_title(lane_input), items=[])
    output = _base_output(
        lane_input,
        status="blocked",
        markdown=markdown,
        items=[],
        sources=[],
        selected_items=[],
        rejected_items=[],
        reasoning_notes=[f"blocked: {reason}"],
        quality={"item_count": 0, "rejected_count": 0, "reason": reason, "warnings": [reason]},
        validation_status="blocked",
    )
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output


def _degraded_no_own_corpus_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    queries = (lane_input.get("cross_lane_context") or {}).get("github_search_queries") or []
    note = "github-ai-projects has discovery context but no dedicated raw corpus"
    output = _base_output(
        lane_input,
        status="degraded",
        markdown=_render_markdown(section_title=_section_title(lane_input), items=[]),
        items=[],
        sources=[],
        selected_items=[],
        rejected_items=[],
        reasoning_notes=[note, f"discovery query count: {len(queries)}"],
        quality={
            "item_count": 0,
            "rejected_count": 0,
            "reason": "degraded/no_own_raw_corpus",
            "github_search_query_count": len(queries),
            "warnings": ["no_own_raw_corpus"],
        },
        validation_status="degraded",
    )
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output
