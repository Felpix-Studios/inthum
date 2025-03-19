import os
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -- Preset Questions --
QUESTIONS = [
    "Can you describe a time you realized you were wrong about something important? How did you come to that realization, and what did you do afterward?",
    "What’s a topic you used to feel very certain about, but now feel less certain—or even uncertain—about? What made you reconsider?",
    "When you’re in a debate and you encounter evidence that contradicts your view, how do you usually respond?",
    "In areas you’re most knowledgeable about, do you ever worry that you might still have blind spots? How do you watch out for them?",
    "How do you decide which sources of information you trust and which you don’t?"
]

# -- Helper Functions --

def get_assistant_follow_up(preset_question, user_response):
    """
    Given the preset question and the user's answer,
    request ChatGPT to generate 2-3 probing follow-up questions
    plus an importance scale question (from 1 to 5).
    """
    prompt = (
        f"The user was asked: \"{preset_question}\"\n"
        f"And responded: \"{user_response}\"\n\n"
        "Please provide 2-3 follow-up or probing questions to learn more about the user's thoughts. "
        "Then ask an importance scale question (from 1 to 5) regarding how much the user agrees with a relevant statement. "
        "Format your response with the follow-up questions first (each on its own line) and then the scale question."
    )
    messages = [
        {"role": "system", "content": "You are a curious and thoughtful assistant."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9
    )
    return response.choices[0].message.content

def get_final_score(responses):
    """
    After all questions have been answered, this function sends all
    the user responses to ChatGPT to calculate a final score along
    with a brief explanation.
    """
    prompt = (
        "You are an expert psychologist. Evaluate the following user responses to the questions and their follow-ups, "
        "and provide a final score on a scale from 1 (low) to 10 (high) along with a brief explanation for the score. "
        "User responses:\n\n"
    )
    for idx, resp in enumerate(responses, start=1):
        prompt += f"Question {idx}:\n"
        prompt += f"Preset Answer: {resp.get('preset_answer', '')}\n"
        prompt += f"Follow-up Answer: {resp.get('followup_answer', '')}\n\n"
    messages = [
        {"role": "system", "content": "You are an expert psychologist."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9
    )
    return response.choices[0].message.content

def display_chat():
    """
    Displays the chat history using st.chat_message.
    """
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.chat_message("user").write(msg["content"])

# -- Streamlit App --

def main():
    st.title("AI Chat & Assessment App")
    st.write(
        """
        This app will ask you a series of introspective questions via a chat interface.
        
        1. You’ll first answer a preset question.
        2. The AI will then generate follow-up/probing questions plus an importance scale question.
        3. You answer these follow-ups.
        
        Once all questions are complete, type **final** to receive your final assessment.
        """
    )
    
    # Initialize session state variables if they don't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0  # Index for preset questions
    if "phase" not in st.session_state:
        st.session_state.phase = "preset"  # "preset", "follow_up", or "final"
    if "responses" not in st.session_state:
        st.session_state.responses = []  # Store answers for each preset question
    if "current_response" not in st.session_state:
        st.session_state.current_response = {}  # Temp storage for current question

    # On initial load, send the first preset question if the chat is empty.
    if not st.session_state.chat_history and st.session_state.current_question_index < len(QUESTIONS):
        first_question = QUESTIONS[st.session_state.current_question_index]
        st.session_state.chat_history.append({"role": "assistant", "content": first_question})
    
    # Display the full chat history.
    display_chat()

    # Get user input from the chat input box.
    user_input = st.chat_input("Your message:")
    if user_input:
        # Depending on the current phase, process the input.
        if st.session_state.phase == "preset":
            # Save the user's answer to the preset question.
            st.session_state.current_response["preset_answer"] = user_input
            st.session_state.current_response["question"] = QUESTIONS[st.session_state.current_question_index]
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Generate follow-up questions.
            with st.spinner("Generating follow-up questions..."):
                follow_up = get_assistant_follow_up(QUESTIONS[st.session_state.current_question_index], user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": follow_up})
            st.session_state.phase = "follow_up"

        elif st.session_state.phase == "follow_up":
            # Save the user's answer to the follow-up questions.
            st.session_state.current_response["followup_answer"] = user_input
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            # Store the complete responses.
            st.session_state.responses.append(st.session_state.current_response)
            st.session_state.current_response = {}
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index < len(QUESTIONS):
                # Send the next preset question.
                next_question = QUESTIONS[st.session_state.current_question_index]
                st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                st.session_state.phase = "preset"
            else:
                # All questions answered; prompt user to type "final".
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "All preset questions have been answered! Type **final** to receive your final assessment."
                })
                st.session_state.phase = "final"

        elif st.session_state.phase == "final":
            # Trigger final assessment if the user types "final".
            if user_input.strip().lower() == "final":
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Calculating your assessment..."):
                    final_assessment = get_final_score(st.session_state.responses)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "## Final Assessment\n" + final_assessment
                })
            else:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "Please type **final** to receive your final assessment."
                })
        st.experimental_rerun()

if __name__ == "__main__":
    main()