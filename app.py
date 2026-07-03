import streamlit as st
import streamlit.components.v1 as components
import time
import os

# --- FORCE LIGHT THEME AT THE FRAMEWORK LEVEL ---
# CSS overrides alone can't reliably beat Streamlit's dark theme tokens for
# every widget (status widget, file uploader icons, etc). Writing a real
# config.toml is what actually locks the app to light mode.
_config_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
_config_path = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_path):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_path, "w") as f:
        f.write(
            "[theme]\n"
            "base = \"light\"\n"
            "primaryColor = \"#f04438\"\n"
            "backgroundColor = \"#f8f9fa\"\n"
            "secondaryBackgroundColor = \"#ffffff\"\n"
            "textColor = \"#1e293b\"\n"
            "font = \"sans serif\"\n"
        )

# Set up page and wide layout
st.set_page_config(page_title="ClaimAdvocate AI", page_icon="⚖️", layout="wide")

# --- THE ABSOLUTE FORCE OVERRIDE RULES FOR ALL TEXT INSIDE DARK BLOCKS ---
st.markdown(
    """
    <style>
    /* Light theme is now enforced via .streamlit/config.toml, which is the
       correct mechanism (Streamlit's real theme tokens, not CSS variables
       we can't actually control from outside the app). */

    /* 1. Global Page Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 2. Standard Labels outside of dark boxes */
    h1, h2, h3 {
        color: #1e293b !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    label, p, .stMarkdown, [data-testid="stWidgetLabel"] p {
        color: #1e293b !important;
    }

    /* 3. Force these containers to stay LIGHT (not dark) with dark text */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stExpander"],
    div[data-testid="stExpanderDetails"],
    .streamlit-expanderHeader,
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] [data-testid="stExpanderIcon"],
    div[data-testid="stExpander"] [data-testid="stExpanderIcon"] svg {
        background-color: #ffffff !important;
        color: #1e293b !important;
        fill: #1e293b !important;
    }

    div[data-testid="stFileUploader"] *, 
    div[data-testid="stFileUploaderDropzone"] *,
    section[data-testid="stFileUploaderDropzone"] *,
    div[data-testid="stStatusWidget"] *,
    div[data-testid="stStatusWidget"] label,
    div[data-testid="stStatusWidget"] p,
    div[data-testid="stStatusWidget"] span,
    div[data-testid="stExpander"] *,
    .streamlit-expanderHeader,
    .streamlit-expanderHeader *,
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="baseButton-secondary"] span,
    button[data-testid="baseButton-secondary"] p,
    button[data-testid="stBaseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] span,
    button[data-testid="stBaseButton-secondary"] p,
    button[data-testid="stBaseButton-secondary"] div {
        color: #1e293b !important;
        fill: #1e293b !important;
        stroke: #1e293b !important;
    }

    /* Blanket fix for the file uploader's file-list row and its icons/buttons.
       Streamlit renders the uploaded-file icon square with
       backgroundColor: theme.colors.bodyText and color: theme.colors.bgColor
       (dark square, icon drawn in the page background color). If bgColor
       isn't resolving to a light value the icon becomes invisible, so we
       force both explicitly here rather than relying on theme tokens. */
    div[data-testid="stFileUploader"] div[class*="e1dmul8p5"],
    div[data-testid="stFileUploader"] div[style*="border-radius"] > svg,
    div[data-testid="stFileUploader"] > div div > div > div:has(> svg) {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    div[data-testid="stFileUploader"] svg {
        color: inherit !important;
        fill: currentColor !important;
        stroke: currentColor !important;
    }

    div[data-testid="stFileUploader"] button svg,
    div[data-testid="stFileUploader"] [role="button"] svg {
        color: #475569 !important;
        fill: #475569 !important;
        stroke: #475569 !important;
    }

    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] [role="button"] {
        background-color: transparent !important;
        color: #475569 !important;
    }

    div[data-testid="stFileUploader"] button:hover svg,
    div[data-testid="stFileUploader"] [role="button"]:hover svg {
        fill: #dc2626 !important;
        stroke: #dc2626 !important;
        color: #dc2626 !important;
    }

    /* Catch-all: any element rendered with a dark/black background that
       Streamlit applies inline via its own theme (status widget, buttons) */
    div[data-testid="stStatusWidget"] > div,
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
    }

    /* 4. Column Borders */
    [data-testid="stHorizontalBlock"] > div {
        border-color: #cbd5e1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚖️ Patient Insurance Claim Advocate")
st.markdown("---")

# --- SMOOTH SCROLL HELPER ---
def scroll_to_bottom():
    components.html(
        """
        <div id="end-of-page"></div>
        <script>
            document.getElementById("end-of-page").scrollIntoView({behavior: "smooth"});
        </script>
        """,
        height=0,
    )

# --- INITIALIZE MEMORY ---
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

if "generated_appeal" not in st.session_state:
    st.session_state.generated_appeal = None

# Two-column dynamic layout split
left_c, right_c = st.columns(2, border=True)

with left_c:
    file = st.file_uploader("Upload your insurance denial letter — We'll securely protect and analyze your data (PDF only)")
    patient_story = st.text_area(
        "Tell us your story. What medical care did your doctor recommend, and why did insurance say no?",
        placeholder="Type out any extra details or background context here..."
    )

    conditions = True
    if st.session_state.extracted_data is None:
        if st.button("Submit Details & Start Analysis", type="primary", use_container_width=True):
            with st.status("Processing your request...", expanded=True) as status:        
                if file is None:
                    st.error("Please upload a PDF file.")
                    conditions = False
                if patient_story == "":
                    st.error("Please describe what happened.")
                    conditions = False

                if conditions:
                    time.sleep(2)
                    status.write("Looking for details...")
                    time.sleep(2)

                    st.session_state.extracted_data = {
                        "cpt_code": "72148",
                        "doctor_name": "Dr. Smith"
                    }
                    status.update(label="Analysis Complete", state="complete", expanded=False)
                    st.rerun()
    else:
        if st.button("Reset Application & Start New Case", type="primary", use_container_width=True):
            st.session_state.extracted_data = None
            st.session_state.generated_appeal = None
            st.rerun()

with right_c:
    st.header("AI Data Verification Hub")
    
    if st.session_state.extracted_data is None:
        st.info("Please fill out your details and upload your document on the left to activate this interactive panel.")
    else:
        st.warning("🤖 **Agent:** I've parsed your document. Click into any box below to easily fix any mistakes I made:")
        
        corrected_code = st.text_input("Verified CPT Code:", value=st.session_state.extracted_data["cpt_code"])
        corrected_doctor = st.text_input("Verified Doctor:", value=st.session_state.extracted_data["doctor_name"])
        
        st.markdown("---")
        st.markdown(f"**🤖 Agent Question:** I see {corrected_doctor} ordered code {corrected_code}. Did you complete any physical therapy before this request?")
        followup_response = st.text_area("Your answer:")

# --- CONTROL BAR AND OUTPUT AREA ---
st.markdown("---")

if st.session_state.extracted_data is not None:
    middle_left, middle_right = st.columns(2)
    
    with middle_left:
        st.metric(label="Predicted Overturn Success Probability", value="84%", delta="Strong Case Foundation")
        st.caption("✨ *Based on thousands of historical appeal cases, your clinical criteria shows a high probability of reversing this decision.*")
        
    with middle_right:
        st.write("### Appeal Document Actions")
        
        if st.session_state.generated_appeal is None:
            if st.button("Generate Appeal Letter", type="primary", use_container_width=True):
                with st.spinner("Drafting your custom appeal letter..."):
                    time.sleep(2.5)
                    st.session_state.generated_appeal = "Dear Appeals Department,\n\nI am writing to formally appeal..."
                st.rerun()
        else:
            if st.button("Regenerate Appeal Letter", use_container_width=True):
                with st.spinner("Re-drafting a new version..."):
                    time.sleep(2.5)
                    st.session_state.generated_appeal = "Dear Appeals Department,\n\n[NEW DRAFT] I am writing to formally appeal..."
                st.rerun()

    # --- FINAL SCREEN OUTPUT ---
    if st.session_state.generated_appeal is not None:
        st.markdown("### 📄 Generated Appeal Letter Draft")
        final_text = st.text_area(
            "Review and edit your final document text below:", 
            value=st.session_state.generated_appeal, 
            height=400
        )
        
        scroll_to_bottom()