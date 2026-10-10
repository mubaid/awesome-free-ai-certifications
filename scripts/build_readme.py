"""Generate README.md from data/course_catalog.csv. Stdlib only."""
import csv
import datetime
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "course_catalog.csv"
README = ROOT / "README.md"

# Ordered: first track with any keyword hit (lowercased substring) wins.
# Tuple: (track name, keywords, header emoji).
TRACKS: list[tuple[str, tuple[str, ...], str]] = [
    ("Responsible AI & Ethics", ("responsible", "ethic", "safety", "assurance", "alignment"), "🛡️"),
    ("Prompt Engineering", ("prompt",), "💬"),
    ("AI Agents & RAG", ("agent", "rag", "langchain", "langgraph", "n8n", "mcp", "autogen", "crewai"), "🤖"),
    ("Data & ML", ("data analytic", "python", "machine learning", "pandas", "kaggle", "mongo", "neo4j", "rulex", "sas ", "statistics"), "📊"),
    ("Cloud AI", ("cloud", "azure", "aws", "gcp", "nvidia", "cumulus", "databricks", "linux", "alibaba", "sap"), "☁️"),
    ("Dev & Tools", ("copilot", "website", "youtube", "gmail", "sheets", "slides", "meet", "workspace", "chatgpt", "gemini", "sora", "canva", "hubspot", "semrush", "trailhead", "salesforce", "make ", "hugging face", "mistral"), "🛠️"),
    ("GenAI Foundations", (), "🌱"),
]

# One-line "who it's for" per track. Display only; does not affect assignment.
TRACK_BLURBS: dict[str, str] = {
    "Responsible AI & Ethics": "Ethics, safety, and governance basics. Good on any CV, required reading before you ship AI.",
    "Prompt Engineering": "Practical prompting for ChatGPT, Copilot, Gemini, and more. Fastest win if you are not a developer.",
    "AI Agents & RAG": "The most job-relevant track right now. Agents, RAG, LangChain, LangGraph, MCP, and Agentforce.",
    "Data & ML": "Python, analytics, and machine learning foundations. Start here for data roles and ML interviews.",
    "Cloud AI": "AI on your cloud and infra stack: SAP, NVIDIA, Databricks, Google Cloud, and related cloud AI services.",
    "Dev & Tools": "Ship faster with AI tools: Copilot, ChatGPT, and Gemini for code, docs, marketing, and support.",
    "GenAI Foundations": "New to AI? Start here. Beginner-friendly generative AI and LLM foundations from major providers.",
}

# Hand-curated flagship picks: (catalog id, one-line why-it-matters).
TOP_PICKS: list[tuple[str, str]] = [
    ("165", "Official Claude primer. Best first certificate if you use Claude."),
    ("166", "Official intro to coding with Claude Code. Directly useful for developers."),
    ("175", "Official intro to MCP, the open standard for connecting AI to tools."),
    ("172", "Official intro to agent skills. Short, practical follow-up to Claude 101."),
    ("187", "Hands-on agent course with a Unit 1 certificate. Best free agents starting point."),
    ("188", "Hands-on MCP companion with a Unit 1 certificate. Pair it with the course above."),
    ("312", "Official foundations from OpenAI Academy. Good CV anchor."),
    ("323", "Classic hands-on ML intro with exercises. Good before interviews."),
    ("260", "Google's own LLM primer. Short, beginner-friendly theory base."),
    ("334", "Short responsible-AI intro. Easy second certificate."),
]


