import streamlit as st
import requests
from bs4 import BeautifulSoup
from chains import Chain

# Initialize LangChain model
chain = Chain()

def extract_job_description(url):
    """Scrape and clean job description from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for failed requests
    except requests.RequestException as e:
        st.error(f"❌ Error fetching job page: {e}")
        return None

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Try to find common job description containers
    job_sections = soup.find_all(["div", "section", "article"], class_=lambda x: x and "job" in x.lower())
    
    if not job_sections:
        job_sections = soup.find_all("p")  # Fallback to paragraphs if no sections are found

    job_text = " ".join([section.get_text(strip=True) for section in job_sections])

    if len(job_text) < 100:  # Ensure enough job-related content
        st.warning("⚠️ Job description not found or too short.")
        return None

    return job_text

# 🏠 Streamlit App Interface
st.title("📧 Cold Mail Generator")

url = st.text_input("Enter a job posting URL:")
if st.button("Fetch Job Description"):
    if url:
        st.info("🔄 Fetching job description...")
        job_description = extract_job_description(url)

        if job_description:
            st.success("✅ Job description extracted!")
            st.text_area("📄 Extracted Job Description:", job_description[:1000], height=300)

            st.info("🔄 Extracting structured job details...")
            extracted_jobs = chain.extract_jobs(job_description)

            if extracted_jobs:
                st.success("✅ Job details extracted successfully!")
                st.json(extracted_jobs)
                
                # Generate a cold email
                st.info("✉️ Generating cold email...")
                email = chain.write_mail(extracted_jobs[0], links=["https://yourportfolio.com"])
                st.text_area("📧 Cold Email:", email, height=250)
            else:
                st.error("❌ No structured job details extracted. Check the job posting format.")
    else:
        st.warning("⚠️ Please enter a valid job URL.")
