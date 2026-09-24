import streamlit as st
import requests

MASTRA_URL = "https://archagent-1pjd.onrender.com"
st.set_page_config(
    page_title="ArchAgent",
    page_icon="🏗️",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "approval_pending" not in st.session_state:
    st.session_state["approval_pending"] = False

if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🏗️ ArchAgent")
st.subheader("Architecture Decision Assistant")

st.write(
    "Describe a software architecture problem. ArchAgent will research "
    "internal architecture knowledge and external information when needed, "
    "then evaluate options and recommend an architecture."
)

st.divider()


# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

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


# --------------------------------------------------
# ANALYZE ARCHITECTURE
# --------------------------------------------------

if analyze and question:

    # Clear any previous approval request
    st.session_state["approval_pending"] = False

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

            # Store recommendation so it survives Streamlit reruns
            if data.get("text"):
                st.session_state["recommendation"] = data["text"]

            # --------------------------------------------------
            # CHECK FOR HUMAN APPROVAL REQUEST
            # --------------------------------------------------

            suspend_payload = data.get("suspendPayload")

            if suspend_payload:

                st.session_state["approval_pending"] = True

                st.session_state["run_id"] = data.get("runId")

                st.session_state["tool_call_id"] = (
                    suspend_payload.get("toolCallId")
                )

                st.session_state["tool_name"] = (
                    suspend_payload.get("toolName")
                )

                args = suspend_payload.get("args", {})

                st.session_state["adr_title"] = args.get(
                    "title"
                )

                st.session_state["adr_content"] = args.get(
                    "content"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Unable to connect to ArchAgent. "
                "Unable to connect to the ArchAgent backend."
            )

        except requests.exceptions.Timeout:

            st.error(
                "ArchAgent took too long to respond. "
                "Please try again."
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


elif analyze:

    st.warning(
        "Please describe an architecture problem first."
    )


# --------------------------------------------------
# DISPLAY ARCHITECTURE RECOMMENDATION
# --------------------------------------------------

if st.session_state.get("recommendation"):

    st.divider()

    st.subheader("Architecture Recommendation")

    st.markdown(
        st.session_state["recommendation"]
    )


# --------------------------------------------------
# HUMAN-IN-THE-LOOP APPROVAL
#
# IMPORTANT:
# This is OUTSIDE the "if analyze" block.
# Therefore it survives Streamlit reruns.
# --------------------------------------------------

if st.session_state.get("approval_pending"):

    st.divider()

    st.warning(
        "⚠️ Human approval required before saving this ADR."
    )

    st.subheader("Proposed Architecture Decision Record")

    st.write(
        f"**Title:** "
        f"{st.session_state.get('adr_title', 'Architecture Decision')}"
    )

    st.markdown(
        st.session_state.get("adr_content", "")
    )

    col1, col2 = st.columns(2)

    with col1:

        approve_clicked = st.button(
            "✅ Approve ADR",
            type="primary",
            use_container_width=True,
            key="approve_adr"
        )

    with col2:

        decline_clicked = st.button(
            "❌ Decline",
            use_container_width=True,
            key="decline_adr"
        )


    # --------------------------------------------------
    # APPROVE
    # --------------------------------------------------

    if approve_clicked:

        with st.spinner(
            "Sending approval to ArchAgent..."
        ):

            try:

                approval_response = requests.post(
                    f"{MASTRA_URL}/api/agents/"
                    f"arch-agent/approve-tool-call-generate",
                    json={
                        "runId": st.session_state["run_id"],
                        "toolCallId": st.session_state[
                            "tool_call_id"
                        ]
                    },
                    timeout=120
                )

                # Debug information
                st.write(
                    "Approval HTTP status:",
                    approval_response.status_code
                )

                approval_response.raise_for_status()

                approval_data = approval_response.json()

                st.success(
                    "✅ ADR approved and saved successfully!"
                )

                # Show final agent response if available
                if approval_data.get("text"):

                    st.subheader(
                        "ArchAgent Response"
                    )

                    st.markdown(
                        approval_data["text"]
                    )

                # Clear approval state
                st.session_state["approval_pending"] = False


            except requests.exceptions.ConnectionError:

                st.error(
                    "Unable to connect to ArchAgent."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "Approval request timed out."
                )


            except requests.exceptions.HTTPError as e:

                st.error(
                    f"Mastra approval request failed: {e}"
                )

                st.write(
                    "Server response:"
                )

                st.code(
                    approval_response.text
                )


            except Exception as e:

                st.error(
                    f"Approval failed: {e}"
                )


    # --------------------------------------------------
    # DECLINE
    # --------------------------------------------------

    if decline_clicked:

        with st.spinner("Declining ADR..."):

            try:
                decline_response = requests.post(
                    f"{MASTRA_URL}/api/agents/"
                    f"arch-agent/decline-tool-call-generate",
                    json={
                        "runId": st.session_state["run_id"],
                        "toolCallId": st.session_state["tool_call_id"],
                        "reason": "User declined the proposed Architecture Decision Record."
                    },
                    timeout=120
                )

                decline_response.raise_for_status()

                decline_data = decline_response.json()

                st.warning(
                    "❌ ADR declined. The architecture decision was not saved."
                )

                # Show agent response after decline, if Mastra returned one
                if decline_data.get("text"):
                    st.markdown(decline_data["text"])

                # Clear pending approval
                st.session_state["approval_pending"] = False

            except requests.exceptions.ConnectionError:
                st.error(
                    "Unable to connect to ArchAgent."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "Decline request timed out."
                )

            except requests.exceptions.HTTPError as e:
                st.error(
                    f"Mastra decline request failed: {e}"
                )

                st.write("Server response:")
                st.code(decline_response.text)

            except Exception as e:
                st.error(
                    f"Decline failed: {e}"
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "ArchAgent can use internal architecture knowledge, "
    "web research, AI reasoning, and human-approved actions."
)