"""Renders the "GitHub Activity" and "Most Used Languages" cards from a single source.

Third-party cards each count something different (all branches, public calendar
only, bytes of every org repo...), so their numbers contradict each other. This
script reads the user's contribution history year by year since the account was
created, through their own token (private and organization repos included), and
derives everything from it:

  - commits, contributions, repos contributed to and streaks from the
    contribution calendar,
  - languages by splitting each repo's commits across its languages by byte
    share, so repos you never committed to (and their vendored code) don't count.

Usage: GH_TOKEN=... GH_USER=zaosdev python3 profile_cards.py dist/
Stdlib only, so it runs on a bare GitHub Actions runner.
"""
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape

API = "https://api.github.com/graphql"

BG, BORDER = "#1a1b27", "#292e42"
FG, FG2, COMMENT, MUTED = "#c0caf5", "#a9b1d6", "#565f89", "#737aa2"
BLUE, CYAN, PURPLE, GREEN, ORANGE, YELLOW = "#7aa2f7", "#7dcfff", "#bb9af7", "#9ece6a", "#ff9e64", "#e0af68"
SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', 'Cascadia Code', Menlo, Consolas, monospace"
W, H, PAD = 400, 200, 24

USER_QUERY = "query($login: String!) { user(login: $login) { createdAt } }"

CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
      commitContributionsByRepository(maxRepositories: 100) {
        contributions { totalCount }
        repository {
          nameWithOwner
          languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
            totalSize
            edges { size node { name color } }
          }
        }
      }
    }
  }
}
"""


def graphql(token, query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.load(res)
    if body.get("errors"):
        raise RuntimeError(json.dumps(body["errors"], indent=2))
    return body["data"]


def fetch_history(token, login):
    created = datetime.fromisoformat(graphql(token, USER_QUERY, {"login": login})["user"]["createdAt"].replace("Z", "+00:00"))
    start = created.replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.now(timezone.utc)

    history = {"since": created.year, "commits": 0, "contributions": 0, "days": {}, "repo_commits": defaultdict(int), "repo_langs": {}}
    # contributionsCollection spans at most one year, so walk the account history in windows
    while start < now:
        end = min(start + timedelta(days=365) - timedelta(seconds=1), now)
        data = graphql(token, CONTRIB_QUERY, {"login": login, "from": start.isoformat(), "to": end.isoformat()})
        coll = data["user"]["contributionsCollection"]
        history["commits"] += coll["totalCommitContributions"]
        history["contributions"] += coll["contributionCalendar"]["totalContributions"]
        for week in coll["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                d = date.fromisoformat(day["date"])
                history["days"][d] = max(history["days"].get(d, 0), day["contributionCount"])
        for item in coll["commitContributionsByRepository"]:
            repo = item["repository"]
            history["repo_commits"][repo["nameWithOwner"]] += item["contributions"]["totalCount"]
            history["repo_langs"][repo["nameWithOwner"]] = repo["languages"]
        start += timedelta(days=365)
    return history


def streaks(days):
    longest = run = 0
    prev = None
    for d in sorted(days):
        if days[d] > 0:
            run = run + 1 if prev and d - prev == timedelta(days=1) and days[prev] > 0 else 1
            longest = max(longest, run)
        prev = d
    # the current streak survives a still-empty today
    current, d = 0, max(days) if days else None
    if d and days[d] == 0:
        d -= timedelta(days=1)
    while d in days and days[d] > 0:
        current += 1
        d -= timedelta(days=1)
    return current, longest


def language_entries(history, max_shown=8):
    scores, colors = defaultdict(float), {}
    for name, count in history["repo_commits"].items():
        langs = history["repo_langs"][name]
        if not langs["totalSize"]:
            continue
        for edge in langs["edges"]:
            lang = edge["node"]["name"]
            scores[lang] += count * edge["size"] / langs["totalSize"]
            colors[lang] = edge["node"]["color"] or COMMENT
    total = sum(scores.values())
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    if len(ranked) > max_shown:
        ranked = ranked[:max_shown - 1] + [("Other", sum(s for _, s in ranked[max_shown - 1:]))]
        colors["Other"] = "#414868"
    return [(name, 100 * score / total, colors[name]) for name, score in ranked]


def frame(title, note, desc, body, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(desc)}</desc>
  <style>
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; }}
    /* visible by default; the animation only plays the entrance, so static renderers still show everything */
    .fade {{ animation: fade .5s ease-out backwards; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
    {extra_css}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
  <text x="{PAD}" y="38" class="sans" font-size="18" font-weight="600" fill="{BLUE}">{escape(title)}</text>
  <text x="{W - PAD}" y="38" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">{escape(note)}</text>
  {body}
</svg>
"""


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def render_stats(history):
    current, longest = streaks(history["days"])
    tiles = [
        (fmt(history["commits"]), "", "Commits", BLUE),
        (fmt(history["contributions"]), "", "Contributions", CYAN),
        (str(len(history["repo_commits"])), "", "Repositories", PURPLE),
        (str(current), " days" if current != 1 else " day", "Current streak", GREEN),
        (str(longest), " days" if longest != 1 else " day", "Longest streak", ORANGE),
        (str(history["since"]), "", "Coding since", YELLOW),
    ]
    col_w = (W - 2 * PAD) / 3
    body = []
    for i, (value, unit, label, color) in enumerate(tiles):
        x, y = PAD + (i % 3) * col_w, 98 + (i // 3) * 64
        unit_svg = f'<tspan font-size="13" font-weight="400" fill="{MUTED}">{unit}</tspan>' if unit else ""
        body.append(
            f'<g class="fade" style="animation-delay:{0.1 + i * 0.08:.2f}s">'
            f'<text x="{x:.1f}" y="{y}" class="sans" font-size="26" font-weight="700" fill="{color}">{value}{unit_svg}</text>'
            f'<text x="{x:.1f}" y="{y + 20}" class="mono" font-size="10.5" letter-spacing=".6" fill="{MUTED}">{label.upper()}</text></g>'
        )
    desc = ", ".join(f"{label}: {value}{unit}" for value, unit, label, _ in tiles)
    return frame("GitHub Activity", f"since {history['since']} · incl. private", desc, "\n  ".join(body))


def render_languages(entries):
    bar_w, bar_y = W - 2 * PAD, 56
    segments, x = [], PAD
    for i, (_, pct, color) in enumerate(entries):
        w = bar_w * pct / 100 if i < len(entries) - 1 else PAD + bar_w - x  # last one absorbs rounding
        segments.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w + 0.5:.2f}" height="8" fill="{color}"/>')
        x += w

    legend = []
    for i, (name, pct, color) in enumerate(entries):
        lx, ly = PAD + (i % 2) * (bar_w / 2 + 12), 98 + (i // 2) * 26
        label = name if len(name) <= 18 else name[:17] + "…"
        legend.append(
            f'<g class="fade" style="animation-delay:{0.3 + i * 0.06:.2f}s">'
            f'<circle cx="{lx + 5:.1f}" cy="{ly - 4.5}" r="5" fill="{color}"/>'
            f'<text x="{lx + 17:.1f}" y="{ly}" class="sans" font-size="13.5" fill="{FG2}">{escape(label)} '
            f'<tspan class="mono" font-size="12" fill="{MUTED}">{pct:.1f}%</tspan></text></g>'
        )

    body = (
        f'<defs><clipPath id="bar"><rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="8" rx="4"/></clipPath></defs>'
        f'<rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="8" rx="4" fill="{BORDER}"/>'
        f'<g clip-path="url(#bar)"><g class="grow">{"".join(segments)}</g></g>\n  ' + "\n  ".join(legend)
    )
    css = (".grow { transform-box: fill-box; transform-origin: left; animation: grow .9s ease-out backwards; }"
           " @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }")
    desc = "Languages weighted by my commits: " + ", ".join(f"{n} {p:.1f}%" for n, p, _ in entries)
    return frame("Most Used Languages", "by my commits", desc, body, css)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    history = fetch_history(os.environ["GH_TOKEN"], os.environ["GH_USER"])
    print(f"{len(history['repo_commits'])} repos, {history['commits']} commits, {history['contributions']} contributions", file=sys.stderr)
    if not history["repo_commits"]:
        sys.exit("No commit contributions found; is GH_STATS_TOKEN set?")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(render_stats(history))
    with open(os.path.join(out_dir, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(render_languages(language_entries(history)))
