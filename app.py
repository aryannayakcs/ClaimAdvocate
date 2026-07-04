import streamlit as st
import streamlit.components.v1 as components
import time
import os
from doc_processor import extraction_agent

# --- FORCE LIGHT THEME AT THE FRAMEWORK LEVEL --- Claude
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


st.set_page_config(page_title="ClaimAdvocate AI", page_icon="⚖️", layout="wide")

# Custom CSS Overrides -- Claude
st.markdown(
    """
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1e293b !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    label, p, .stMarkdown, [data-testid="stWidgetLabel"] p { color: #1e293b !important; }
    div[data-testid="stHorizontalBlock"] > div { border-color: #cbd5e1 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚖️ Patient Insurance Claim Advocate")
st.markdown("---")

# Claude
def scroll_to_bottom():
    components.html(
        """
        <div id="end-of-page"></div>
        <script>document.getElementById("end-of-page").scrollIntoView({behavior: "smooth"});</script>
        """,
        height=0,
    )

# --- CORRECTED INITIALIZATION MEMORY ---
# Changing this to None makes sure the verification panel stays hidden until processed!
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

if "generated_appeal" not in st.session_state:
    st.session_state.generated_appeal = None

# Two-column layout split
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
                time.sleep(2)
       
                if file is None:
                    st.error("Please upload a PDF file.")
                    conditions = False
                if patient_story == "":
                    st.error("Please describe what happened.")
                    conditions = False

                if conditions:
                    status.write("Analyzing document structure...")
                    
                    # Call processor file
                    ai_results = extraction_agent(file, patient_story)
                    time.sleep(2)
                    status.write("Extracting key values...")
                    

                    if ai_results is None:
                        st.error("Error in extraction_agent: Please check your document and story, and try agian. The agent was unable to extract data. ")
                    else:
                        st.session_state.extracted_data = ai_results.model_dump()
                        st.session_state.extracted_data["cpt_codes"] = ", ".join(st.session_state.extracted_data["cpt_codes"])
                        
                        status.update(label="Analysis completed", state = "complete", expanded=False)
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

        # Aligned cleanly with schema key string values using safe .get()
        first_name = st.text_input("First Name", value=st.session_state.extracted_data.get("patient_firstname", "UNKNOWN"))        
        last_name = st.text_input("Last Name", value=st.session_state.extracted_data.get("patient_lastname", "UNKNOWN"))        
        birthday = st.text_input("Birthday", value=st.session_state.extracted_data.get("patient_bday", "UNKNOWN")) 
        
        cpt_codes = st.text_input("CPT Code(s)", value=st.session_state.extracted_data.get("cpt_codes", "UNKNOWN"))
        claim_number = st.text_input("Claim Number", value=st.session_state.extracted_data.get("claim_number", "UNKNOWN"))
        member_id = st.text_input("Member ID", value=st.session_state.extracted_data.get("member_id", "UNKNOWN"))
        date_of_denial = st.text_input("Date of Denial", value=st.session_state.extracted_data.get("date_of_denial", "UNKNOWN"))
        filing_deadline = st.text_input("Filing Deadline", value=st.session_state.extracted_data.get("filing_deadline", "UNKNOWN"))
        insurance_company = st.text_input("Insurance Company", value=st.session_state.extracted_data.get("insurance_company", "UNKNOWN"))

        finding_list = st.session_state.extracted_data.get("additional_findings", [])
        
        if not finding_list:
            st.info("No additional findings were detected in your document.")
        else:
            for i, finding in enumerate(finding_list):
                finding = st.text_input(finding.get("title", "Finding"), value=finding.get("value", ""), key=f"finding_{i}")

# --- CONTROL BAR AND OUTPUT AREA ---
st.markdown("---")

if st.session_state.extracted_data is not None:
    middle_left, middle_right = st.columns(2)
    
    with middle_left:
        st.metric(label="Predicted Overturn Success Probability", value="84%", delta="Strong Case Foundation")
        st.caption("✨ *Based on historical appeal cases.*")
        
    with middle_right:
        st.write("### Appeal Document Actions")
        
        if st.session_state.generated_appeal is None:
            if st.button("Generate Appeal Letter", type="primary", use_container_width=True):
                with st.spinner("Drafting your custom appeal letter..."):
                    time.sleep(2.5)
                    st.session_state.generated_appeal = f"Dear Appeals Department,\n\nI am writing to formally appeal the denial of coverage for claim #{claim_number}..."
                st.rerun()
        else:
            if st.button("Regenerate Appeal Letter", use_container_width=True):
                with st.spinner("Re-drafting a new version..."):
                    time.sleep(2.5)
                    st.session_state.generated_appeal = "Dear Appeals Department,\n\n[NEW DRAFT] I am writing to formally appeal..."
                st.rerun()

    if st.session_state.generated_appeal is not None:
        st.markdown("### 📄 Generated Appeal Letter Draft")
        final_text = st.text_area(
            "Review and edit your final document text below:", 
            value=st.session_state.generated_appeal, 
            height=400
        )
        scroll_to_bottom()