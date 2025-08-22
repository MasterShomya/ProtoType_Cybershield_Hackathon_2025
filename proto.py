from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate,load_prompt

load_dotenv()   

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation"
)
    
model = ChatHuggingFace(llm=llm)

st.header("ProtoType")

template = load_prompt("template_proto.json")

text = st.text_area("Enter the statement for analysis")

if st.button("Check Statement"):
    # result = model.invoke(prompt)
    chain = template | model
    result = chain.invoke({
        "statement_input": text
    })
    st.write(result.content)
