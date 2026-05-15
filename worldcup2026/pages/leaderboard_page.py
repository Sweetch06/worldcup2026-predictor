"""
pages/leaderboard_page.py
-------------------------
Leaderboard with podium, expandable per-player breakdown rows,
and a points-by-category breakdown chart.
"""
import streamlit as st
import pandas as pd
from database import get_db
from scoring import get_leaderboard
from utils.ui import inject_css, page_header, require_login, require_room, get_avatar_svg


def render():
    inject_css()
    require_login()
    require_room()

    user = st.session_state.user
    room = st.session_state.room

    page_header("LEADERBOARD", f"Room: {room['name']}")

    with get_db() as db:
        lb = get_leaderboard(db, room["id"])

    if not lb:
        st.info("No players or scored predictions in this room yet.")
        return

    # ── Podium ────────────────────────────────────────────────────────
    if len(lb) >= 2:
        _render_podium(lb[:min(3, len(lb))])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Rankings ──────────────────────────────────────────────────────
    st.subheader("Full Rankings")

    leader_pts = lb[0]["total_points"] if lb else 1

    for entry in lb:
        rank_labels = {1: "1st", 2: "2nd", 3: "3rd"}
        rank_label  = rank_labels.get(entry["rank"], f"#{entry['rank']}")
        is_me       = entry["user_id"] == user["id"]
        bg          = "#2A2A2A" if is_me else "#1E1E1E"
        border      = "1px solid #C8102E" if is_me else "1px solid #3A3A3A"
        pct         = (entry["total_points"] / leader_pts * 100) if leader_pts > 0 else 0

        # Expandable row — header rendered as HTML, body via st.expander
        with st.expander(
            f"{rank_label}  ·  {entry['username']}  ·  {entry['total_points']:.0f} pts",
            expanded=is_me,
        ):
            c_ava, c_info, c_pts = st.columns([1, 5, 2])

            with c_ava:
                st.markdown(
                    f"<div style='display:flex;align-items:center;justify-content:center;"
                    f"height:100%;padding-top:4px;'>"
                    f"{get_avatar_svg(entry['avatar_emoji'], 40)}</div>",
                    unsafe_allow_html=True,
                )

            with c_info:
                you_badge = (
                    ' <span style="color:#C8102E;font-size:0.72rem;">(you)</span>'
                    if is_me else ""
                )
                st.markdown(
                    f"<div style='font-weight:700;font-size:1rem;'>"
                    f"{entry['username']}{you_badge}</div>",
                    unsafe_allow_html=True,
                )
                # Progress bar relative to leader
                st.markdown(
                    f"<div style='background:#141414;border-radius:4px;height:5px;"
                    f"overflow:hidden;margin:8px 0 4px 0;'>"
                    f"<div style='background:linear-gradient(90deg,#C8102E,#D4AF37);"
                    f"width:{pct:.1f}%;height:100%;border-radius:4px;'></div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='color:#9A9A9A;font-size:0.72rem;'>"
                    f"{pct:.0f}% of leader</div>",
                    unsafe_allow_html=True,
                )

            with c_pts:
                st.markdown(
                    f"<div style='text-align:right;'>"
                    f"<div style='font-size:2rem;font-weight:800;color:#D4AF37;"
                    f"font-family:\"Bebas Neue\",sans-serif;line-height:1;'>"
                    f"{entry['total_points']:.0f}</div>"
                    f"<div style='color:#9A9A9A;font-size:0.68rem;'>points</div></div>",
                    unsafe_allow_html=True,
                )

            # ── Per-phase breakdown ───────────────────────────────────
            st.markdown("<hr style='border-color:#3A3A3A;margin:12px 0;'>",
                        unsafe_allow_html=True)

            phases = [
                ("⚽ Match Results",     entry.get("match_points",  0)),
                ("📊 Group Standings",   entry.get("group_points",  0)),
                ("🏆 Tournament Winner", entry.get("winner_points", 0)),
            ]

            p_cols = st.columns(3)
            for p_col, (phase_label, phase_pts) in zip(p_cols, phases):
                with p_col:
                    st.markdown(
                        f"<div style='background:#141414;border:1px solid #3A3A3A;"
                        f"border-radius:8px;padding:10px;text-align:center;'>"
                        f"<div style='font-size:0.72rem;color:#9A9A9A;'>{phase_label}</div>"
                        f"<div style='font-size:1.4rem;font-weight:800;color:#D4AF37;"
                        f"font-family:\"Bebas Neue\",sans-serif;'>{phase_pts:.0f}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    # ── Points breakdown chart ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Points by Category")

    df = pd.DataFrame(lb)[["username", "match_points", "group_points", "winner_points"]]
    df.columns = ["Player", "Match Points", "Group Points", "Winner Points"]
    df = df.sort_values("Match Points", ascending=False)

    # Filter by player (multi-select)
    all_players = df["Player"].tolist()
    selected_players = st.multiselect(
        "Filter players",
        options=all_players,
        default=all_players,
        label_visibility="collapsed",
    )
    df_filtered = df[df["Player"].isin(selected_players)] if selected_players else df

    # Stacked bar via Streamlit's built-in chart
    if not df_filtered.empty:
        st.bar_chart(
            df_filtered.set_index("Player"),
            use_container_width=True,
            color=["#C8102E", "#D4AF37", "#1E90FF"],
        )


def _render_podium(top: list[dict]):
    # Order: 2nd | 1st | 3rd
    order: list[dict] = []
    if len(top) >= 2:
        order.append(top[1])
    if len(top) >= 1:
        order.insert(len(order) // 2, top[0])
    if len(top) >= 3:
        order.append(top[2])

    heights = {1: "110px", 2: "80px", 3: "60px"}
    medals  = {1: "1st", 2: "2nd", 3: "3rd"}

    cols = st.columns(len(order))
    for col, entry in zip(cols, order):
        h = heights.get(entry["rank"], "60px")
        m = medals.get(entry["rank"], "")
        with col:
            st.markdown(
                f"""<div style="text-align:center;">
                    <div style="display:flex;justify-content:center;margin-bottom:4px;">
                        {get_avatar_svg(entry['avatar_emoji'], 38)}
                    </div>
                    <div style="font-weight:700;font-size:0.88rem;">{entry['username']}</div>
                    <div style="color:#D4AF37;font-weight:800;font-size:1.3rem;
                        font-family:'Bebas Neue',sans-serif;">{entry['total_points']:.0f} pts</div>
                    <div style="background:#2A2A2A;border:2px solid #D4AF37;
                        border-radius:8px 8px 0 0;height:{h};
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.5rem;font-weight:800;color:#D4AF37;
                        margin-top:8px;">{m}</div>
                </div>""",
                unsafe_allow_html=True,
            )
