"""
pages/news_page.py — World Cup news via NewsAPI with relevance filtering.
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta
from utils.ui import inject_css, page_header, require_login, svg_icon

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")

# (display label) -> (API query string, required keywords for client-side filtering)
CATEGORIES = {
    "All World Cup":  ('"World Cup 2026" football',          ["world cup", "2026", "fifa"]),
    "Portugal":       ('Portugal "World Cup" football',      ["portugal"]),
    "Argentina":      ('Argentina "World Cup" football',     ["argentina"]),
    "Brazil":         ('Brazil "World Cup" football',        ["brazil", "brasil"]),
    "France":         ('France "World Cup" football',        ["france"]),
    "England":        ('England "World Cup" football',       ["england"]),
    "Spain":          ('Spain "World Cup" football',         ["spain"]),
    "Germany":        ('Germany "World Cup" football',       ["germany"]),
    "Morocco":        ('Morocco "World Cup" football',       ["morocco"]),
    "USA":            ('USA "World Cup" 2026 football',      ["usa", "united states", "usmnt"]),
    "Mexico":         ('Mexico "World Cup" football',        ["mexico"]),
}

FOOTBALL_KEYWORDS = [
    "football", "soccer", "fifa", "world cup", "mundial", "goal", "match",
    "squad", "player", "coach", "manager", "tournament", "qualifier",
    "national team", "selecção", "seleção", "futebol",
]

STATIC_ARTICLES = [
    {"title": "FIFA World Cup 2026: Everything You Need to Know",
     "description": "The 2026 World Cup will be hosted across USA, Canada and Mexico — the first edition with 48 teams and 104 matches.",
     "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canada-mexico-usa2026",
     "source": "FIFA Official", "publishedAt": "2026-01-01T00:00:00Z", "urlToImage": None},
    {"title": "World Cup 2026 Groups & Format Explained",
     "description": "For the first time, 48 nations compete in 12 groups of 4, with the top 2 plus 8 best third-placed teams advancing.",
     "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canada-mexico-usa2026/articles",
     "source": "FIFA Official", "publishedAt": "2026-02-01T00:00:00Z", "urlToImage": None},
    {"title": "Host Cities for FIFA World Cup 2026",
     "description": "16 cities across USA, Canada and Mexico will host matches — including New York, Los Angeles, Dallas and Mexico City.",
     "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canada-mexico-usa2026/destination",
     "source": "FIFA Official", "publishedAt": "2026-02-15T00:00:00Z", "urlToImage": None},
    {"title": "Qualification: Which Teams Have Made It to USA/Canada/Mexico?",
     "description": "Teams from Europe, South America, Africa, Asia and CONCACAF battle for the 48 spots at the expanded World Cup.",
     "url": "https://www.bbc.com/sport/football/world-cup",
     "source": "BBC Sport", "publishedAt": "2026-03-01T00:00:00Z", "urlToImage": None},
    {"title": "Top Favourites & Dark Horses for World Cup 2026",
     "description": "Argentina defend their title while Brazil, France, England and Spain are all expected to challenge for glory.",
     "url": "https://www.goal.com/en/world-cup",
     "source": "Goal.com", "publishedAt": "2026-03-10T00:00:00Z", "urlToImage": None},
    {"title": "World Cup 2026 Schedule: Full Fixture List",
     "description": "Group stage begins June 11. Round of 32 starts June 29. The final is July 19 at MetLife Stadium, New Jersey.",
     "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canada-mexico-usa2026/match-schedule",
     "source": "FIFA Official", "publishedAt": "2026-03-15T00:00:00Z", "urlToImage": None},
]


@st.cache_data(ttl=600)
def _fetch_news(query: str) -> list[dict]:
    if not NEWSAPI_KEY:
        return []
    try:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 30,
            "from": from_date,
            "apiKey": NEWSAPI_KEY,
        }
        r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=8)
        return r.json().get("articles", [])
    except Exception:
        return []


def _is_relevant(article: dict, required_keywords: list) -> bool:
    text = " ".join([
        (article.get("title") or ""),
        (article.get("description") or ""),
        (article.get("content") or ""),
    ]).lower()
    if not any(kw in text for kw in required_keywords):
        return False
    if not any(kw in text for kw in FOOTBALL_KEYWORDS):
        return False
    title = (article.get("title") or "").strip()
    if not title or title == "[Removed]":
        return False
    return True


def _article_card(article: dict):
    title       = article.get("title", "No title") or "No title"
    description = article.get("description", "") or ""
    url         = article.get("url", "#") or "#"
    source      = article.get("source") or {}
    source_name = source.get("name", "") if isinstance(source, dict) else str(source)
    published   = article.get("publishedAt", "") or ""
    image       = article.get("urlToImage", None)

    try:
        dt = datetime.fromisoformat(published.replace("Z", ""))
        date_str = dt.strftime("%d %b %Y")
    except Exception:
        date_str = published[:10] if published else ""

    if len(description) > 160:
        description = description[:157] + "…"

    img_html = ""
    if image:
        img_html = (f'<img src="{image}" style="width:100%;height:140px;object-fit:cover;'
                    f'border-radius:8px 8px 0 0;" onerror="this.style.display=\'none\'" />')

    st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration:none;">
        <div style="background:var(--surface2);border:1px solid var(--border);
            border-radius:var(--radius);overflow:hidden;margin-bottom:12px;
            transition:border-color 0.2s,transform 0.2s;box-shadow:var(--shadow-sm);"
            onmouseover="this.style.borderColor='#B71C1C';this.style.transform='translateY(-2px)'"
            onmouseout="this.style.borderColor='var(--border)';this.style.transform='translateY(0)'">
            {img_html}
            <div style="padding:14px 16px;">
                <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:6px;
                    display:flex;justify-content:space-between;">
                    <span style="color:var(--primary);font-weight:600;">{source_name}</span>
                    <span>{date_str}</span>
                </div>
                <div style="font-size:0.9rem;font-weight:600;color:var(--text);
                    line-height:1.4;margin-bottom:8px;">{title}</div>
                <div style="font-size:0.78rem;color:var(--text-muted);line-height:1.5;">{description}</div>
                <div style="margin-top:10px;font-size:0.72rem;color:var(--primary);
                    font-weight:600;display:flex;align-items:center;gap:4px;">
                    {svg_icon("link", 12, "#B71C1C")} Read more
                </div>
            </div>
        </div>
        </a>""", unsafe_allow_html=True)


