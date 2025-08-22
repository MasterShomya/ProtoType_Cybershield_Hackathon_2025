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

# Using a more reliable model for structured output.
# This is a likely source of the formatting issue.
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation",
    max_new_tokens=250 # Increased tokens to ensure context is not cut off
)
model = ChatHuggingFace(llm=llm)
template = load_prompt("template_proto.json")

# --- UI Rendering ---
st.title("🛡️ Threat Hunters")
st.subheader("Anti-India Statement Detection Prototype")
st.markdown("---")

st.info("This tool uses AI to analyze text for potential anti-India sentiment. Enter a statement below to receive a verdict, a sentiment score, and the context for the analysis.", icon="�")

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
    Parses the raw text output from the LLM to extract Verdict, Score, and Context.
    This version uses more flexible regex to handle whitespace.
    """
    # More robust regex to handle potential whitespace variations
    verdict_match = re.search(r"Is_Anti_India_Statement:\s*(Yes|No|Unrecognized)", result_content, re.IGNORECASE)
    score_match = re.search(r"Anti_India_Score_Percent:\s*(\d+)", result_content)
    # The DOTALL flag allows '.' to match newline characters
    context_match = re.search(r"Context:\s*(.*)", result_content, re.IGNORECASE | re.DOTALL)

    if verdict_match and score_match and context_match:
        verdict = verdict_match.group(1).strip()
        score = int(score_match.group(1).strip())
        context = context_match.group(1).strip()
        return {"verdict": verdict, "score": score, "context": context}
    
    # Return None if any part of the expected format is not found
    return None

if submit_button and text_input:
    with st.spinner("AI is analyzing the statement... This may take a moment."):
        # Create the chain and invoke it
        chain = template | model
        result = chain.invoke({"statement_input": text_input})
        
        # Parse the result
        parsed_data = parse_llm_output(result.content)

        st.markdown("---")
        st.subheader("Analysis Results")

        if parsed_data:
            # Display Verdict and Score side-by-side
            col1, col2 = st.columns(2)
            
            with col1:
                verdict_lower = parsed_data["verdict"].lower()
                if verdict_lower == "yes":
                    st.error(f"**Verdict: Anti-India**")
                elif verdict_lower == "no":
                    st.success(f"**Verdict: Not Anti-India**")
                else: # Handles "Unrecognized"
                    st.warning(f"**Verdict: {parsed_data['verdict']}**")

            with col2:
                st.metric(
                    label="Anti-India Score",
                    value=f"{parsed_data['score']}/100"
                )
            
            # Display Context
            st.info("**Context & Reasoning:**")
            st.write(parsed_data["context"])
        else:
            # If parsing fails, show an error and the raw output for debugging
            st.error("The AI returned an unexpected format. The raw output is shown below.", icon="🚨")
            st.caption("This can happen if the AI model doesn't follow the instructions perfectly. Trying a different statement may help.")
            st.code(result.content, language="text")

# --- Footer ---
st.markdown("---")
st.caption("Threat Hunters | Hackathon Prototype")
