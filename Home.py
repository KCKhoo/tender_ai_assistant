import streamlit as st

from app_core.resources import setup_rag_pipeline

st.set_page_config(page_title="AI Tender Assistant", page_icon="💬")

rag_pipeline = setup_rag_pipeline()

st.title("Tender AI Assistant")
st.caption("Hi! Ask me anything about the tender documents.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_ques := st.chat_input("Enter your question"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_ques})

    with st.chat_message("user"):
        st.markdown(user_ques)

    # Answer user query
    if rag_pipeline:
        spinner = st.empty()

        with st.chat_message("assistant"):
            output = rag_pipeline.answer(
                user_ques,
                20,
                retriever_filter=None,
                top_k_rerank=10,
                callback=lambda msg: spinner.markdown(f"⏳ *{msg}*"),
            )

            if output.get("status") == "error":
                error_msg = output["error_message"]
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Error: {error_msg}"}
                )

            else:
                answer = output["answer"]
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

        spinner.empty()

    else:
        st.error("Oops, there is an error")
