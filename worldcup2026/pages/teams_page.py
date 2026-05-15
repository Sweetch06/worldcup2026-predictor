"""
pages/teams_page.py
--------------------
Teams browser with WC history (appearances, titles, 2022 result),
flag images, form dots, and a quick News shortcut per team.
"""
import streamlit as st
from database import get_db
from models import Team, Match, MatchStage
from api.football_api import get_team_recent_matches, _fallback_teams
from utils.ui import inject_css, page_header, require_login, flag_emoji
from utils.standings import get_full_group_table
from utils.svg_icons import icon as _icon

# ── Country code map ───────────────────────────────────────────────────
COUNTRY_CODE: dict[str, str] = {
    "Argentina":"ar","Australia":"au","Austria":"at","Belgium":"be","Bolivia":"bo",
    "Bosnia-Herzegovina":"ba","Brazil":"br","Burkina Faso":"bf","Cameroon":"cm",
    "Canada":"ca","Cape Verde Islands":"cv","Chile":"cl","China PR":"cn",
    "Colombia":"co","Congo DR":"cd","Costa Rica":"cr","Croatia":"hr","Cuba":"cu",
    "Czech Republic":"cz","Czechia":"cz","Denmark":"dk","Ecuador":"ec","Egypt":"eg",
    "El Salvador":"sv","England":"gb-eng","France":"fr","Germany":"de","Ghana":"gh",
    "Haiti":"ht","Honduras":"hn","Hungary":"hu","Iran":"ir","Iraq":"iq",
    "Israel":"il","Italy":"it","Ivory Coast":"ci","Jamaica":"jm","Japan":"jp",
    "Jordan":"jo","Mexico":"mx","Morocco":"ma","Netherlands":"nl","New Zealand":"nz",
    "Nigeria":"ng","Norway":"no","Oman":"om","Panama":"pa","Paraguay":"py","Peru":"pe",
    "Poland":"pl","Portugal":"pt","Qatar":"qa","Saudi Arabia":"sa","Scotland":"gb-sct",
    "Senegal":"sn","Serbia":"rs","South Africa":"za","South Korea":"kr","Spain":"es",
    "Sweden":"se","Switzerland":"ch","Tunisia":"tn","Turkey":"tr","Ukraine":"ua",
    "United Arab Emirates":"ae","United States":"us","Uruguay":"uy","USA":"us",
    "Uzbekistan":"uz","Venezuela":"ve","Wales":"gb-wls","Curaçao":"cw",
    "Algeria":"dz","Indonesia":"id","Benin":"bj","TBD": "",
}

