import streamlit as st
from google import genai
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
    .success-msg { color: #00FF00; font-size: 0.8rem; }
    .error-msg { color: #FF4B4B; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ SYSTEM ALERT: API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- ROBUST MODEL SELECTOR ---
# This list acts as a fallback chain. If the first fails, it tries the next.
MODEL_CHAIN = [
    "gemini-2.0-flash",        # Bleeding edge
    "gemini-1.5-flash",        # Standard Fast
    "gemini-1.5-flash-001",    # Specific Version
    "gemini-1.5-flash-002",    # Specific Version 2
    "gemini-1.5-pro",          # Standard Pro
    "gemini-1.0-pro",          # Legacy Stable
    "gemini-pro"               # Universal Alias
]

def generate_content_safe(prompt_text):
    """Iterates through models until one works."""
    last_error = None
    
    for model_name in MODEL_CHAIN:
        try:
            # Attempt to generate with current model
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt_text
            )
            # If successful, return the text and the working model name
            return response.text, model_name
            
        except Exception as e:
            # If 404 or 429, save error and continue to next model
            last_error = e
            continue
            
    # If we run out of models, throw the last error
    raise last_error

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
    st.caption("System Status: **ONLINE**")

# --- MAIN APP ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

if st.button("GENERATE NEW SCENARIO"):
    status_box = st.empty()
    
    with st.spinner("Initializing Neural Network... Hunting for active model uplink..."):
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
        
        try:
            # Call the smart generator
            result_text, working_model = generate_content_safe(prompt)
            
            # Save to session
            st.session_state.current_question = result_text
            st.session_state.last_model = working_model
            
        except Exception as e:
            st.error(f"CRITICAL FAILURE: All model uplinks failed. \nLast Error: {str(e)}")

# --- DISPLAY ---
if "current_question" in st.session_state and st.session_state.current_question:
    # Show which model actually worked (for your info)
    st.markdown(f"<p class='success-msg'> // CONNECTED VIA: {st.session_state.get('last_model', 'UNKNOWN')}</p>", unsafe_allow_html=True)
    
    try:
        parts = st.session_state.current_question.split("---")
        st.markdown(parts[0])
        with st.expander("REVEAL OFFICIAL ANSWER"):
            st.markdown(parts[1] if len(parts) > 1 else "Check raw output.")
    except:
        st.markdown(st.session_state.current_question)
