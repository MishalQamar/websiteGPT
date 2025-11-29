import streamlit as st
from utils import set_openai_api_key,create_chain_type,generate_response,load_pinecone_database

st.title("AI Customer Support")
st.caption("Ask questions about your website content")

def handle_chat(chain):
    if "messages" not in st.session_state:
        st.session_state.messages=[
            {
                "role":"assistant",
                "content":"How can I help you today?"
            }
        ]
    
    # Display all messages
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    # Handle chat input (outside the loop to avoid duplicate elements)
    if question := st.chat_input(key="chat_input", placeholder="Ask a question..."):
        # Add user message
        st.session_state.messages.append({
            "role":"user",
            "content":question
        })
        st.chat_message("user").write(question)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(chain,question)
                st.write(response["answer"])

            st.session_state.messages.append({
                "role":"assistant",
                "content":response["answer"]
            })

# Check if API key is set
if not st.session_state.get("openai_api_key"):
    st.warning("Please set your OpenAI API key in the Settings page")
    st.stop()

set_openai_api_key(st.session_state.openai_api_key)

try:
    pinecone_db= load_pinecone_database()
    chain = create_chain_type(pinecone_db)
    handle_chat(chain)
except Exception as e:
    st.warning("You don't have any knowledge base. Please create one in the Settings page first.")