# ── Static WC history data ─────────────────────────────────────────────
# (appearances, titles, 2022_result)   None = did not qualify for 2022
TEAM_WC_HISTORY: dict[str, tuple[int, int, str | None]] = {
    "Argentina":       (18, 3, "🏆 Champions"),
    "France":          (16, 2, "🥈 Runners-up"),
    "Croatia":         ( 7, 0, "🥉 3rd Place"),
    "Morocco":         ( 6, 0, "4th Place"),
    "Netherlands":     (11, 1, "Quarter-Finals"),
    "Brazil":          (22, 5, "Quarter-Finals"),
    "Portugal":        ( 8, 0, "Quarter-Finals"),
    "England":         (16, 1, "Quarter-Finals"),
    "Spain":           (16, 1, "Round of 16"),
    "USA":             (11, 0, "Round of 16"),
    "United States":   (11, 0, "Round of 16"),
    "Australia":       ( 6, 0, "Round of 16"),
    "Japan":           ( 7, 0, "Round of 16"),
    "South Korea":     (11, 0, "Round of 16"),
    "Switzerland":     (12, 0, "Round of 16"),
    "Senegal":         ( 3, 0, "Round of 16"),
    "Poland":          (10, 0, "Group Stage"),
    "Denmark":         ( 6, 0, "Group Stage"),
    "Mexico":          (17, 0, "Group Stage"),
    "Germany":         (20, 4, "Group Stage"),
    "Belgium":         (14, 0, "Group Stage"),
    "Uruguay":         (14, 2, "Group Stage"),
    "Cameroon":        ( 8, 0, "Group Stage"),
    "Canada":          ( 2, 0, "Group Stage"),
    "Ecuador":         ( 4, 0, "Group Stage"),
    "Ghana":           ( 4, 0, "Group Stage"),
    "Iran":            ( 6, 0, "Group Stage"),
    "Qatar":           ( 1, 0, "Group Stage"),
    "Saudi Arabia":    ( 6, 0, "Group Stage"),
    "Serbia":          ( 3, 0, "Group Stage"),
    "Tunisia":         ( 6, 0, "Group Stage"),
    "Wales":           ( 2, 0, "Group Stage"),
    "Costa Rica":      ( 5, 0, None),
    "Colombia":        ( 6, 0, None),
    "Chile":           ( 9, 0, None),
    "Italy":           (14, 4, None),
    "Portugal":        ( 8, 0, "Quarter-Finals"),
    "Nigeria":         ( 7, 0, None),
    "Algeria":         ( 4, 0, None),
    "Egypt":           ( 3, 0, None),
    "Peru":            ( 5, 0, None),
    "Paraguay":        ( 9, 0, None),
    "Venezuela":       ( 0, 0, None),
    "Bolivia":         ( 3, 0, None),
    "Austria":         ( 7, 0, None),
    "Norway":          ( 4, 0, None),
    "Scotland":        ( 8, 0, None),
    "Turkey":          ( 2, 0, None),
    "Ukraine":         ( 1, 0, None),
    "Hungary":         ( 9, 0, None),
    "Indonesia":       ( 1, 0, None),
    "Panama":          ( 1, 0, None),
    "Jamaica":         ( 2, 0, None),
    "Honduras":        ( 3, 0, None),
    "El Salvador":     ( 2, 0, None),
    "Iraq":            ( 1, 0, None),
    "Jordan":          ( 0, 0, None),
    "United Arab Emirates": (0, 0, None),
    "Oman":            ( 0, 0, None),
    "China PR":        ( 1, 0, None),
    "New Zealand":     ( 2, 0, None),
    "South Africa":    ( 3, 0, None),
    "Ivory Coast":     ( 3, 0, None),
    "Congo DR":        ( 1, 0, None),
    "Uzbekistan":      ( 0, 0, None),
    "Burkina Faso":    ( 0, 0, None),
    "Mali":            ( 0, 0, None),
    "Cape Verde Islands": (0, 0, None),
    "Curaçao":         ( 0, 0, None),
    "Haiti":           ( 1, 0, None),
    "Benin":           ( 0, 0, None),
    "Cuba":            ( 0, 0, None),
}


# ── Helpers ────────────────────────────────────────────────────────────

def _flag_img(team_name: str, size: int = 24) -> str:
    code = COUNTRY_CODE.get((team_name or "").strip(), "")
    if code:
        w = int(size * 1.35)
        return (f'<img src="https://flagcdn.com/h40/{code}.png" '
                f'style="width:{w}px;height:{size}px;object-fit:cover;'
                f'border-radius:3px;vertical-align:middle;'
                f'box-shadow:0 1px 3px rgba(0,0,0,0.3);" />')
    return f'<span style="font-size:{size}px;">{flag_emoji(team_name)}</span>'


def _dot(result: str | None) -> str:
    m = {"win": "dot-win", "draw": "dot-draw", "loss": "dot-loss", "none": "dot-none", None: "dot-none"}
    return _icon(m.get(result, "dot-none"), 10)


def _wc_result_badge(result: str | None) -> str:
    if result is None:
        return '<span style="color:#9AA3B2;font-size:0.7rem;">Did not qualify (2022)</span>'
    colors = {
        "🏆": "#D4AF37",
        "🥈": "#C0C0C0",
        "🥉": "#CD7F32",
        "Quarter": "#4CAF50",
        "Round": "#64B5F6",
        "Group": "#9AA3B2",
        "4th": "#A5D6A7",
    }
    color = next((c for k, c in colors.items() if result.startswith(k[:5])), "#9AA3B2")
    return f'<span style="color:{color};font-size:0.7rem;font-weight:600;">2022: {result}</span>'