def slug(text: str) -> str:
    """Stable in-page anchor (GitHub renders matching ids for these)."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9 _-]", "", s)
    return re.sub(r"\s+", "-", s.strip())


def primary_track(title: str) -> str:
    low = title.lower()
    for name, keywords, _ in TRACKS:
        if any(k in low for k in keywords):
            return name
    return "GenAI Foundations"


def badge(provider: str) -> str:
    slug_p = urllib.parse.quote(provider.replace(" ", "_"), safe="_")
    return f"![{provider}](https://img.shields.io/badge/{slug_p}-blue)"


def esc(text: str) -> str:
    return text.replace("|", "\\|")


def load_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows and set(rows[0]) == {"id", "title", "provider", "url"}, "CSV header must be id,title,provider,url"
    return rows


def validate(rows: list[dict[str, str]]) -> None:
    ids = [r["id"] for r in rows]
    assert rows, "no courses in CSV"
    assert len(ids) == len(set(ids)), f"duplicate ids in CSV: {len(rows)} rows / {len(set(ids))} unique"
    for r in rows:
        assert r["url"].startswith("https://"), f"non-https URL for {r['id']}: {r['url']}"
    assert len({r["url"] for r in rows}) == len(rows), "duplicate URLs in CSV"


def build_readme() -> str:
    rows = load_rows()
    validate(rows)
    today = datetime.date.today().isoformat()
    providers: dict[str, list[dict[str, str]]] = {}
    tracks: dict[str, list[dict[str, str]]] = {name: [] for name, _, _ in TRACKS}
    for r in rows:
        providers.setdefault(r["provider"], []).append(r)
        tracks[primary_track(r["title"])].append(r)
    by_id = {r["id"]: r for r in rows}
    for pid, _ in TOP_PICKS:
        assert pid in by_id, f"top-pick id not in catalog: {pid}"

    repo_url = "https://github.com/mubaid/awesome-free-ai-certifications"
    share_text = urllib.parse.quote(
        f"{len(rows)} free AI courses with certificates - Awesome Free AI Certifications {repo_url}")
    x_share = f"https://x.com/intent/post?text={share_text}"

    L: list[str] = []
    L.append('<a id="top"></a>')
    L.append("# Awesome Free AI Certifications\n")
    L.append(f"[![courses](https://img.shields.io/badge/courses-{len(rows)}-brightgreen)]"
             f"(#by-provider-index) [![providers](https://img.shields.io/badge/providers-{len(providers)}-blue)]"
             "(#by-provider-index) [![price](https://img.shields.io/badge/price-free-success)]"
             "(#awesome-free-ai-certifications) "
             "[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)\n")
    L.append(f"**{len(rows)} free AI courses with certificates · {len(providers)} providers · updated {today}.**\n")
    L.append(
        "A maintained catalog of **free AI courses** that grant a **certificate or badge** on completion — "
        "covering generative AI, AI agents and RAG, prompt engineering, machine learning, and AI development tools. "
        f"Courses come from {len(providers)} providers including Anthropic, OpenAI Academy, Google Skills, "
        "Microsoft Learn, Hugging Face, Kaggle Learn, LangChain Academy, NVIDIA, Salesforce Trailhead, and SAP Learning.\n"
    )
    L.append(
        "> Inclusion rule: a course is listed because its provider page advertises no-cost access "
        "plus a completion certificate or badge at the time of curation. "
        "Terms can change, so check the course page before you start. "
        "See [What \"free with certificate\" means](#what-free-with-certificate-means).\n"
    )
    L.append(f"⭐ **Star this repo to bookmark it** — that also helps others discover it. "
             f"[Share on X]({x_share}) · [Add a course](CONTRIBUTING.md)\n")
    L.append("## Choose your path in 30 seconds\n")
    L.append("| If you want to… | Start here |")
    L.append("|---|---|")
    L.append("| Learn AI from zero | [GenAI Foundations](#genai-foundations) → pick any beginner title, or course #1 below |")
    L.append("| Earn certificates for your CV and LinkedIn | [Top 10 flagship picks](#top-10-flagship-picks) — every entry in this repo grants one |")
    L.append("| Build AI agents and RAG apps (most job-relevant) | [AI Agents & RAG](#ai-agents-rag) → Hugging Face or LangChain courses first |")
    L.append("| Get practical with ChatGPT, Copilot, and Gemini | [Prompt Engineering](#prompt-engineering) + [Dev & Tools](#dev-tools) |")
    L.append("| Strengthen ML and data fundamentals | [Data & ML](#data-ml) → Kaggle Learn titles first |")
    L.append("| Use AI responsibly or lead a team | [Responsible AI & Ethics](#responsible-ai-ethics) |")
    L.append("")
    L.append("How to use this list: pick a track, open the provider page, finish the course, "
             "then claim the certificate there. "
             "To browse by platform instead, use the [By Provider Index](#by-provider-index).\n")
    L.append("## Contents\n")
    L.append("- [🔥 Top 10 flagship picks](#top-10-flagship-picks)")
    L.append("- [📊 Provider stats](#provider-stats)")
    for name, _, emoji in TRACKS:
        n = len(tracks[name])
        L.append(f"- [{emoji} {name} ({n})](#{slug(name)})")
    L.append("- [By Provider Index](#by-provider-index)")
    L.append("- [What \"free with certificate\" means](#what-free-with-certificate-means)")
    L.append("- [Add it to LinkedIn in 2 minutes](#add-it-to-linkedin-in-2-minutes)")
    L.append("- [Contributing](#contributing)")
    L.append("- [Maintenance](#maintenance)\n")
    L.append('<a id="top-10-flagship-picks"></a>')
    L.append("## 🔥 Top 10 flagship picks\n")
    L.append("New here? Start with these. Highest-signal, official courses from the biggest names in AI.\n")
    L.append("| # | Course | Provider | Why start here | Link |")
    L.append("|---|---|---|---|---|")
    for i, (pid, blurb) in enumerate(TOP_PICKS, 1):
        r = by_id[pid]
        L.append(f"| {i} | {esc(r['title'])} | {badge(r['provider'])} | {blurb} | [Open]({r['url']}) |")
    L.append("\n[↑ Back to top](#top)\n")
    L.append('<a id="provider-stats"></a>')
    L.append("## 📊 Provider stats\n")
    L.append(f"{len(rows)} courses across {len(providers)} providers, sorted by course count. "
             "Browse any provider in the [By Provider Index](#by-provider-index).\n")
    L.append("| Provider | Courses |")
    L.append("|---|---:|")
    for prov in sorted(providers, key=lambda p: (-len(providers[p]), p.lower())):
        L.append(f"| {esc(prov)} | {len(providers[prov])} |")
    L.append("\n[↑ Back to top](#top)\n")
    for name, _, emoji in TRACKS:
        items = sorted(tracks[name], key=lambda r: r["title"].lower())
        L.append(f'<a id="{slug(name)}"></a>')
        L.append(f"## {emoji} {name} ({len(items)})\n")
        L.append(f"{TRACK_BLURBS.get(name, '')}\n")
        if len(items) > 25:
            L.append("<details><summary>Show all</summary>\n")
        L.append("| Course | Provider | Link |")
        L.append("|---|---|---|")
        for r in items:
            L.append(f"| {esc(r['title'])} | {badge(r['provider'])} | [Open]({r['url']}) |")
        if len(items) > 25:
            L.append("</details>")
        L.append("\n[↑ Back to top](#top)\n")
    L.append('<a id="by-provider-index"></a>')
    L.append("## By Provider Index\n")
    L.append("Prefer a platform? Every course also appears once here, grouped by provider.\n")
    for prov in sorted(providers):
        items = sorted(providers[prov], key=lambda r: r["title"].lower())
        L.append(f"<details><summary><strong>{esc(prov)} ({len(items)})</strong></summary>\n")
        L.append("| Course | Link |")
        L.append("|---|---|")
        for r in items:
            L.append(f"| {esc(r['title'])} | [Open]({r['url']}) |")
        L.append("</details>\n")
    L.append('<a id="what-free-with-certificate-means"></a>')
    L.append("## What \"free with certificate\" means\n")
    L.append("Transparency first, because \"free\" varies by provider:")
    L.append("- **Listed** means the provider page advertised free access and a completion certificate, badge, or Trailhead-style achievement when the entry was added.")
    L.append("- **Check before you start.** Most courses need a free account. A few may gate exams, ID verification, or certificates behind login, region, or policy changes.")
    L.append("- **Found a paywall or dead link?** Please [add a course or fix](CONTRIBUTING.md) via `data/course_catalog.csv` — or open an issue with the course URL. That is how this list stays trustworthy.\n")
    L.append('[↑ Back to top](#top)\n')
    L.append('<a id="add-it-to-linkedin-in-2-minutes"></a>')
    L.append("## Add it to LinkedIn in 2 minutes\n")
    L.append("Certificates only help if people see them:")
    L.append("1. Finish the course and download the certificate from the provider.")
    L.append("2. LinkedIn profile → **Add profile section → Licenses & Certifications → Add**, then paste the course name, provider, and credential URL.")
    L.append("3. Fork this repo to track what you finished, and share one course that helped you — see the copy-paste text below.\n")
    L.append('[↑ Back to top](#top)\n')
    L.append('<a id="contributing"></a>')
    L.append("## Contributing\n")
    L.append("This list improves when readers submit what they find. One row in `data/course_catalog.csv`, then regenerate:")
    L.append("1. Add `id,title,provider,url` to `data/course_catalog.csv` (free course that grants a certificate, `https://` URL, no affiliates or paywalls).")
    L.append("2. Run `python3 scripts/build_readme.py` and commit both files.")
    L.append("Full 60-second guide: [CONTRIBUTING.md](CONTRIBUTING.md).\n")
    L.append('[↑ Back to top](#top)\n')
    L.append('<a id="maintenance"></a>')
    L.append("## Maintenance\n")
    L.append(f"- Catalog: `{len(rows)}` courses · `{len(providers)}` providers · updated `{today}`.")
    L.append("- Source of truth is [`data/course_catalog.csv`](data/course_catalog.csv). This README is generated by [`scripts/build_readme.py`](scripts/build_readme.py) — do not hand-edit tables.")
    L.append("- The build asserts unique ids, unique `https://` URLs, and reconciles track + provider counts on every run.")
    L.append("- Spotted an error? Open an issue with the course title and URL, or send a PR per [CONTRIBUTING.md](CONTRIBUTING.md).\n")
    L.append('[↑ Back to top](#top)\n')
    L.append("## Share\n")
    L.append("Copy-paste to recommend this list:")
    L.append("```")
    L.append(f"{len(rows)} free AI courses with certificates (GenAI, agents/RAG, prompting, ML) — organized by goal and provider:")
    L.append("```")
    L.append(f"[Share on X]({x_share})\n")
    L.append("---\n")
    L.append(f"⭐ **Found this useful? Star the repo** — it keeps this list maintained and discoverable. "
             f"[Share on X]({x_share}) · [Add a course](CONTRIBUTING.md)\n")
    L.append("<!-- Generated by scripts/build_readme.py — do not hand-edit tables. Edit data/course_catalog.csv and rerun. -->\n")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    fresh = build_readme()
    if "--check" in sys.argv[1:]:
        current = README.read_text(encoding="utf-8")
        if current != fresh:
            print("README.md is stale: run python3 scripts/build_readme.py and commit the result")
            raise SystemExit(1)
        print("README.md is in sync with data/course_catalog.csv")
    else:
        README.write_text(fresh, encoding="utf-8")
        print(f"wrote {README} ({len(fresh.splitlines())} lines)")
