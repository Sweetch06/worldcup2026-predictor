"""
pages/predictions_page.py - Predictions hub. 
Features auto-repair for groups, dynamic match cards, and progress bars.
"""
import streamlit as st
from database import get_db
from models import Team, Match, MatchStage
from utils.ui import inject_css, page_header, require_login, format_kickoff, svg_icon
from utils.deadline import is_prediction_open, prediction_deadline_label
from utils.predictions import (upsert_group_predictions, get_user_group_predictions,
                                upsert_match_prediction, get_user_match_predictions,
                                upsert_winner_prediction, get_winner_prediction)
from api.football_api import _fallback_teams
from scoring import STAGE_POINTS

STAGE_LABELS = {
    MatchStage.GROUP:       "Group Stage",
    MatchStage.ROUND_OF_32: "Round of 32",
    MatchStage.ROUND_OF_16: "Round of 16",
    MatchStage.QUARTER:     "Quarter-Finals",
    MatchStage.SEMI:        "Semi-Finals",
    MatchStage.FINAL:       "Final",
}

# ── Flag Helpers ──────────────────────────────────────────────────────
COUNTRY_CODE = {
    "Brazil":"br","Argentina":"ar","France":"fr","England":"gb-eng","Germany":"de",
    "Spain":"es","Portugal":"pt","Netherlands":"nl","USA":"us","Mexico":"mx",
    "Canada":"ca","Japan":"jp","South Korea":"kr","Morocco":"ma","Senegal":"sn",
    "Colombia":"co","Uruguay":"uy","Ecuador":"ec","Switzerland":"ch","Belgium":"be",
    "Croatia":"hr","Serbia":"rs","Denmark":"dk","Austria":"at","Poland":"pl",
    "Australia":"au","Iran":"ir","Saudi Arabia":"sa","Cameroon":"cm","Nigeria":"ng",
    "Ghana":"gh","Ivory Coast":"ci","Venezuela":"ve","Bolivia":"bo","Paraguay":"py",
    "Qatar":"qa","Wales":"gb-wls","Tunisia":"tn","Costa Rica":"cr",
    "Algeria":"dz","Egypt":"eg","Congo DR":"cd","Uzbekistan":"uz","Peru":"pe",
    "Chile":"cl","Sweden":"se","Italy":"it","Turkey":"tr","Ukraine":"ua",
    "Scotland":"gb-sct","Hungary":"hu","Czech Republic":"cz","Mali":"ml",
    "Burkina Faso":"bf","South Africa":"za","Iraq":"iq","United Arab Emirates":"ae",
    "Oman":"om","China PR":"cn","New Zealand":"nz","Panama":"pa","Jamaica":"jm",
    "Honduras":"hn","El Salvador":"sv","Czechia":"cz","Bosnia-Herzegovina":"ba",
    "United States":"us","Haiti":"ht","Curaçao":"cw","Cape Verde Islands":"cv",
    "Norway":"no","Jordan":"jo","TBD": ""
}

def _flag_img(team_name, size=24):
    clean_name = team_name.strip() if team_name else ""
    code = COUNTRY_CODE.get(clean_name, "")
    if code:
        # Forçamos uma largura proporcional (ex: 32px largura para 24px altura)
        # O object-fit:cover garante que a bandeira enche esse espaço sem distorcer
        width = int(size * 1.35)
        return f'<img src="https://flagcdn.com/h40/{code}.png" style="width:{width}px; height:{size}px; object-fit:cover; border-radius:3px; vertical-align:middle; box-shadow:0 1px 3px rgba(0,0,0,0.3);" />'
    return "🏳️" if clean_name != "TBD" else "❓"