# ── Data loaders ───────────────────────────────────────────────────────

def _load_teams() -> list[dict]:
    with get_db() as db:
        teams = db.query(Team).order_by(Team.name).all()
        return [
            {
                "id":           t.id,
                "name":         t.name,
                "short_name":   t.short_name or "",
                "tla":          t.tla or "",
                "group_letter": t.group_letter or "",
                "crest_url":    t.crest_url or "",
            }
            for t in teams
        ]


def _load_group_table(group_letter: str) -> list[dict]:
    with get_db() as db:
        return get_full_group_table(db, group_letter)


def _load_recent_matches(team_id: int) -> list[dict]:
    with get_db() as db:
        return get_team_recent_matches(db, team_id, limit=5)


def _build_form_dots(recent: list[dict], team_id: int) -> str:
    dots = []
    for m in recent[-5:]:
        hs  = m.get("home_score")
        as_ = m.get("away_score")
        ht  = m.get("home_team", {})
        if hs is None or as_ is None:
            dots.append(_dot(None))
            continue
        t_is_home = ht.get("id") == team_id
        if hs == as_:
            dots.append(_dot("draw"))
        elif (t_is_home and hs > as_) or (not t_is_home and as_ > hs):
            dots.append(_dot("win"))
        else:
            dots.append(_dot("loss"))
    while len(dots) < 5:
        dots.append(_dot(None))
    return " ".join(dots)


# ── Main render ────────────────────────────────────────────────────────

