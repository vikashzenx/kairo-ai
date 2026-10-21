
import streamlit as st
from google import genai
st.set_page_config(
    page_title="Kairo AI — Find Your Way Forward",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');

.stApp {
    background: #FAF8F2;
    color: #29392D;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] {
    background: rgba(250,248,242,0.95);
}
.block-container {
    max-width: 1120px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}
[data-testid="stSidebar"] {
    background: #F0EFE6;
    border-right: 1px solid #E4E2D8;
}
[data-testid="stSidebar"] * {
    color: #344636;
}
.brand {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 600;
    color: #344B37;
    letter-spacing: -1px;
}
.eyebrow {
    color: #778675;
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
}
.hero {
    background: linear-gradient(135deg, #E8EEE4, #F0F0E5);
    padding: 38px;
    border-radius: 24px;
    border: 1px solid #DFE6DA;
    margin: 18px 0 28px 0;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    line-height: 1.2;
    color: #2D4432;
    margin: 8px 0 12px 0;
}
.hero p {
    font-size: 16px;
    color: #657566;
    line-height: 1.7;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 25px;
    color: #304533;
    margin: 12px 0 6px 0;
}
div[data-testid="stForm"] {
    background: #FFFFFF;
    padding: 26px;
    border: 1px solid #E9E7DE;
    border-radius: 20px;
}
.stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: #FCFBF8;
    border-radius: 10px;
}
.stButton button, .stFormSubmitButton button {
    background: #637B65;
    color: white;
    border: 1px solid #637B65;
    border-radius: 11px;
    min-height: 45px;
    font-weight: 600;
    transition: all .2s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    background: #4C654F;
    color: white;
    border-color: #4C654F;
}
.tip-card {
    background: #FFFFFF;
    padding: 20px;
    border: 1px solid #E9E7DE;
    border-radius: 17px;
    min-height: 112px;
}
.tip-card b {
    color: #344B37;
    font-size: 15px;
}
.tip-card p {
    color: #7A8075;
    font-size: 13px;
    line-height: 1.5;
}
footer {visibility: hidden;}
.footer {
    text-align: center;
    padding: 28px 10px 12px;
    margin-top: 30px;
}
.footer-line {
    height: 1px;
    background: #E4E2D8;
    margin-bottom: 25px;
}
.footer-small {
    color: #92978B;
    font-size: 10px;
    letter-spacing: 3px;
}
.footer-name {
    color: #344B37;
    font-family: 'Playfair Display', serif;
    font-size: 23px;
    font-style: italic;
    margin: 12px 0 2px;
}
.footer-signature {
    color: #788B70;
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-style: italic;
}
.footer-tagline {
    color: #92978B;
    font-size: 10px;
    letter-spacing: 1.5px;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">🌿 Kairo</div>', unsafe_allow_html=True)
    st.caption("FIND YOUR WAY FORWARD")
    st.divider()

    page = st.radio(
        "YOUR SPACE",
        ["⌂  Home", "✳  My Roadmap", "◷  Progress"],
        label_visibility="visible",
    )

    st.divider()
    st.caption("SMALL STEPS. REAL GROWTH.")
    st.write("Your journey starts with one clear goal.")

st.markdown('<div class="eyebrow">YOUR PERSONAL GROWTH SPACE</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="eyebrow">A LITTLE CLARITY GOES A LONG WAY</div>
    <h1>Every goal has<br>a path.</h1>
    <p>Big dreams feel simpler when you know what to do next.<br>
    Tell us where you want to go. We'll help you plan the journey.</p>
</div>
""", unsafe_allow_html=True)

if page == "⌂  Home":
    st.markdown("<div class='section-title'>Let's find your direction.</div>",
                unsafe_allow_html=True)
    st.write("Start with a goal. Kairo will help you turn it into manageable steps.")

    with st.form("goal_form"):
        goal = st.text_area(
            "What's something you want to achieve?",
            placeholder="e.g. Learn Python and build my first AI project...",
            height=110,
        )

        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox(
                "Where are you starting from?",
                ["Beginner", "Intermediate", "Advanced"],
            )
        with col2:
            hours = st.selectbox(
                "Time you can give each day",
                [1, 2, 3, 4, 5, 6],
                format_func=lambda h: f"{h} hour{'s' if h > 1 else ''}",
            )

        submitted = st.form_submit_button(
            "Create My Roadmap  →",
            use_container_width=True,
        )

    if submitted:
        if goal.strip():
            st.session_state["goal"] = goal.strip()
            st.session_state["level"] = level
            st.session_state["hours"] = hours

            prompt = f"""
You are Kairo AI, a friendly goal-planning assistant.
Create a practical, personalized roadmap for this goal: {goal.strip()}

Starting level: {level}
Available time per day: {hours} hour(s)

Write in natural Hinglish (Hindi written in English/Roman letters mixed with simple English). Avoid Devanagari Hindi. Keep the language friendly, simple, and easy for a beginner to understand.
Include:
1. A short encouraging introduction
2. Four learning phases in order
3. Weekly targets and daily tasks
4. Tools or resources to learn
5. A simple way to track progress

Be realistic about the available daily time.
Use clear headings and bullet points.
"""

            try:
                with st.spinner("Kairo is creating your roadmap..."):
                    client = genai.Client(
                        api_key=st.secrets["GEMINI_API_KEY"]
                    )

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                    )

                st.session_state["roadmap"] = response.text
                st.success("Your personalized roadmap is ready!")

                st.markdown("### your personalized roadmap")
                st.markdown(st.session_state["roadmap"])

            except Exception as e:
                st.error(
    "AI se connection nahi ho paya. "
    "Gemini API connection check karo."
)
                st.caption(str(e))
        else:
            st.warning("Write your goal first, then let's get started.")

    st.markdown('<div class="section-title">The ' \
    'Kairo approach</div>',
            unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="tip-card">
            <b>01 · Find clarity</b>
            <p>Define what matters to you and where you want to go.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="tip-card">
            <b>02 · Make a plan</b>
            <p>Break a big ambition into smaller, practical steps.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="tip-card">
            <b>03 · Keep growing</b>
            <p>Track your progress and keep moving at your own pace.</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "✳  My Roadmap":
    st.markdown('<div class="section-title">Your roadmap</div>',
                unsafe_allow_html=True)
    if "goal" in st.session_state:
        st.write("**Your goal:**", st.session_state["goal"])
        st.write("**Starting level:**", st.session_state["level"])
        st.write("**Daily time:**", f'{st.session_state["hours"]} hour(s)')
        if "roadmap" in st.session_state:
            st.markdown(st.session_state["roadmap"])
        else:
            st.info("Create your roadmap from the Home page first.")
    else:
        st.info("Your journey starts on the Home page. Add a goal to see it here.")

elif page == "◷  Progress":
    st.markdown('<div class="section-title">Your progress</div>',
                unsafe_allow_html=True)
    st.write("Every small step counts.")
    st.info("Progress tracking will be available when we build the roadmap feature.")

st.markdown("""
<div class="footer">
    <div class="footer-line"></div>
    <p class="footer-small">A LITTLE PROGRESS, EVERY DAY</p>
    <p class="footer-name">Made with intention</p>
    <p class="footer-signature">— Vikash ✳</p>
    <p class="footer-tagline">KAIRO AI · FIND YOUR WAY FORWARD</p>
</div>
""", unsafe_allow_html=True)
