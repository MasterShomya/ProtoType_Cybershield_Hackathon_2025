import streamlit as st
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import load_prompt
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Threat Hunters AI",
    page_icon="🛡️",
    layout="centered"
)

# --- LLM and LangChain Setup ---
load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation"
)
model = ChatHuggingFace(llm=llm)
template = load_prompt("template_proto.json")

# --- UI Rendering ---
st.title("🛡️ Threat Hunters")
st.subheader("Anti-India Statement Detection Prototype")
st.markdown("---")

st.info("This tool uses AI to analyze text for potential anti-India sentiment. Enter a statement below to receive a verdict, a sentiment score, and the context for the analysis.", icon="🤖")

# Use a form for better input management
with st.form(key='analysis_form'):
    text_input = st.text_area(
        "Enter the statement for analysis:",
        height=150,
        placeholder="Type or paste the text you want to analyze..."
    )
    submit_button = st.form_submit_button(
        label="Analyze Statement", 
        use_container_width=True
    )

# --- Backend Logic ---
def parse_llm_output(result_content):
    """
    Parses the raw text output from the LLM to extract Verdict, Score, and Context
    based on the detailed prompt template.
    """
    # Updated regex to match the keys from your prompt template
    verdict_match = re.search(r"Is_Anti_India_Statement: (Yes|No|Unrecognized)", result_content, re.IGNORECASE)
    score_match = re.search(r"Anti_India_Score_Percent: (\d+)", result_content)
    context_match = re.search(r"Context: (.*)", result_content, re.DOTALL)

    verdict = verdict_match.group(1).strip() if verdict_match else "N/A"
    score = int(score_match.group(1).strip()) if score_match else 0
    context = context_match.group(1).strip() if context_match else "No context provided."
    
    return {"verdict": verdict, "score": score, "context": context}

if submit_button and text_input:
    # Create the chain and invoke it
    chain = template | model
    result = chain.invoke({"statement_input": text_input})
    
    # Parse and display the result
    parsed_data = parse_llm_output(result.content)

    st.markdown("---")
    st.subheader("Analysis Results")
    
    # Display Verdict and Score side-by-side
    col1, col2 = st.columns(2)
    
    with col1:
        verdict_lower = parsed_data["verdict"].lower()
        if verdict_lower == "yes":
            st.error(f"**Verdict: Anti-India**")
        elif verdict_lower == "no":
            st.success(f"**Verdict: Not Anti-India**")
        else: # Handles "Unrecognized" or "N/A"
            st.warning(f"**Verdict: {parsed_data['verdict']}**")

    with col2:
        st.metric(
            label="Anti-India Score",
            value=f"{parsed_data['score']}/100"
        )
    
    # Display Context
    st.info("**Context & Reasoning:**")
    st.write(parsed_data["context"])

# --- Footer ---
st.markdown("---")
st.caption("Threat Hunters | Hackathon Prototype")
