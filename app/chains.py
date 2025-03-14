import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        """Initialize the Chain class with an LLM model."""
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        """Extract job details from a structured job description using LLM."""

        if not cleaned_text or len(cleaned_text) < 100:
            print("⚠️ No valid job description found or too short.")
            return []

        print(f"🔹 Extracting job details from:\n{cleaned_text[:500]}")  # Debugging

        prompt_extract = PromptTemplate(
            input_variables=["page_data"],  # Correct variable handling
            template="""
            ### JOB DESCRIPTION:
            {page_data}

            ### INSTRUCTIONS:
            Extract job details and return a **valid JSON array**:
            - **role** (str): Job title.
            - **experience** (int | null): Required years of experience.
            - **skills** (list[str]): Required skills (empty if not mentioned).
            - **description** (str): Concise job responsibilities.

            **Return ONLY JSON output. No extra text.**
            """
        )

        try:
            chain_extract = prompt_extract | self.llm
            res = chain_extract.invoke({"page_data": cleaned_text})

            print("🔹 Raw LLM Output:", res.content)  # Debugging

            json_parser = JsonOutputParser()
            extracted_jobs = json_parser.parse(res.content)

            return extracted_jobs if isinstance(extracted_jobs, list) else [extracted_jobs]

        except OutputParserException as e:
            print(f"❌ Error parsing job data: {e}")
            return []

        except Exception as e:
            print(f"⚠️ Unexpected error in job extraction: {e}")
            return []

    def write_mail(self, job, links):
        """Generate a cold email based on job details and portfolio links."""
        if not job:
            print("⚠️ No job data provided.")
            return "Error: No job data available."

        prompt_email = PromptTemplate(
            input_variables=["job_description", "link_list"],
            template="""
            ### JOB DETAILS:
            {job_description}

            ### INSTRUCTIONS:
            You are Muskan, a Business Development Executive at AtliQ. AtliQ is an AI & Software Consulting company that 
            helps businesses optimize processes through automation and AI-driven solutions.

            Your task is to draft a professional cold email introducing AtliQ’s expertise in fulfilling the job requirements mentioned above.
            Incorporate the most relevant portfolio links from: {link_list}

            **Format the email professionally with no unnecessary text.**
            """
        )

        try:
            chain_email = prompt_email | self.llm
            email_response = chain_email.invoke({"job_description": str(job), "link_list": links})
            return email_response.content

        except Exception as e:
            print(f"❌ Error generating email: {e}")
            return "Error: Unable to generate email."


if __name__ == "__main__":
    print(f"GROQ API Key Loaded: {bool(os.getenv('GROQ_API_KEY'))}")