def render():
    inject_css()
    require_login()
    page_header("TEAMS", "All FIFA World Cup 2026 nations")

    teams = _load_teams()
    if not teams:
        raw = _fallback_teams()
        st.info("Team data not yet synced. Showing static list — go to Admin → Sync to load data.")
        _render_static_teams(raw)
        return

    col_search, col_group = st.columns([3, 1])
    with col_search:
        search = st.text_input("Search team", placeholder="e.g. Brazil, Spain…",
                               label_visibility="collapsed")
    with col_group:
        groups = sorted({t["group_letter"] for t in teams if t["group_letter"]})
        group_filter = st.selectbox("Group", options=["All"] + groups,
                                    label_visibility="collapsed")

    filtered = teams
    if search:
        filtered = [t for t in filtered if search.lower() in t["name"].lower()]
    if group_filter != "All":
        filtered = [t for t in filtered if t["group_letter"] == group_filter]

    st.markdown(
        f"<p style='color:var(--text-muted);font-size:0.82rem;'>{len(filtered)} team(s)</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for idx, team in enumerate(filtered):
        with cols[idx % 3]:
            _render_team_card(team)


# ── Team card ──────────────────────────────────────────────────────────

def _render_team_card(team: dict):
    flag_html  = _flag_img(team["name"], 32)
    group_txt  = f"Group {team['group_letter']}" if team["group_letter"] else "Group TBD"
    recent     = _load_recent_matches(team["id"])
    form_dots  = _build_form_dots(recent, team["id"])

    hist       = TEAM_WC_HISTORY.get(team["name"], (0, 0, None))
    appearances, titles, wc2022 = hist
    appearances_txt = f"{appearances} WC" if appearances else "No WC"
    titles_txt      = f"🏆 {titles}×" if titles else "0 titles"
    result_badge    = _wc_result_badge(wc2022)

    with st.expander(f"{team['name']}  ·  {group_txt}"):
        st.markdown(
            f"""
            <div style="background:var(--surface2);border:1px solid var(--border);
                border-radius:10px;padding:14px;text-align:center;margin-bottom:12px;">
                <div style="display:flex;justify-content:center;margin-bottom:4px;">
                    {flag_html}
                </div>
                <div style="font-weight:700;font-size:1rem;margin:4px 0 2px 0;">
                    {team['name']}
                </div>
                <div style="color:var(--text-muted);font-size:0.78rem;margin-bottom:8px;">
                    {group_txt}
                </div>
                <div style="display:flex;justify-content:center;gap:16px;
                    font-size:0.72rem;color:var(--text-dim);margin-bottom:6px;">
                    <span title="World Cup appearances">{appearances_txt}</span>
                    <span title="World Cup titles">{titles_txt}</span>
                </div>
                <div style="margin-bottom:6px;">{result_badge}</div>
                <div style="margin-top:8px;">{form_dots}</div>
                <div style="color:var(--text-dim);font-size:0.68rem;margin-top:2px;">
                    Recent form (last 5)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # News shortcut button
        if st.button(f"📰 News: {team['name']}", key=f"news_btn_{team['id']}",
                     use_container_width=True):
            st.session_state.news_query = team["name"]
            st.session_state.nav = "News"
            st.rerun()

        if team["group_letter"]:
            table = _load_group_table(team["group_letter"])
            if table:
                st.markdown("**Group Standing**")
                for row in table:
                    is_this  = row["team_id"] == team["id"]
                    bg       = "var(--primary)" if is_this else "rgba(0,0,0,0.15)"
                    row_flag = _flag_img(row["team_name"], 16)
                    st.markdown(
                        f"""<div style="background:{bg};border-radius:6px;
                            padding:5px 10px;margin-bottom:3px;
                            display:flex;align-items:center;justify-content:space-between;
                            font-size:0.78rem;">
                            <span style="display:flex;align-items:center;gap:6px;">
                                <span>{row['position']}.</span>
                                {row_flag}
                                <span style="color:var(--text);">{row['team_name']}</span>
                            </span>
                            <span style="color:var(--secondary);font-weight:700;">
                                {row['pts']} pts
                            </span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        if recent:
            st.markdown("**Recent Matches**")
            for m in reversed(recent[-5:]):
                ht  = m.get("home_team", {})
                at  = m.get("away_team", {})
                hs  = m.get("home_score")
                as_ = m.get("away_score")
                if hs is not None and as_ is not None:
                    t_is_home = ht.get("id") == team["id"]
                    if hs == as_:
                        result = "draw"
                    elif (t_is_home and hs > as_) or (not t_is_home and as_ > hs):
                        result = "win"
                    else:
                        result = "loss"
                    score_str = f"{hs}–{as_}"
                else:
                    result    = "none"
                    score_str = "–"
                opp      = at if ht.get("id") == team["id"] else ht
                opp_name = opp.get("shortName", opp.get("name", "?"))
                opp_flag = _flag_img(opp.get("name", ""), 16)
                dot      = _dot(result)
                st.markdown(
                    f"""<div style="font-size:0.78rem;padding:3px 0;color:var(--text-muted);
                        display:flex;align-items:center;gap:6px;">
                        {dot} <span>vs</span> {opp_flag}
                        <span>{opp_name}</span>
                        <span style="color:var(--text);font-weight:600;margin-left:4px;">
                            {score_str}
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No recent match data available.")


# ── Static fallback ────────────────────────────────────────────────────

def _render_static_teams(raw: list[dict]):
    cols = st.columns(4)
    for idx, t in enumerate(raw):
        with cols[idx % 4]:
            flag_html = _flag_img(t["name"], 40)
            hist      = TEAM_WC_HISTORY.get(t["name"], (0, 0, None))
            apps, ttl, r22 = hist
            st.markdown(
                f"""<div style="background:var(--surface2);border:1px solid var(--border);
                    border-radius:10px;padding:12px;text-align:center;margin-bottom:8px;">
                    <div style="margin-bottom:6px;">{flag_html}</div>
                    <div style="font-size:0.85rem;font-weight:600;color:var(--text);">
                        {t['name']}
                    </div>
                    <div style="color:var(--text-muted);font-size:0.7rem;">{t['tla']}</div>
                    <div style="color:var(--text-dim);font-size:0.68rem;margin-top:4px;">
                        {apps} WC apps · {'🏆 ' + str(ttl) if ttl else 'No titles'}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
