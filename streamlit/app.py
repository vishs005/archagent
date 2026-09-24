import streamlit as st
import requests

MASTRA_URL = "http://localhost:4111"

st.set_page_config(
    page_title="ArchAgent",
    page_icon="🏗️",
    layout="wide"
)

# Header
st.title("🏗️ ArchAgent")
st.subheader("Architecture Decision Assistant")

st.write(
    "Describe a software architecture problem. ArchAgent will research "
    "internal architecture knowledge and external information when needed, "
    "then evaluate options and recommend an architecture."
)

st.divider()

# Input
question = st.text_area(
    "What architecture problem are you trying to solve?",
    height=150,
    placeholder=(
        "Example: We are considering Apache Kafka versus AWS EventBridge "
        "for an event-driven order processing platform. Compare them using "
        "our internal architecture guidance and current external information."
    ),
)

analyze = st.button(
    "Analyze Architecture",
    type="primary",
    use_container_width=True
)

# Agent call
if analyze and question:

    with st.spinner("ArchAgent is researching and analyzing..."):

        try:
            response = requests.post(
                f"{MASTRA_URL}/api/agents/arch-agent/generate",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                },
                timeout=120
            )

            response.raise_for_status()
            data = response.json()

            st.divider()

            st.subheader("Architecture Recommendation")

            st.markdown(data["text"])

            st.divider()

            st.caption(
                "ArchAgent can use internal architecture knowledge, "
                "web research, AI reasoning, and human-approved actions."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Unable to connect to ArchAgent. "
                "Make sure the Mastra server is running on port 4111."
            )

        except requests.exceptions.Timeout:
            st.error(
                "ArchAgent took too long to respond. Please try again."
            )

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif analyze:
    st.warning("Please describe an architecture problem first.")