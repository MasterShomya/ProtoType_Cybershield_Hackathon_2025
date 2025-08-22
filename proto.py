import streamlit as st
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import json
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
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation",
    max_new_tokens=250
)
model = ChatHuggingFace(llm=llm)

# --- New In-line Prompt Template ---
# This prompt asks for a JSON output, which is more reliable to parse.
prompt_template_str = """
Analyze the following statement to determine if it is 'Anti-India'.

**Criteria:**
- An "Anti-India Statement" incites hatred/violence, calls for disintegration, denies sovereignty, or spreads malicious misinformation to harm national security.
- Criticism of government policy, reporting on negative events, or expressing dissent is NOT considered anti-India.

**Statement:** "{statement_input}"

Based on your analysis, provide a JSON object with the following keys and nothing else:
- "verdict": A string which can be "Yes", "No", or "Unrecognized".
- "score": An integer score from 0 to 100.
- "context": A brief, neutral explanation for your verdict and score.

JSON Output:
"""

template = PromptTemplate(
    input_variables=["statement_input"],
    template=prompt_template_str,
)


# --- UI Rendering ---
st.title("🛡️ Threat Hunters")
st.subheader("Anti-India Statement Detection Prototype")
st.markdown("---")

st.info("This tool uses AI to analyze text for potential anti-India sentiment. Enter a statement below to receive a verdict, a sentiment score, and the context for the analysis.")

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
    Parses the JSON output from the LLM.
    """
    try:
        # The model might sometimes add extra text before the JSON.
        # This regex finds the JSON block.
        json_match = re.search(r'\{.*\}', result_content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        return None
    except (json.JSONDecodeError, AttributeError):
        return None

if submit_button and text_input:
    with st.spinner("AI is analyzing the statement... This may take a moment."):
        chain = template | model
        result = chain.invoke({"statement_input": text_input})
        
        parsed_data = parse_llm_output(result.content)

        st.markdown("---")
        st.subheader("Analysis Results")

        if parsed_data and all(k in parsed_data for k in ["verdict", "score", "context"]):
            col1, col2 = st.columns(2)
            
            with col1:
                verdict_lower = parsed_data["verdict"].lower()
                if verdict_lower == "yes":
                    st.error(f"**Verdict: Anti-India**")
                elif verdict_lower == "no":
                    st.success(f"**Verdict: Not Anti-India**")
                else:
                    st.warning(f"**Verdict: {parsed_data['verdict']}**")

            with col2:
                st.metric(
                    label="Anti-India Score",
                    value=f"{parsed_data['score']}/100"
                )
            
            st.info("**Context & Reasoning:**")
            st.write(parsed_data["context"])
        else:
            st.error("The AI returned an unexpected format. The raw output is shown below.", icon="�")
            st.caption("This can happen if the AI model doesn't follow the instructions perfectly. Trying a different statement may help.")
            st.code(result.content, language="text")

# --- Footer ---
st.markdown("---")
st.caption("Threat Hunters | Hackathon Prototype")

