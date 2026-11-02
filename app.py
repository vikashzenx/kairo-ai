import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from google import genai

st.set_page_config(
    page_title="Kairo AI — Find Your Way Forward",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- THEME --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    --forest: #142D23;
    --forest-light: #1E4031;
    --sage: #B9C9A9;
    --cream: #F5F2E9;
    --muted: #B7C4B8;
    --line: rgba(222, 234, 219, 0.16);
}

.stApp {
    background: var(--forest);
    color: var(--cream);
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: var(--forest); }
[data-testid="stSidebar"] { display: none; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 { color: var(--cream); }
p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
hr { border-color: var(--line); }

.brand {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: -1px;
}
.brand span { color: var(--sage); }
.brand-caption {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: -5px;
}
div[role="radiogroup"] {
    gap: 7px;
    justify-content: flex-end;
}
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--line);
    border-radius: 30px;
    padding: 7px 14px;
}
div[role="radiogroup"] label p {
    color: var(--cream) !important;
    font-weight: 600;
}
div[role="radiogroup"] label:has(input:checked) {
    background: var(--sage);
    border-color: var(--sage);
}
div[role="radiogroup"] label:has(input:checked) p {
    color: var(--forest) !important;
}

.eyebrow {
    color: var(--sage);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.hero {
    background: linear-gradient(130deg, #234735, #1A382A 65%, #294838);
    border: 1px solid rgba(204, 222, 192, 0.18);
    border-radius: 26px;
    padding: 40px;
    margin: 24px 0 28px;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(36px, 5vw, 60px);
    line-height: 1.12;
    letter-spacing: -1.5px;
    margin: 14px 0;
    color: #F7F4EA;
}
.hero p {
    font-size: 15px;
    line-height: 1.8;
    max-width: 600px;
    color: #C0D0C1;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 29px;
    color: var(--cream);
    margin: 8px 0;
}
.subtext { color: var(--muted); font-size: 14px; line-height: 1.7; }
.panel, .metric-card, .tip-card {
    background: var(--forest-light);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 21px;
}
.panel { margin: 12px 0; }
.metric-card { min-height: 120px; }
.metric-label {
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}
.metric-value {
    color: var(--sage);
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    margin-top: 9px;
    overflow-wrap: anywhere;
}
.tip-card { min-height: 145px; }
.tip-number { color: var(--sage); font-size: 12px; letter-spacing: 2px; }
.tip-title { color: var(--cream); font-weight: 700; margin: 12px 0 6px; }
.tip-copy { color: var(--muted); font-size: 13px; line-height: 1.6; }

.stTextArea textarea, .stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    background: #10271D;
    color: var(--cream);
    border: 1px solid #45624D;
    border-radius: 11px;
}

.stButton button,
.stFormSubmitButton button {
    background: #E8E3D3 !important;
    color: #203A2E !important;
    border: 1px solid #E8E3D3 !important;
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #D0DEC2 !important;
    border-color: #D0DEC2 !important;
    color: #203A2E !important;
}


.stProgress > div > div > div > div { background: var(--sage); }
.roadmap-content {
    background: #193628;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 24px;
    line-height: 1.8;
}
.footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 24px;
    border-top: 1px solid var(--line);
}
.footer-title {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-style: italic;
    color: var(--cream);
}
.footer-caption {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 2px;
}
@media (max-width: 700px) {
    .hero { padding: 25px; }
    .hero h1 { font-size: 38px; }
}
</style>
""", unsafe_allow_html=True)


# -------------------- SESSION STATE --------------------

defaults = {
    "goal": "",
    "level": "Beginner",
    "hours": 2,
    "roadmap": "",
    "tasks": [],
    "task_goal": "",
    "top_navigation": "Home",
    "chat_messages": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- HELPERS --------------------

def create_initial_tasks(goal: str) -> list[dict]:
    """Create an editable starter checklist for a new roadmap."""
    return [
        {"title": f"Write down the first step for: {goal}", "done": False},
        {"title": "Work on the first learning phase", "done": False},
        {"title": "Practise what I learned", "done": False},
        {"title": "Review my progress this week", "done": False},
    ]
def today_ist() -> date:
    return datetime.now(ZoneInfo("Asia/Kolkata")).date()


def fmt_time(minutes: int) -> str:
    return f"{minutes // 60}h {minutes % 60}m"


def metric_card(label: str, value: str) -> str:
    return (
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>'
    )


def calc_streak(active_days: set, today: date) -> tuple:
    d = today if today.isoformat() in active_days else today - timedelta(days=1)
    current = 0

    while d.isoformat() in active_days:
        current += 1
        d -= timedelta(days=1)

    best = run = 0
    prev = None

    for s in sorted(active_days):
        day = date.fromisoformat(s)
        run = run + 1 if prev and (day - prev).days == 1 else 1
        best = max(best, run)
        prev = day

    return current, best


def show_roadmap() -> None:
    st.markdown('<div class="roadmap-content">', unsafe_allow_html=True)
    st.markdown(st.session_state["roadmap"])
    st.markdown("</div>", unsafe_allow_html=True)


def show_footer() -> None:
    st.markdown("""
    <div class="footer">
        <div class="footer-caption">A LITTLE PROGRESS, EVERY DAY</div>
        <div class="footer-title">Made with intention — Vikash ✳</div>
        <div class="footer-caption">KAIRO AI · FIND YOUR WAY FORWARD</div>
    </div>
    """, unsafe_allow_html=True)



def go_to(page_name: str) -> None:
    st.session_state["top_navigation"] = page_name

    st.rerun()


# -------------------- TOP NAVIGATION --------------------

left, right = st.columns([1, 2])

with left:
    st.markdown(
        '<div class="brand">🌿 Kairo<span>.</span></div>'
        '<div class="brand-caption">FIND YOUR WAY FORWARD</div>',
        unsafe_allow_html=True,
    )

with right:
    st.radio(
        "Navigation",
        ["Home", "My Roadmap", "Program Tracker", "Progress", "AI Chat"],
        horizontal=True,
        label_visibility="collapsed",
        key="top_navigation",
    )

page = st.session_state["top_navigation"]
st.markdown("---")


# -------------------- HOME --------------------

if page == "Home":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">YOUR NEXT CHAPTER STARTS HERE</div>
        <h1>Big dreams.<br>Clear direction.</h1>
        <p>
            You don't need to figure everything out today.
            Start with one goal, and let Kairo help you turn it
            into small, practical steps.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">What would you like to achieve?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Tell us where you want to go. '
        'We will help you plan how to get there.</div>',
        unsafe_allow_html=True,
    )

    with st.form("goal_form"):
        goal = st.text_area(
            "Your goal",
            value=st.session_state["goal"],
            placeholder=(
                "For example: Learn Python, build an AI project, "
                "prepare for JLPT N5..."
            ),
            height=110,
        )
        col1, col2 = st.columns(2)

        with col1:
            level = st.selectbox(
                "Your current level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(
                    st.session_state["level"]
                ),
            )

        with col2:
            hours = st.selectbox(
                "Time available per day",
                [1, 2, 3, 4, 5, 6],
                index=[1, 2, 3, 4, 5, 6].index(
                    st.session_state["hours"]
                ),
                format_func=lambda h: f"{h} hour" if h == 1 else f"{h} hours",
            )

        submitted = st.form_submit_button(
            "Create my roadmap  →",
            use_container_width=True,
        )

    if submitted:
        if not goal.strip():
            st.warning("Pehle apna goal likho, phir roadmap banate hain.")
        else:
            st.session_state["goal"] = goal.strip()
            st.session_state["level"] = level
            st.session_state["hours"] = hours

            prompt = f"""