# ── Data Loading & Auto-Repair ────────────────────────────────────────
def _load_groups():
    with get_db() as db:
        missing = db.query(Team).filter((Team.group_letter == None) | (Team.group_letter == "")).first()
        if missing:
            matches = db.query(Match).filter(Match.group_letter != None, Match.group_letter != "").all()
            for m in matches:
                gl = m.group_letter.strip()[-1] if m.group_letter else ""
                if not gl: continue
                
                if m.home_team_id:
                    t_home = db.get(Team, m.home_team_id)
                    if t_home and not t_home.group_letter: t_home.group_letter = gl
                if m.away_team_id:
                    t_away = db.get(Team, m.away_team_id)
                    if t_away and not t_away.group_letter: t_away.group_letter = gl
            db.commit()

        teams = db.query(Team).order_by(Team.name).all()
        groups = {}
        for t in teams:
            if t.group_letter:
                gl = t.group_letter.strip()[-1]
                groups.setdefault(gl, []).append({
                    "id": t.id, "name": t.name, "tla": t.tla or "", "group_letter": gl
                })
        return groups

def _load_open_matches():
    with get_db() as db:
        matches = db.query(Match).filter(Match.status != "FINISHED").order_by(Match.kickoff_time).all()
        result = []
        for m in matches:
            home = db.get(Team, m.home_team_id) if m.home_team_id else None
            away = db.get(Team, m.away_team_id) if m.away_team_id else None
            result.append({
                "id": m.id, "stage": m.stage, "status": m.status or "SCHEDULED",
                "kickoff_time": m.kickoff_time,
                "home_name": home.name if home else "TBD",
                "away_name": away.name if away else "TBD",
            })
        return result

def _load_user_match_preds(user_id, room_id):
    with get_db() as db:
        return get_user_match_predictions(db, user_id, room_id)

def _load_winner_pred(user_id, room_id):
    with get_db() as db:
        return get_winner_prediction(db, user_id, room_id)

def _load_room_winner_picks(room_id):
    with get_db() as db:
        from models import TournamentWinnerPrediction, User as UserModel
        picks = (db.query(TournamentWinnerPrediction, UserModel)
                 .join(UserModel, TournamentWinnerPrediction.user_id == UserModel.id)
                 .filter(TournamentWinnerPrediction.room_id == room_id).all())
        return [{"team_id": p.team_id, "username": u.username, "avatar_emoji": u.avatar_emoji,
                 "user_id": u.id} for p, u in picks]

