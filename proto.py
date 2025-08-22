from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate, load_prompt
import json
import re

load_dotenv()   

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

# Simple page config
st.set_page_config(
    page_title="Anti-India Statement Detector",
    page_icon="🛡️",
    layout="centered"
)

# Header
st.title("🛡️ Anti-India Statement Detector")
st.subheader("Team: Threat Hunters | Hackathon Prototype")

# Description
st.info("""
**What this app does:**
- Analyzes statements for anti-India sentiment
- Provides a threat score (0-100)  
- Supports English and Hinglish text
- Gives contextual explanation
""")

# Input section
st.markdown("### 📝 Enter Statement for Analysis")
text = st.text_area(
    "Statement", 
    placeholder="Enter the statement you want to analyze...",
    height=100
)

# Load template
template = load_prompt("enhanced_template.json")

if st.button("🔍 Analyze Statement", type="primary"):
    if text.strip():
        with st.spinner('Analyzing statement...'):
            chain = template | llm
            result = chain.invoke({
                "statement_input": text
            })
            
            # Parse the JSON output from the model
            try:
                # Extract JSON from the result content
                content = result.content
                
                # Try to find JSON in the content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed_result = json.loads(json_str)
                    
                    # Display results
                    st.markdown("## 📊 Analysis Results")
                    
                    # Create columns for main metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        classification = parsed_result.get('is_anti_india_statement', 'Unknown')
                        if classification == 'No':
                            st.success(f"**Classification:** {classification}")
                        elif classification == 'Yes':
                            st.error(f"**Classification:** {classification}")
                        else:
                            st.warning(f"**Classification:** {classification}")
                    
                    with col2:
                        score = parsed_result.get('anti_india_score_percent', 0)
                        if score <= 20:
                            st.success(f"**Threat Score:** {score}/100")
                        elif score <= 50:
                            st.warning(f"**Threat Score:** {score}/100")
                        else:
                            st.error(f"**Threat Score:** {score}/100")
                    
                    # Score interpretation
                    if score <= 20:
                        st.success("🟢 **Low Risk** - Statement appears safe")
                    elif score <= 50:
                        st.warning("🟡 **Medium Risk** - Borderline content detected")
                    elif score <= 80:
                        st.error("🟠 **High Risk** - Concerning language found")
                    else:
                        st.error("🔴 **Critical Risk** - High threat level detected")
                    
                    # Context
                    context = parsed_result.get('context', 'No context provided')
                    st.markdown("### 📖 Context")
                    st.info(context)
                    
                else:
                    # If no JSON found, show raw content
                    st.markdown("### 🤖 AI Response")
                    st.write(content)
                    
            except json.JSONDecodeError as e:
                st.error("Failed to parse AI response as JSON")
                st.markdown("### Raw AI Response:")
                st.code(result.content, language="text")
                
            except Exception as e:
                st.error(f"Error processing result: {str(e)}")
                st.markdown("### Raw Response:")
                st.write(result.content)
    
    else:
        st.warning("⚠️ Please enter a statement to analyze!")

# Sidebar with simple info
with st.sidebar:
    st.header("🛡️ About")
    st.markdown("""
    **Team:** Threat Hunters
    
    **Purpose:** Detect anti-India statements using AI
    
    **Technology:**
    - LangChain + Groq
    - Pydantic validation  
    - Streamlit UI
    """)
    
    st.markdown("---")
    
    st.markdown("**Scoring Guide:**")
    st.markdown("""
    - 🟢 0-20: Safe
    - 🟡 21-50: Borderline  
    - 🟠 51-80: Concerning
    - 🔴 81-100: High Threat
    """)

# Footer
st.markdown("---")
st.caption("🚀 Hackathon Prototype | Threat Hunters Team")
