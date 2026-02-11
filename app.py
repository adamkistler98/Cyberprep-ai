import streamlit as st
import requests
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberPrep AI | CISSP Architect",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #262730; color: #ffffff; border: 1px solid #4B4B4B; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; }
    div[data-testid="stExpander"] { border: 1px solid #30363D; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ CRITICAL: API Key missing. Configure GEMINI_API_KEY in Secrets.")
    st.stop()

# --- BARE METAL API FUNCTION ---
def query_gemini_api(prompt_text):
    """
    Sends a direct HTTP REST request to Google, bypassing the SDK.
    This is the 'Platform Admin' way to ensure connectivity.
    """
    # We use the Stable 1.5 Flash endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check for HTTP 200 (Success)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # If 1.5 Flash fails (404), failover to Legacy Pro automatically
            if response.status_code == 404:
                return query_gemini_legacy(prompt_text)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        st.error(f"Connection Protocol Failure: {e}")
        return None

def query_gemini_legacy(prompt_text):
    """Failover to the legacy model endpoint"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        st.error(f"Legacy Failover Failed {response.status_code}: {response.text}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ COMMAND CENTER")
    selected_domain = st.selectbox(
        "Select Target Domain:",
        [
            "1. Security & Risk Management",
            "2. Asset Security",
            "3. Security Architecture & Engineering",
            "4. Communication & Network Security",
            "5. Identity & Access Management (IAM)",
            "6. Security Assessment & Testing",
            "7. Security Operations",
            "8. Software Development Security"
        ]
    )
    difficulty = st.select_slider("Simulation Difficulty", options=["Associate", "Professional", "Chief Architect"])
    st.divider()
    st.caption("Protocol: **REST / HTTP 1.1**")

# --- MAIN APP ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

if st.button("GENERATE NEW SCENARIO"):
    with st.spinner("Transmitting Payload to Neural Network..."):
        prompt = f"""
        Act as a CISSP exam creator. Create a {difficulty}-level scenario for: {selected_domain}.
        Format exactly as:
        **SCENARIO:** [Text]
        **QUESTION:** [Text]
        **OPTIONS:**
        A) [Text]
        B) [Text]
        C) [Text]
        D) [Text]
        ---
        **CORRECT ANSWER:** [Letter]
        **EXPLANATION:** [Text]
        """
        
        result = query_gemini_api(prompt)
        if result:
            st.session_state.current_question = result

# --- DISPLAY ---
if "current_question" in st.session_state and st.session_state.current_question:
    try:
        parts = st.session_state.current_question.split("---")
        st.markdown(parts[0])
        with st.expander("REVEAL OFFICIAL ANSWER"):
            st.markdown(parts[1] if len(parts) > 1 else "Check raw output.")
    except:
        st.markdown(st.session_state.current_question)