You are Kairo AI, a friendly and practical goal-planning assistant.

User goal: {goal.strip()}
Current level: {level}
Available time each day: {hours} hour(s)

Create a personalized, realistic roadmap.

Write in natural Hinglish using Roman letters only.
Do not use Devanagari script.
Keep explanations simple, supportive and practical.

Include:
1. A short introduction tailored to the goal.
2. Four phases in a sensible order.
3. Weekly targets for each phase.
4. Actionable daily tasks that fit the available time.
5. Useful tools and learning resources.
6. A way to measure progress.
7. Common mistakes to avoid.
8. A realistic suggested timeline.

Use clear Markdown headings and bullet points.
Do not promise guaranteed results.
"""

            try:
                with st.spinner("Kairo is building your personal roadmap..."):
                    client = genai.Client(
                        api_key=st.secrets["GEMINI_API_KEY"]
                    )
                    # Keep the model name that was configured in the current app.
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                    )

                if not response.text:
                    st.error("AI ne empty response diya. Please try again.")
                else:
                    st.session_state["roadmap"] = response.text
                    st.session_state["tasks"] = create_initial_tasks(goal.strip())
                    st.session_state["task_goal"] = goal.strip()
                    st.success("Tumhara roadmap ready hai! 🌿")
                    st.markdown("### Your personalized roadmap")
                    show_roadmap()

            except Exception as e:
                error_text = str(e)
                if "GEMINI_API_KEY" in error_text or "secrets" in error_text.lower():
                    st.error(
                        "Gemini API key nahi mili. Local project mein "
                        ".streamlit/secrets.toml aur Cloud secrets check karo."
                    )
                else:
                    st.error(
                        "Gemini se connection nahi ho paya. API availability, "
                        "model name aur API key check karo."
                    )
                    st.caption(error_text)

    st.markdown("---")
    st.markdown(
        '<div class="section-title">The Kairo approach</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    cards = [
        ("01", "Find clarity", "Apne goal ko samjho aur decide karo ki tumhe kya achieve karna hai."),
        ("02", "Build your path", "Bade goal ko manageable steps aur weekly targets mein divide karo."),
        ("03", "Keep moving", "Tasks complete karo, progress check karo aur zarurat par plan adjust karo."),
    ]
    for col, item in zip([c1, c2, c3], cards):
        with col:
            st.markdown(
                f"""
                <div class="tip-card">
                    <div class="tip-number">{item[0]}</div>
                    <div class="tip-title">{item[1]}</div>
                    <div class="tip-copy">{item[2]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# -------------------- MY ROADMAP --------------------

elif page == "My Roadmap":
    st.markdown('<div class="eyebrow">YOUR PERSONAL PLAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">My Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtext">Your goal, your pace, your next step.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state["goal"] and st.session_state["roadmap"]:
        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Your goal</div>
                    <div style="color:#F5F2E9;font-size:17px;margin-top:12px;overflow-wrap:anywhere;">
                        {st.session_state["goal"][:90]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Current level</div>
                    <div class="metric-value">{st.session_state["level"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Daily commitment</div>
                    <div class="metric-value">{st.session_state["hours"]} hr/day</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("")
        show_roadmap()

        if st.button("Create a new roadmap"):
            st.session_state["roadmap"] = ""
            st.session_state["tasks"] = []
            st.session_state["task_goal"] = ""
            go_to("Home")
    elif st.session_state["goal"]:
        st.info("Goal saved hai, lekin roadmap abhi generate nahi hua. Home par jaakar roadmap create karo.")
        if st.button("Go to Home"):
            go_to("Home")
    else:
        st.markdown("""
        <div class="panel">
            <div class="section-title">Your journey starts here.</div>
            <p class="subtext">
                Abhi koi roadmap nahi hai. Home page par apna goal add karo
                aur Kairo ko tumhare liye plan banane do.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create my first roadmap →"):
            go_to("Home")


# -------------------- PROGRAM TRACKER --------------------

elif page == "Program Tracker":
    st.markdown(
        '<div class="eyebrow">YOUR DAILY MOMENTUM</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-title">Program Tracker</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Plan your day, track study time, '
        'and keep moving towards your goal.</div>',
        unsafe_allow_html=True,
    )

    today = today_ist()
    today_key = today.isoformat()

    # Initialise tracker data
    if "tracker_tasks" not in st.session_state:
        st.session_state["tracker_tasks"] = []
    if "study_logs" not in st.session_state:
        st.session_state["study_logs"] = []
    if "tracker_task_counter" not in st.session_state:
        st.session_state["tracker_task_counter"] = 0

    tracker_tasks = st.session_state["tracker_tasks"]
    study_logs = st.session_state["study_logs"]

    # Today's overview
    today_tasks = [
        task for task in tracker_tasks
        if task["date"] == today_key
    ]
    completed_today = sum(1 for task in today_tasks if task["done"])
    total_today = len(today_tasks)
    progress_today = (
        int(completed_today / total_today * 100)
        if total_today else 0
    )
    minutes_today = sum(
        log["minutes"] for log in study_logs
        if log["date"] == today_key
    )

    st.markdown("### Today's Overview")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'Tasks completed</div><div class="metric-value">'
            f'{completed_today}/{total_today}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'Today progress</div><div class="metric-value">'
            f'{progress_today}%</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'Study time</div><div class="metric-value">'
            f'{minutes_today // 60}h {minutes_today % 60}m</div></div>',
            unsafe_allow_html=True,
        )

    st.progress(progress_today)

    # Add tasks
    st.markdown("---")
    st.markdown("### Daily Tasks")

    with st.form("tracker_add_task", clear_on_submit=True):
        task_title = st.text_input(
            "Task name",
            placeholder="e.g. Practise Python for 30 minutes",
        )
        task_date = st.date_input("Task date", value=today)
        add_task = st.form_submit_button(
            "＋ Add Task",
            use_container_width=True,
        )

    if add_task:
        if task_title.strip():
            st.session_state["tracker_task_counter"] += 1
            st.session_state["tracker_tasks"].append({
                "id": st.session_state["tracker_task_counter"],
                "title": task_title.strip(),
                "date": task_date.isoformat(),
                "done": False,
            })
            st.rerun()
        else:
            st.warning("Pehle task ka naam likho.")

    display_date = st.date_input(
        "View tasks for",
        value=today,
        key="tracker_view_date",
    )
    selected_tasks = [
        task for task in st.session_state["tracker_tasks"]
        if task["date"] == display_date.isoformat()
    ]

    if not selected_tasks:
        st.info("Is date ke liye tasks nahi hain. Upar se add karo.")
    else:
        for task in selected_tasks:
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

            with col1:
                task["done"] = st.checkbox(
                    "Done",
                    value=task["done"],
                    key=f"tracker_done_{task['id']}",
                    label_visibility="collapsed",
                )

            with col2:
                edited_title = st.text_input(
                    "Task",
                    value=task["title"],
                    key=f"tracker_title_{task['id']}",
                    label_visibility="collapsed",
                )
                if edited_title.strip():
                    task["title"] = edited_title.strip()

            with col3:
                if st.button("Delete", key=f"tracker_delete_{task['id']}"):
                    st.session_state["tracker_tasks"] = [
                        item for item in st.session_state["tracker_tasks"]
                        if item["id"] != task["id"]
                    ]
                    st.rerun()

    # Study time logger
    st.markdown("---")
    st.markdown("### Study Time Log")

    with st.form("tracker_study_log", clear_on_submit=True):
        log_date = st.date_input(
            "Study date",
            value=today,
            key="tracker_log_date",
        )
        hours_studied = st.number_input(
            "Hours studied",
            min_value=0,
            max_value=24,
            value=1,
        )
        minutes_studied = st.selectbox(
            "Extra minutes",
            [0, 15, 30, 45],
        )
        study_note = st.text_input(
            "What did you study?",
            placeholder="e.g. Python functions",
        )
        save_log = st.form_submit_button(
            "Save Study Log",
            use_container_width=True,
        )

    if save_log:
        total_minutes = int(hours_studied) * 60 + minutes_studied

        if total_minutes == 0:
            st.warning("Study time 0 se zyada enter karo.")
        else:
            st.session_state["study_logs"].append({
                "date": log_date.isoformat(),
                "minutes": total_minutes,
                "note": study_note.strip() or "Study session",
            })
            st.success("Study log saved!")
            st.rerun()

    # Weekly overview
    st.markdown("---")
    st.markdown("### This Week")

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    week_logs = [
        log for log in st.session_state["study_logs"]
        if week_start.isoformat() <= log["date"] <= week_end.isoformat()
    ]
    week_minutes = sum(log["minutes"] for log in week_logs)

    week_tasks = [
        task for task in st.session_state["tracker_tasks"]
        if week_start.isoformat() <= task["date"] <= week_end.isoformat()
    ]
    week_done = sum(1 for task in week_tasks if task["done"])
    week_total = len(week_tasks)
    week_percent = (
        int(week_done / week_total * 100) if week_total else 0
    )

    w1, w2, w3 = st.columns(3)
    with w1:
        st.metric("Study time", f"{week_minutes // 60}h {week_minutes % 60}m")
    with w2:
        st.metric("Tasks completed", f"{week_done}/{week_total}")
    with w3:
        st.metric("Task completion", f"{week_percent}%")

    daily_study = {}
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        day_name = day.strftime("%a")
        daily_study[day_name] = sum(
            log["minutes"] for log in week_logs
            if log["date"] == day.isoformat()
        )

    st.markdown("#### Daily study minutes")
    st.bar_chart(daily_study)



# -------------------- PROGRESS --------------------

elif page == "Progress":
    today = today_ist()
    today_key = today.isoformat()

    tracker_tasks = st.session_state.get("tracker_tasks", [])
    study_logs = st.session_state.get("study_logs", [])

    st.markdown(
        '<div class="eyebrow">EVERY STEP COUNTS</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-title">Your Progress</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">A clear picture of your consistency, '
        'study time, and daily momentum.</div>',
        unsafe_allow_html=True,
    )

    # Collect activity dates from study logs and completed tracker tasks.
    active_days = {
        log["date"] for log in study_logs
        if int(log.get("minutes", 0)) > 0
    }
    active_days.update(
        task["date"] for task in tracker_tasks
        if task.get("done", False)
    )

    current_streak, best_streak = calc_streak(active_days, today)

    # Today's and all-time totals.
    today_minutes = sum(
        int(log.get("minutes", 0))
        for log in study_logs
        if log["date"] == today_key
    )
    today_tasks = [
        task for task in tracker_tasks
        if task["date"] == today_key
    ]
    today_done = sum(1 for task in today_tasks if task.get("done", False))
    all_minutes = sum(int(log.get("minutes", 0)) for log in study_logs)
    all_done = sum(1 for task in tracker_tasks if task.get("done", False))
    all_tasks = len(tracker_tasks)
    overall_completion = int(all_done / all_tasks * 100) if all_tasks else 0

    # Main metrics.
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(metric_card("Current streak", f"{current_streak} days"),
                    unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("Best streak", f"{best_streak} days"),
                    unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card("Total study time", fmt_time(all_minutes)),
                    unsafe_allow_html=True)
    with m4:
        st.markdown(metric_card("Tasks completed", f"{all_done}/{all_tasks}"),
                    unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="section-title">Today at a glance</div>',
                unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1:
        st.metric("Study time today", fmt_time(today_minutes))
    with t2:
        st.metric("Tasks completed today", f"{today_done}/{len(today_tasks)}")
    with t3:
        st.metric("Overall task completion", f"{overall_completion}%")

    st.progress(overall_completion,
                text=f"{overall_completion}% of your tracked tasks completed")

    # Compare the latest 7 days with the previous 7 days.
    this_week_start = today - timedelta(days=6)
    previous_week_start = today - timedelta(days=13)
    previous_week_end = today - timedelta(days=7)

    this_week_logs = [
        log for log in study_logs
        if this_week_start.isoformat() <= log["date"] <= today_key
    ]
    previous_week_logs = [
        log for log in study_logs
        if previous_week_start.isoformat() <= log["date"] <= previous_week_end.isoformat()
    ]
    this_week_minutes = sum(int(log.get("minutes", 0)) for log in this_week_logs)
    previous_week_minutes = sum(int(log.get("minutes", 0)) for log in previous_week_logs)

    this_week_tasks = [
        task for task in tracker_tasks
        if this_week_start.isoformat() <= task["date"] <= today_key
    ]
    previous_week_tasks = [
        task for task in tracker_tasks
        if previous_week_start.isoformat() <= task["date"] <= previous_week_end.isoformat()
    ]
    this_week_done = sum(1 for task in this_week_tasks if task.get("done", False))
    previous_week_done = sum(1 for task in previous_week_tasks if task.get("done", False))

    st.markdown("---")
    st.markdown('<div class="section-title">Last 7 days</div>',
                unsafe_allow_html=True)
    w1, w2, w3 = st.columns(3)
    with w1:
        st.metric("Study time", fmt_time(this_week_minutes))
    with w2:
        st.metric("Tasks completed", f"{this_week_done}/{len(this_week_tasks)}")
    with w3:
        st.metric("Active days", len({
            log["date"] for log in this_week_logs
            if int(log.get("minutes", 0)) > 0
        } | {
            task["date"] for task in this_week_tasks
            if task.get("done", False)
        }))

    if previous_week_minutes or previous_week_tasks:
        if this_week_minutes > previous_week_minutes:
            st.success(
                f"Study time is up by {fmt_time(this_week_minutes - previous_week_minutes)} "
                "compared with the previous 7 days."
            )
        elif this_week_minutes < previous_week_minutes:
            st.info(
                f"Study time is down by {fmt_time(previous_week_minutes - this_week_minutes)} "
                "compared with the previous 7 days. You can build momentum again."
            )
        else:
            st.info("Your study time is the same as the previous 7 days.")

    # Last 30 days chart.
    st.markdown("---")
    st.markdown('<div class="section-title">Your 30-day activity</div>',
                unsafe_allow_html=True)

    chart_rows = []
    for offset in range(29, -1, -1):
        day = today - timedelta(days=offset)
        minutes = sum(
            int(log.get("minutes", 0))
            for log in study_logs
            if log["date"] == day.isoformat()
        )
        chart_rows.append({"Date": day, "Study minutes": minutes})

    chart_df = pd.DataFrame(chart_rows).set_index("Date")
    st.bar_chart(chart_df, y="Study minutes", use_container_width=True)

    # Weekly goal based on the daily hours selected while creating the roadmap.
    daily_target = int(st.session_state.get("hours", 2)) * 60
    target_days = sum(
        1 for offset in range(6, -1, -1)
        if sum(
            int(log.get("minutes", 0))
            for log in study_logs
            if log["date"] == (today - timedelta(days=offset)).isoformat()
        ) >= daily_target
    )
    st.caption(
        f"Daily study target: {fmt_time(daily_target)} · "
        f"You reached it on {target_days} of the last 7 days."
    )

    # AI-generated weekly reflection, only when the user asks for it.
    st.markdown("---")
    st.markdown('<div class="section-title">Your AI weekly review</div>',
                unsafe_allow_html=True)
    st.caption("Kairo will review your recent activity and suggest practical next steps.")

    if st.button("Generate my weekly review", key="generate_weekly_review"):
        review_data = {
            "goal": st.session_state.get("goal", "Not set"),
            "study_minutes_last_7_days": this_week_minutes,
            "study_minutes_previous_7_days": previous_week_minutes,
            "tasks_completed_last_7_days": this_week_done,
            "tasks_created_last_7_days": len(this_week_tasks),
            "current_streak_days": current_streak,
            "daily_target_minutes": daily_target,
            "target_reached_days": target_days,
        }
        review_prompt = f"""
You are Kairo AI, a supportive and practical study coach.
Review this user's activity data:
{review_data}

Write in natural Hinglish using Roman letters only. Do not use Devanagari.
Give an honest, encouraging review in this structure:
1. What went well
2. What needs attention
3. One realistic focus for the next 7 days
4. Three small actionable steps

Do not invent activity or claim progress that is not present in the data.
Keep it concise and specific.
"""
        try:
            with st.spinner("Kairo is reviewing your progress..."):
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=review_prompt,
                )
            if response.text:
                st.session_state["weekly_review"] = response.text
            else:
                st.warning("Kairo could not create a review just now. Try again.")
        except Exception as e:
            error_text = str(e)
            if "GEMINI_API_KEY" in error_text or "secrets" in error_text.lower():
                st.error(
                    "Gemini API key nahi mili. .streamlit/secrets.toml "
                    "ya Streamlit Cloud secrets check karo."
                )
            else:
                st.error(f"Weekly review generate nahi ho paya: {error_text}")

    if st.session_state.get("weekly_review"):
        st.markdown('<div class="roadmap-content">', unsafe_allow_html=True)
        st.markdown(st.session_state["weekly_review"])
        st.markdown('</div>', unsafe_allow_html=True)

    if not tracker_tasks and not study_logs:
        st.info(
            "Abhi tracker data nahi hai. Program Tracker mein tasks add karo "
            "aur study time log karo. Tumhara Progress dashboard yahan update hoga."
        )



# -------------------- AI CHAT --------------------

elif page == "AI Chat":
    st.markdown(
        '<div class="eyebrow">YOUR AI COMPANION</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-title">AI Chat Assistant</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtext">Ask anything. Explore ideas, solve problems, '
        'or take your next step with Kairo.</div>',
        unsafe_allow_html=True,
    )

    # Display previous messages
    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask Kairo anything...")

    if user_prompt:
        st.session_state["chat_messages"].append({
            "role": "user",
            "content": user_prompt,
        })

        # Build conversation context for Gemini
        conversation = []
        for message in st.session_state["chat_messages"]:
            speaker = "User" if message["role"] == "user" else "Kairo"
            conversation.append(f"{speaker}: {message['content']}")

        prompt = f"""
You are Kairo AI, a friendly and helpful AI chat assistant.
Reply naturally in Hinglish using Roman letters, unless the user
asks for another language. Help with general questions, studies,
coding, career planning, and goal guidance.
Be accurate, practical, and clear. Never pretend to know something
you do not know.

Conversation so far:
{chr(10).join(conversation)}

Kairo:
"""

        try:
            with st.spinner("Kairo is thinking..."):
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                )

            answer = response.text or (
                "Mujhe is baar clear response nahi mila. Dobara try karo."
            )

            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": answer,
            })
            st.rerun()

        except Exception as e:
            # Remove the unanswered user message so it can be retried cleanly.
            st.session_state["chat_messages"].pop()
            st.error("Kairo abhi reply nahi kar paaya. Dobara try karo.")
            st.caption(str(e))

    if st.button("Clear chat"):
        st.session_state["chat_messages"] = []
        st.rerun()



# -------------------- FOOTER --------------------

show_footer()