def render():
    inject_css()
    require_login()
    page_header("NEWS", "Latest World Cup & national team updates")

    if not NEWSAPI_KEY:
        st.info(
            f"{svg_icon('globe', 14, '#1565C0')} &nbsp;"
            "**Live news** requires a free NewsAPI key — add `NEWSAPI_KEY=your_key` to `.env`. "
            "Get one free at [newsapi.org](https://newsapi.org). Showing curated links for now.",
        )

    # If teams page sent us a team name via session state, pre-fill search
    _preset = st.session_state.pop("news_query", None)

    col_search, col_cat, col_refresh = st.columns([2, 2, 1])
    with col_search:
        team_search = st.text_input(
            "Search team",
            value=_preset or "",
            placeholder="e.g. Brazil, Morocco…",
            label_visibility="collapsed",
        )
    with col_cat:
        category = st.selectbox(
            "Topic",
            options=list(CATEGORIES.keys()),
            label_visibility="collapsed",
            disabled=bool(team_search),
        )
    with col_refresh:
        if st.button("↺ Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if team_search:
        query        = f"{team_search} soccer football"
        required_kws = []
    else:
        query, required_kws = CATEGORIES[category]

    with st.spinner("A carregar notícias…"):
        raw_articles = _fetch_news(query)

    if not raw_articles:
        articles = STATIC_ARTICLES
        st.markdown(
            f'<p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:16px;">'
            f'{svg_icon("clock", 13, "#B8960C")} Links curados — adiciona NEWSAPI_KEY para notícias ao vivo</p>',
            unsafe_allow_html=True)
    else:
        articles = [a for a in raw_articles if _is_relevant(a, required_kws)][:12]
        if articles:
            st.markdown(
                f'<p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:16px;">'
                f'{svg_icon("check", 13, "#2E7D32")} {len(articles)} artigos · '
                f'Tópico: <strong style="color:var(--text);">{category}</strong></p>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:16px;">'
                f'{svg_icon("x", 13, "#B8960C")} Sem notícias de futebol sobre '
                f'<strong style="color:var(--text);">{category}</strong> nos últimos 7 dias.</p>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, article in enumerate(articles):
        with cols[idx % 3]:
            _article_card(article)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:var(--text-dim);font-size:0.75rem;">'
        'Artigos abrem em nova aba · NewsAPI · Filtradas por relevância</div>',
        unsafe_allow_html=True)
