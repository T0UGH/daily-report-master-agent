from __future__ import annotations

from typing import Any

from helpers.github_trending_worker import (
    _extract_facts,
    _normalize_repo_from_url,
    _summary,
)
from helpers.lane_agent_contracts import validate_agent_lane_input, validate_agent_lane_output
from helpers.lane_contracts import validate_lane_output_artifact


LANE_NAME = "github-trending-weekly"
SECTION_TITLE = "GitHub 趋势项目"


def build_github_trending_agent_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_agent_lane_input(lane_input)
    if lane_input["lane"] != LANE_NAME:
        raise ValueError(f"{LANE_NAME} agent requires lane {LANE_NAME}")

    raw_candidates = [candidate for candidate in lane_input.get("raw_candidates", []) if isinstance(candidate, dict)]
    if lane_input.get("raw_corpus_status") == "blocked_raw_corpus_missing":
        return _blocked_output(lane_input, reason="blocked_raw_corpus_missing")
    if not raw_candidates:
        return _blocked_output(lane_input, reason="blocked_raw_corpus_missing")

    target_count = _target_count(lane_input)
    forbidden_phrases = _forbidden_phrases(lane_input)
    selected_items: list[dict[str, Any]] = []
    rejected_items: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    seen_repos: set[str] = set()

    for candidate in raw_candidates:
        title = _candidate_title(candidate)
        source_url = str(candidate.get("source_url") or "").strip()
        repo = _normalize_repo_from_url(source_url) or title
        source_text = str(candidate.get("source_snippet") or "").strip()
        if not source_url or not _normalize_repo_from_url(source_url):
            rejected_items.append(_rejected(candidate, title=title, reason="缺少有效 GitHub 仓库 URL"))
            continue
        if repo.lower() in seen_repos:
            rejected_items.append(_rejected(candidate, title=repo, reason="重复仓库，已由前一个 raw candidate 覆盖"))
            continue
        if not source_text:
            rejected_items.append(_rejected(candidate, title=repo, reason="缺少可读 source_snippet"))
            continue
        if not _is_agent_ecosystem_relevant(source_text, repo):
            rejected_items.append(_rejected(candidate, title=repo, reason="原始片段没有体现 coding-agent、Claude/Codex、MCP、agent runtime 或 agent workflow 相关性"))
            continue
        if len(selected_items) >= target_count:
            rejected_items.append(_rejected(candidate, title=repo, reason="超出本 lane item budget"))
            continue

        facts = _clean_facts_for_report(_extract_facts(source_text, repo))
        summary = _clean_text(_summary(repo, facts, source_text), forbidden_phrases)
        selected = {
            "id": str(candidate.get("id") or f"repo:{repo}"),
            "title": repo,
            "why_selected": summary,
            "sources": [source_url],
        }
        selected_items.append(selected)
        items.append(
            {
                "id": selected["id"],
                "title": repo,
                "url": source_url,
                "summary": summary,
                "why_today": summary,
                "source_urls": [source_url],
            }
        )
        sources.append({"label": repo, "url": source_url})
        seen_repos.add(repo.lower())

    markdown = _render_markdown(items)
    status = "ok" if items else "empty"
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": lane_input["report_date"],
        "lane": LANE_NAME,
        "agent_first": True,
        "status": status,
        "section_title": SECTION_TITLE,
        "markdown": markdown,
        "items": items,
        "sources": sources,
        "selected_items": selected_items,
        "rejected_items": rejected_items,
        "reasoning_notes": [
            f"selected {len(selected_items)} of {len(raw_candidates)} raw candidates",
            f"rejected {len(rejected_items)} raw candidates",
            "consumed raw_candidates only; compatibility selected_items were ignored",
        ],
        "agent_runtime": {
            "kind": "specialized_agent",
            "implementation": "github_trending_agent",
        },
        "quality": {
            "item_count": len(items),
            "rejected_count": len(rejected_items),
            "warnings": [] if items else ["no_ai_relevant_github_trending_items"],
        },
        "validation": {"status": "passed" if items else "empty", "errors": []},
    }
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output


def _target_count(lane_input: dict[str, Any]) -> int:
    value = lane_input.get("target_item_count")
    if isinstance(value, int) and value > 0:
        return min(value, 7)
    return 5


def _is_agent_ecosystem_relevant(source_text: str, repo: str) -> bool:
    haystack = f"{repo}\n{source_text}".lower()
    strong_needles = [
        "claude code",
        "codex",
        "openclaw",
        "mcp",
        "agent",
        "agents",
        "agentic",
        "multi-agent",
        "llm coding",
        "coding agent",
        "skill",
        "skills",
        "sre agents",
        "agent runtime",
        "tool calling",
        "handoffs",
        "tracing",
        "guardrails",
    ]
    return any(needle in haystack for needle in strong_needles)


def _forbidden_phrases(lane_input: dict[str, Any]) -> list[str]:
    phrases = (lane_input.get("style_contract") or {}).get("forbidden_phrases") or []
    return [str(phrase) for phrase in phrases if str(phrase).strip()]


def _candidate_title(candidate: dict[str, Any]) -> str:
    return str(candidate.get("title") or candidate.get("id") or "untitled").strip()


def _rejected(candidate: dict[str, Any], *, title: str, reason: str) -> dict[str, str]:
    return {
        "id": str(candidate.get("id") or title),
        "title": title,
        "reason": reason,
    }


def _clean_text(text: str, forbidden_phrases: list[str]) -> str:
    cleaned = text
    for phrase in forbidden_phrases:
        cleaned = cleaned.replace(phrase, "")
    return " ".join(cleaned.split()).strip(" ，,；;。") + "。"


def _clean_facts_for_report(facts: list[str]) -> list[str]:
    cleaned: list[str] = []
    for fact in facts:
        normalized = " ".join(str(fact).split()).strip()
        lower = normalized.lower()
        if not normalized:
            continue
        if any(fragment in lower for fragment in ["http", ".com/", "com/", "<h1", "</", "png", "svg", "img src", "actions/workflows"]):
            continue
        if normalized.count("(") != normalized.count(")"):
            continue
        cleaned.append(normalized.strip(" ，,；;。"))
    return cleaned or [fact for fact in facts if str(fact).strip()][:1]


def _render_markdown(items: list[dict[str, Any]]) -> str:
    lines = [f"## {SECTION_TITLE}", ""]
    if not items:
        lines.append("- 无")
        return "\n".join(lines)
    for item in items:
        url = item["source_urls"][0]
        lines.append(f"- **{item['title']}**：{item['summary']} [GitHub]({url})")
    return "\n".join(lines)


def _blocked_output(lane_input: dict[str, Any], *, reason: str) -> dict[str, Any]:
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": lane_input["report_date"],
        "lane": LANE_NAME,
        "agent_first": True,
        "status": "blocked",
        "section_title": SECTION_TITLE,
        "markdown": _render_markdown([]),
        "items": [],
        "sources": [],
        "selected_items": [],
        "rejected_items": [],
        "reasoning_notes": [f"blocked: {reason}"],
        "agent_runtime": {
            "kind": "specialized_agent",
            "implementation": "github_trending_agent",
        },
        "quality": {"item_count": 0, "rejected_count": 0, "reason": reason, "warnings": [reason]},
        "validation": {"status": "blocked", "errors": [reason]},
    }
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output
