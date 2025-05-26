import streamlit as st

from tos.rag import RAG

st.set_page_config(page_title="TOS", page_icon="🪐", layout="centered")

rag = RAG()

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input and response logic FIRST
query = st.chat_input("Ask a question...")
if query:
    with st.spinner("🔍 Searching for relevant information..."):
        response = rag.retrieve_with_sources(query)
        st.session_state.chat_history.append(
            {
                "query": query,
                "answer": response["answer"],
                "sources": response["sources"],
            }
        )

# THEN render the sidebar (after history is updated)
with st.sidebar:
    st.title("🪐 TOS")
    st.markdown("I am currently trained in APR user help docs — ask me anything!")

    st.header("💬 Chat History")
    if st.session_state.chat_history:
        for i, item in enumerate(st.session_state.chat_history):
            st.markdown(f"**{i + 1}.** {item['query']}")
    else:
        st.markdown("_No chats yet._")

    if st.button("🧹 Clear chat"):
        st.session_state.chat_history.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small>⚠️ This assistant uses AI-generated content and may make mistakes. "
        "Please verify responses before relying on them.<br><br>"
        "Built with ❤️ by <b>Anil Kulkarni</b> for Soltek.</small>",
        unsafe_allow_html=True,
    )

# Chat UI display
for item in st.session_state.chat_history:
    st.chat_message("user").write(item["query"])
    st.chat_message("assistant").write(item["answer"])

    if item["sources"]:
        with st.expander("🔗 Sources"):
            for src in item["sources"]:
                st.code(src["source"])
                st.code(src["source"])
