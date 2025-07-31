import streamlit as st
from openai import OpenAI
import tempfile
from utils import extract_text
import os

# Intialize OpenAI client with Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit app UI
st.set_page_config(page_title="AI Document Summarizer", page_icon="📄")
st.title("📄 AI-Powered Document Summarizer")
st.warning("🔒 Internal Use Only - Do not share externally.")
st.info("Upload a business or legal document (PDF/DOCX). For large files, this tool auto-chunks and returns a one-page executive summary.")


# File uploader
uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

# Chunking helper
def chunk_text(text, max_chars=7000):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Summarize a single section
def summarize_section(text_chunk):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are summarizing a section of a business or legal document."},
            {"role": "user", "content": f"Summarize this section clearly and concisely:\n\n{text_chunk}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Summarize the entire document from section summaries
def summarize_all(sections):
    combined = "\n\n".join(sections)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are an expert business analyst. Based on the following section summaries, produce a clear, one-page executive summary of the document."},
            {"role": "user", "content": combined}
        ]
    )
    return response.choices[0].message.content.strip()

# Main logic
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getbuffer())
        temp_file_path = tmp.name

    try:
        with st.spinner("🔍 Extracting text from document..."):
            raw_text = extract_text(temp_file_path)

        with st.spinner("📚 Chunking and summarizing sections..."):
            chunks = chunk_text(raw_text)
            section_summaries = []
            for i, chunk in enumerate(chunks):
                with st.spinner(f"🤖 Summarizing section {i + 1} of {len(chunks)}..."):
                    summary = summarize_section(chunk)
                    section_summaries.append(summary)

        with st.spinner("🧠 Generating one-page summary..."):
            final_summary = summarize_all(section_summaries)

        st.success("✅ Summary complete!")
        
        st.markdown("### 📋 One-Page Executive Summary")
        with st.expander("🔎 Click to view summary", expanded=True):
            st.markdown(final_summary, unsafe_allow_html=True)

        st.download_button("📥 Download Summary", final_summary, file_name="summary.md")

    except Exception as e:
        st.error("❌ Something went wrong.")
        st.exception(e)
