def get_info(document, patient_story):
    print("recieved")
    doc = document
    story = patient_story

from pydantic import BaseModel, Field

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