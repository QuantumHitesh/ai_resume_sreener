import streamlit as st
import io
import re
import json
import requests
import PyPDF2
from docx import Document

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="AI Resume Screener",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.

    Args:
        file (st.UploadedFile): The uploaded PDF file object.

    Returns:
        str: The extracted text from the PDF.
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""
    return text


# Function to extract text from a DOCX file
def extract_text_from_docx(file):
    """
    Extracts text from a DOCX file.

    Args:
        file (st.UploadedFile): The uploaded DOCX file object.

    Returns:
        str: The extracted text from the DOCX.
    """
    text = ""
    try:
        doc = Document(io.BytesIO(file.read()))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""
    return text


# Function to call the LLM API and get a structured response
def get_llm_response(prompt, api_key):
    """
    Sends a prompt to a Gemini LLM and returns a structured JSON response.

    Args:
        prompt (str): The prompt containing job description and resume text.
        api_key (str): The Google API key.

    Returns:
        dict: The parsed JSON response from the LLM.
    """
    try:
        if not api_key:
            st.error("API Key is missing. Please enter your API key in the sidebar.")
            return {"error": "API Key is missing."}

        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

        # Define the JSON schema for the desired structured output
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER",
                          "description": "A score from 0 to 100 on how well the resume matches the job description."},
                "reasoning": {"type": "STRING",
                              "description": "Detailed explanation of the score, highlighting strengths and weaknesses."},
                "missing_skills": {"type": "ARRAY", "items": {"type": "STRING"},
                                   "description": "A list of key skills mentioned in the job description that are not present in the resume."}
            },
            "propertyOrdering": ["score", "reasoning", "missing_skills"]
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema
            }
        }

        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes

        result = response.json()

        if result and result.get("candidates"):
            response_json_string = result["candidates"][0]["content"]["parts"][0]["text"]
            # The API returns a string that needs to be parsed as JSON
            return json.loads(response_json_string)
        else:
            return {"error": "Unexpected API response format."}

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {"error": f"API request failed: {e}"}
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response from LLM: {e}")
        st.write(f"Raw response: {response.text}")
        return {"error": f"Failed to parse JSON response: {e}"}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


# Main function to run the Streamlit app
def main():
    """
    The main function for the AI Resume Screener Streamlit app.
    """
    st.title("AI Resume Screener")
    st.markdown("### Match a resume to a job description using AI.")

    # Sidebar for API key input and instructions
    with st.sidebar:
        st.header("Instructions")
        st.markdown(
            """
            1.  Enter your Google API key below.
            2.  Paste the job description in the text area.
            3.  Upload a resume file (PDF or DOCX).
            4.  Click "Analyze Resume" to get the results.
            """
        )
        st.markdown("---")
        api_key = st.text_input(
            "Enter your Google API Key",
            type="password",
            help="Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
        )
        st.markdown("---")
        st.info(
            "The application uses an AI model to evaluate the resume. For best results, ensure the job description and resume are well-formatted.")

    # Main content area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Description")
        job_description = st.text_area(
            "Paste the job description here...",
            height=400,
            key="jd_text_area"
        )
        st.markdown("---")

    with col2:
        st.subheader("Resume Upload")
        uploaded_file = st.file_uploader(
            "Choose a PDF or DOCX file",
            type=["pdf", "docx"],
            key="resume_uploader"
        )
        st.markdown("---")

    # Button to trigger analysis
    if st.button("Analyze Resume", key="analyze_button"):
        if not api_key:
            st.warning("Please enter your Google API key in the sidebar.")
        elif not job_description:
            st.warning("Please paste a job description.")
        elif not uploaded_file:
            st.warning("Please upload a resume file.")
        else:
            with st.spinner("Analyzing... This may take a moment."):
                # Extract text from the uploaded file
                file_extension = uploaded_file.name.split(".")[-1].lower()
                resume_text = ""
                if file_extension == "pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif file_extension == "docx":
                    resume_text = extract_text_from_docx(uploaded_file)

                if not resume_text:
                    st.error("Could not extract text from the file. Please try a different file.")
                    return

                # Construct the prompt for the LLM
                prompt = f"""
                You are a highly skilled resume screening expert. Your task is to evaluate a candidate's resume against a specific job description.

                Job Description:
                ---
                {job_description}
                ---

                Candidate Resume:
                ---
                {resume_text}
                ---

                Based on the job description and the resume provided, perform the following tasks and provide your response in a JSON format.

                Tasks:
                1.  **Score the resume:** Give a numerical score from 0 to 100 representing how well the resume matches the job description.
                2.  **Provide detailed reasoning:** Explain the score. Highlight the key strengths in the resume that align with the job description and point out any significant weaknesses or mismatches.
                3.  **List missing skills:** Identify and list specific, important skills or requirements from the job description that are not clearly mentioned in the resume.

                The output MUST be a JSON object with the keys "score" (integer), "reasoning" (string), and "missing_skills" (array of strings). Do not include any other text or markdown outside of the JSON object.
                """

                # Call the LLM
                response_data = get_llm_response(prompt, api_key)

            # Display results
            if "error" not in response_data:
                st.subheader("Analysis Results")
                st.markdown(f"**Match Score:** {response_data['score']}/100")

                st.markdown("---")
                st.subheader("Reasoning")
                st.write(response_data["reasoning"])

                st.markdown("---")
                st.subheader("Missing Skills")
                if response_data["missing_skills"]:
                    for skill in response_data["missing_skills"]:
                        st.write(f"- {skill}")
                else:
                    st.write("No major skills from the job description were found to be missing.")
            else:
                st.error("Failed to get a response from the AI model. Please try again.")


if __name__ == "__main__":
    main()
