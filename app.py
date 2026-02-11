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
    .status-ok { color: #00FF00; font-size: 0.8rem; font-family: monospace; }
    .status-err { color: #FF4B4B; font-size: 0.8rem; font-family: monospace; }
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

# --- DYNAMIC SERVICE DISCOVERY ---
@st.cache_resource
def discover_active_model():
    """
    Finds the best available model, strictly avoiding restricted 'limit: 0' models.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text}"
        
        data = response.json()
        available_models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        
        # --- SAFE MODEL PRIORITY LIST ---
        # We REMOVED 'gemini-2.0-flash' because it causes Quota 429 errors.
        # We prioritize 1.5-flash because it is the "High Volume" free tier model.
        preferences = [
            "gemini-1.5-flash",          # BEST: Fast, Free, High Limits
            "gemini-1.5-flash-latest",   # Backup alias
            "gemini-1.5-flash-001",      # Specific version
            "gemini-1.5-pro",            # Slower, but powerful
            "gemini-1.0-pro",            # Legacy Stable
            "gemini-pro"                 # Oldest alias
        ]
        
        # 1. Check for preferred models in order
        for pref in preferences:
            for model in available_models:
                if pref in model:
                    # Found a safe match!
                    return model, "OK"
        
        # 2. Fallback: If no preferred model found, grab the first one that ISN'T 2.0
        for model in available_models:
            if "gemini" in model and "2.0" not in model:
                return model, "OK"
                
        return None, "NO_VALID_MODELS_FOUND"

    except Exception as e:
        return None, str(e)

# Run Discovery on App Startup
ACTIVE_MODEL, STATUS_MSG = discover_active_model()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ COMMAND CENTER")
    
    if ACTIVE_MODEL:
        # Clean up the model name for display (remove 'models/' prefix)
        display_name = ACTIVE_MODEL.replace("models/", "")
        st.markdown(f"**System Status:** <span class='status-ok'>ONLINE</span>", unsafe_allow_html=True)
        st.markdown(f"**Uplink:** `{display_name}`")
    else:
        st.markdown(f"**System Status:** <span class='status-err'>OFFLINE</span>", unsafe_allow_html=True)
        st.error(f"Discovery Failed: {STATUS_MSG}")
    
    st.divider()
    
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

# --- API FUNCTION ---
def query_gemini_direct(prompt_text):
    if not ACTIVE_MODEL:
        st.error("Cannot execute: No active model found.")
        return None

    # Use the discovered model name directly
    url = f"https://generativelanguage.googleapis.com/v1beta/{ACTIVE_MODEL}:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # If we hit a random 429 even on a safe model, tell the user to wait
            if response.status_code == 429:
                st.warning("⚠️ High Traffic: API Limit Reached. Please wait 10 seconds and try again.")
                return None
            else:
                st.error(f"Generation Error {response.status_code}: {response.text}")
                return None
    except Exception as e:
        st.error(f"Protocol Failure: {e}")
        return None

# --- MAIN APP ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

if st.button("GENERATE NEW SCENARIO"):
    if not ACTIVE_MODEL:
        st.error("Mission Aborted: System Offline")
    else:
        with st.spinner(f"Contacting Neural Network..."):
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
            
            result = query_gemini_direct(prompt)
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
