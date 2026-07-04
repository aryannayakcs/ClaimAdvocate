from pydantic import BaseModel, Field
import pypdf
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

class finding_structure(BaseModel):
    title: str = Field(description="A short 2-4 word title of the finding.")
    value: str = Field(description="The exact short value, number, policy ID, or specific requirement found (e.g., '6 weeks', 'Policy #A45', 'Medical Records'). Keep it concise.")

class extracted_data(BaseModel):
    patient_firstname: str = Field(description="The patien's first name. If not found return 'UNKNOWN'.")
    patient_lastname: str = Field(description="The patient's last name. If not found return 'UNKNOWN'.")
    patient_bday: str = Field(description="The patient's birthday formated as MM/DD/YYYY. If not found return 'UNKNOWN'.")

    cpt_codes: list[str] = Field(description="A list of all CPT codes found in the letter. If not found return an empty list.")
    claim_number: str = Field(description="The claim number/reference number/unique identifier for the denial. If not found return 'UNKNOWN'.")
    member_id: str = Field(description="The patient's insurance card number. If not found return 'UNKNOWN'.")
    date_of_denial: str = Field(description="The date the claim was denied formated as MM/DD/YYYY. If not found return 'UNKNOWN'.")
    filing_deadline: str = Field(description="The date the claim must be filed by formated as MM/DD/YYYY or a number of days from the date of denial that is added to the date of denial formated as MM/DD/YYYY. If not found return 'UNKNOWN'.")
    insurance_company: str = Field(description="The name of the insurance company. If not found return 'UNKNOWN'.")
    
    additional_findings: list[finding_structure] = Field(
        description="A list of any other highly important details found in the letter that would help a patient win an appeal. Examples include specific medical policies or guidelines cited, missing prerequisites like 'needs 6 weeks of physical therapy', or specific clinical reasons given for the denial. If nothing else if found return 'NONE'."
    )



# value_importance = {
#     "patient_firstname": "REQUIRED",
#     "patient_lastname": "REQUIRED",
#     "patient_bday": "REQUIRED",
#     "cpt_codes": "REQUIRED",
#     "claim_number": "REQUIRED",
#     "member_id": "REQUIRED",
#     "date_of_denial": "REQUIRED",
#     "filing_deadline": "REQUIRED",
#     "insurance_company": "REQUIRED",
#     "additional_findings": "OPTIONAL"
# }


def extract_text(doc) -> str:
    scanner = pypdf.PdfReader(doc)
    text =""
    for page in scanner.pages:
        text += page.extract_text() + "\n"
    return text





llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm = llm.with_structured_output(extracted_data)

def extraction_agent(doc, patient_story):
    text = extract_text(doc)
    if len(text.strip()) < 25:
        print(f"Error in extraction_agent: Document text seems too short. Review extracted text: {text}")
        return None

    prompt = f"""
You are an expert insurance claim analyst for medical denials. You are given a patient's denial letter and a short story in their own words about what happened. With these two pieces of information, you need to pull out specific facts.
    ~The denial letter: {text}
    ~The patient's story in their own words: {patient_story}
    ~NOTE: Do NOT guess or hallucinate values you are unsure about. If you cannot find a value, return 'UNKNOWN'.
"""
    try:
        result = structured_llm.invoke(prompt)
        return result
    except Exception as error:
        print ("Error in extraction_agent:", error)
        return None