# ── Render Logic ──────────────────────────────────────────────────────
def render():
    inject_css()
    require_login()
    user = st.session_state.user
    room = st.session_state.get("room")

    page_header("PREDICTIONS", f"Room: {room['name']}" if room else "")

    if not room:
        st.info("Please select or join a room first.")
        return

    tab_groups, tab_matches, tab_winner = st.tabs([
        "Group Standings", "Match Results", "Tournament Winner"
    ])

    with tab_groups:
        st.markdown("""<div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:15px; margin-bottom:20px;">
            Predict the final order of each group (1st to 4th).<br>
            <span style="color:var(--secondary); font-weight:700;">3 pts</span> if all correct | <span style="color:var(--secondary); font-weight:700;">1 pt</span> if 2+ correct
        </div>""", unsafe_allow_html=True)
        groups = _load_groups()
        if not groups:
            st.info("No group data yet. Go to Admin → Sync All Matches first.")
        else:
            total_groups = len(groups)
            filled_groups = 0
            
            with get_db() as db:
                for gl, teams_in_group in groups.items():
                    existing = get_user_group_predictions(db, user["id"], room["id"], gl)
                    if existing and len(existing) == len(teams_in_group):
                        filled_groups += 1
            
            pct_groups = (filled_groups / total_groups * 100) if total_groups else 0
            
            st.markdown(f"""
                <div style="margin-bottom:25px;">
                    <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:0.8rem; margin-bottom:6px;">
                        <span>Your Progress</span><span>{filled_groups} / {total_groups}</span>
                    </div>
                    <div style="background:var(--surface3); border-radius:10px; height:8px; overflow:hidden;">
                        <div style="background:linear-gradient(90deg, var(--primary), var(--secondary)); width:{pct_groups}%; height:100%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for gl in sorted(groups.keys()):
                _render_group_pred(gl, groups[gl], user, room)

    with tab_matches:
        all_matches = _load_open_matches()
        matches = [m for m in all_matches if m["stage"] != MatchStage.THIRD_PLACE]
        user_preds = _load_user_match_preds(user["id"], room["id"])

        if not matches:
            st.info("No upcoming matches available for predictions.")
        else:
            total = len(matches)
            filled = sum(1 for m in matches if m["id"] in user_preds)
            pct = (filled / total * 100) if total else 0
            st.markdown(f"""
                <div style="margin-bottom:25px;">
                    <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:0.8rem; margin-bottom:6px;">
                        <span>Your Progress</span><span>{filled} / {total}</span>
                    </div>
                    <div style="background:var(--surface3); border-radius:10px; height:8px; overflow:hidden;">
                        <div style="background:linear-gradient(90deg, var(--primary), var(--secondary)); width:{pct}%; height:100%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            by_stage = {}
            for m in matches:
                by_stage.setdefault(m["stage"], []).append(m)

            for stage in STAGE_LABELS.keys():
                stage_matches = by_stage.get(stage, [])
                if not stage_matches: continue
                pts = STAGE_POINTS.get(stage, 1)
                st.subheader(f"{STAGE_LABELS[stage]} — {pts} pt{'s' if pts!=1 else ''}")
                for m in stage_matches:
                    _render_prediction_card(m, user, room, user_preds)

    with tab_winner:
        _render_winner_tab(user, room)

def _render_prediction_card(m, user, room, user_preds):
    current = user_preds.get(m["id"])
    open_pred, why = is_prediction_open(m, room)
    deadline_lbl = prediction_deadline_label(m, room)
    
    home_name = m.get('home_name', 'TBD')
    away_name = m.get('away_name', 'TBD')

    options_map = {
        "home": home_name.upper(), 
        "draw": "DRAW", 
        "away": away_name.upper()
    }

    card_html = f'''
    <div style="background:var(--surface2); border:1px solid var(--border); border-radius:12px; padding:15px; margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="flex:1; display:flex; align-items:center; gap:12px;">
                {_flag_img(home_name, 28)}
                <span style="font-weight:700; font-size:1rem;">{home_name}</span>
            </div>
            <div style="flex:0.3; text-align:center; color:var(--text-dim); font-weight:800;">VS</div>
            <div style="flex:1; display:flex; align-items:center; justify-content:flex-end; gap:12px;">
                <span style="font-weight:700; font-size:1rem;">{away_name}</span>
                {_flag_img(away_name, 28)}
            </div>
        </div>
        <div style="text-align:center; color:var(--text-muted); font-size:0.72rem; margin-top:8px;">
            {format_kickoff(m['kickoff_time'])} &nbsp;·&nbsp; {deadline_lbl}
        </div>
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)

    if open_pred:
        idx = ["home", "draw", "away"].index(current) if current in ["home", "draw", "away"] else 1
        
        choice = st.radio("Pick", ["home", "draw", "away"], index=idx, 
                          format_func=lambda x: options_map[x],
                          horizontal=True, label_visibility="collapsed", 
                          key=f"qp_{m['id']}_{room['id']}")
        
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        
        if st.button("SAVE PREDICTION", key=f"qs_{m['id']}_{room['id']}", use_container_width=True):
            with get_db() as db:
                ok, msg = upsert_match_prediction(db, user["id"], m["id"], room["id"], choice)
            if ok:
                st.toast(f"Saved: {options_map[choice]}", icon="✅")
                st.rerun()
            else:
                st.error(msg)
    else:
        current_pick = options_map.get(current, "").upper()
        pick_html = f' &nbsp;·&nbsp; Your pick: <b style="color:var(--secondary);">{current_pick}</b>' if current else ""
        
        locked_html = f'''
        <div style="text-align:center; padding:10px; background:var(--surface3); border-radius:8px; font-size:0.85rem; color:var(--text-muted); border:1px dashed var(--border);">
            {svg_icon("lock", 14, "#B8960C")} {why} {pick_html}
        </div>
        '''
        st.markdown(locked_html, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

def _render_group_pred(gl, teams, user, room):
    with get_db() as db:
        existing = get_user_group_predictions(db, user["id"], room["id"], gl)
    
    team_by_id = {t["id"]: t["name"] for t in teams}
    team_by_name = {t["name"]: t["id"] for t in teams}

    if existing:
        ordered_ids = existing + [t["id"] for t in teams if t["id"] not in existing]
    else:
        ordered_ids = [t["id"] for t in teams]

    with st.expander(f"Group {gl} Standings", expanded=False):
        chosen_names = []
        selected_ids = []
        
        st.markdown("<div style='font-size:0.8rem; color:var(--text-muted); margin-bottom:8px;'>Select predicted finishing order:</div>", unsafe_allow_html=True)

        for i in range(len(teams)):
            remaining = [team_by_id[tid] for tid in ordered_ids if team_by_id[tid] not in chosen_names]
            if not remaining: break
            
            default_val = team_by_id.get(ordered_ids[i])
            if default_val not in remaining: default_val = remaining[0]
            
            c1, c2 = st.columns([1, 5])
            with c2:
                choice = st.selectbox(f"{i+1}st Place", remaining, index=remaining.index(default_val), key=f"grp_{gl}_{i}_{room['id']}", label_visibility="collapsed")
            with c1:
                st.markdown(f"<div style='display:flex; align-items:center; justify-content:flex-end; height:40px; gap:8px;'><span style='color:var(--text-dim); font-weight:bold;'>{i+1}º</span> {_flag_img(choice, 20)}</div>", unsafe_allow_html=True)
                
            chosen_names.append(choice)
            selected_ids.append(team_by_name[choice])

        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        
        if st.button(f"SAVE GROUP {gl}", key=f"save_grp_{gl}_{room['id']}", use_container_width=True):
            with get_db() as db:
                ok, msg = upsert_group_predictions(db, user["id"], room["id"], gl, selected_ids)
            if ok: st.success(msg)
            else: st.error(msg)

def _render_winner_tab(user, room):
    with get_db() as db:
        teams = db.query(Team).order_by(Team.name).all()
        options = {t.name: t.id for t in teams}
        current_id = get_winner_prediction(db, user["id"], room["id"])
        picks = _load_room_winner_picks(room["id"])

    cur_name = next((name for name, tid in options.items() if tid == current_id), None)

    winner_content = f'<div style="font-size:3rem; margin:10px 0;">{_flag_img(cur_name, 60)}</div><div style="font-weight:700; font-size:1.2rem;">{cur_name}</div>' if cur_name else '<p style="color:var(--text-dim);">Make your pick below</p>'

    st.markdown(f'''
    <div style="background:var(--surface2); border:2px solid var(--secondary); border-radius:15px; padding:25px; text-align:center; margin-bottom:25px;">
        <h3 style="margin:0;">World Cup Winner</h3>
        <p style="color:var(--secondary); font-weight:800; font-size:1.2rem; margin:5px 0;">Worth 15 Points</p>
        {winner_content}
    </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Select Champion", list(options.keys()), 
                               index=list(options.keys()).index(cur_name) if cur_name in options else 0,
                               label_visibility="collapsed")
    with col2:
        if st.button("Save", key="save_winner_btn", use_container_width=True):
            with get_db() as db:
                ok, msg = upsert_winner_prediction(db, user["id"], room["id"], options[selected])
            if ok: st.rerun()
            else: st.error(msg)

    st.markdown("---")
    st.subheader("What others picked")
    if picks:
        cols = st.columns(4)
        for i, pick in enumerate(picks):
            with cols[i % 4]:
                team_name = next((n for n,id in options.items() if id==pick['team_id']), "TBD")
                st.markdown(f'''
                <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:10px; text-align:center; margin-bottom:10px;">
                    <div style="font-size:1.2rem;">{pick['avatar_emoji']}</div>
                    <div style="font-size:0.75rem; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{pick['username']}</div>
                    <div style="margin:5px 0;">{_flag_img(team_name, 20)}</div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.info("No winner predictions in this room yet.")
