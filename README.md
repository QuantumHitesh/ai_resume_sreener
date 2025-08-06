**Introduction**
Welcome to the AI Resume Screener project! This is an intelligent, automated tool designed to streamline the hiring process by efficiently analyzing and scoring resumes against a given job description. 
Leveraging the power of Large Language Models (LLMs), this application provides recruiters and hiring managers with a quick and objective way to identify the best-fit candidates, moving beyond simple keyword matching to a deeper, more nuanced understanding of a candidate's qualifications.

**Problem Solved**: Manual resume screening is a time-consuming and often biased process. 
This tool aims to automate the initial screening phase, allowing recruiters to focus on qualified candidates and reducing the time-to-hire.

**Features** : -
**Intelligent Resume Parsing:**  Extracts key information like skills, experience, education, and contact details from various formats (e.g., PDF, DOCX).
**AI-Powered Matching:** Compares a candidate's resume against a job description to generate a detailed matching score and suitability remarks.
**Unique API Key Management:**  Provides a secure and unique API key for each user, ensuring data privacy and controlled access.
**Scalable and Robust:**  Built with a clean, modular architecture that can handle a high volume of resume submissions.
**Detailed Insights:**  Offers a breakdown of the analysis, including strengths, weaknesses, and personalized suggestions.

**How It Works : -**
**The core of this project is a robust pipeline that uses a combination of natural language processing (NLP) and a powerful LLM.**
**Resume Upload:**  The user uploads one or more resumes and a job description.
**Text Extraction:**  The system parses the resumes and extracts the raw text.
**LLM Analysis:**  The extracted text and the job description are fed into a large language model (e.g., OpenAI GPT, Gemini API). The model is prompted to perform a detailed comparison.
**Scoring & Feedback:**  The model generates a matching score (e.g., 1-100%) and provides a summary of its findings, highlighting the candidate's suitability.
**Secure API Handling:**  All requests are authenticated with a unique, user-specific API key, which is used to manage and track usage.
