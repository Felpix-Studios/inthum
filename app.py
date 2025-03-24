import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=key)

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
    prompt = (
        f"The user was asked: \"{preset_question}\"\n"
        f"And responded: \"{user_response}\"\n\n"
        "You are an expert psycologist analyzing the user's response for their potential of intellectual humulity"
        "Please provide exactly 2 or 3 short follow-up questions (each on its own line) with no extra formatting, "
        "no numbering, no bullet points, and no styling. Then on a separate line, provide one final scale question "
        "from 1 to 5 about how strongly the user agrees with a relevant statement. "
        "Return only the plain question text."
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

    prompt = (
        "You are an expert psychologist. Your task is to interpret how the user's answers and responses reflect thier intellectual"
        "humility. Use the following definition of intellectual humility: Intellectual humility is the "
        "recognition that our knowledge and understanding are always limited and subject to growth or change." 
        "It involves acknowledging that we can be wrong, while staying open to learning from new information or perspectives."
        "Individuals who exhibit intellectual humility demonstrate curiosity, actively seeking out opposing viewpoints to refine their own thinking."
        "They also tend to be self-reflective about their cognitive biases and willing to correct mistakes in pursuit of truth."
        "In essence, intellectual humility emphasizes understanding over ego, valuing the collaborative search for accuracy above the need to be right."
        "Evaluate the following user responses to the questions and their follow-ups, "
        "and provide a final score on a scale from 1 (low intellectual humility) to 10 (high intellectual humility) along with a short explanation for the score.\n\n"
        "User responses:\n\n"
    )
    for idx, resp in enumerate(responses, start=1):
        prompt += f"Question {idx}:\n"
        prompt += f"Preset Answer: {resp.get('preset_answer', '')}\n"
        if 'followup_answers' in resp:
            for i, ans in enumerate(resp['followup_answers'], start=1):
                prompt += f"Follow-up {i} Answer: {ans}\n"
        prompt += "\n"
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
        
        **Flow**:
        1. You’ll first answer a preset question.
        2. The AI will generate a queue of follow-up questions (including the final scale question).
        3. You answer each follow-up one by one (each appears in its own message).
        4. Once all preset questions are complete, type **final** to receive your final assessment.
        """
    )
    
    # Initialize session state variables if they don't exist.
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0  # Index for preset questions
    if "phase" not in st.session_state:
        st.session_state.phase = "preset"  # can be "preset", "follow_up", or "final"
    if "responses" not in st.session_state:
        st.session_state.responses = []  # Store answers for each preset question
    if "current_response" not in st.session_state:
        st.session_state.current_response = {}  # Temporary storage for the current question
    if "follow_up_queue" not in st.session_state:
        st.session_state.follow_up_queue = []
    if "follow_up_index" not in st.session_state:
        st.session_state.follow_up_index = 0
    if "follow_up_answers" not in st.session_state:
        st.session_state.follow_up_answers = []

    # On initial load, send the first preset question if the chat is empty.
    if not st.session_state.chat_history and st.session_state.current_question_index < len(QUESTIONS):
        first_question = QUESTIONS[st.session_state.current_question_index]
        st.session_state.chat_history.append({"role": "assistant", "content": first_question})
    
    user_input = st.chat_input("Your message:")
    if user_input:
        # --- PHASE 1: PRESET ANSWER ---
        if st.session_state.phase == "preset":
            # User has answered the preset question.
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Store the user's preset answer.
            st.session_state.current_response["preset_answer"] = user_input
            st.session_state.current_response["question"] = QUESTIONS[st.session_state.current_question_index]
            
            # Append a temporary assistant message showing the spinner/loading text.
            spinner_index = len(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": "Generating follow-up questions..."})
            
            # Generate the follow-up text.
            follow_up_text = get_assistant_follow_up(
                QUESTIONS[st.session_state.current_question_index],
                user_input
            )
            
            # Split the follow-up content into individual lines.
            lines = [line.strip() for line in follow_up_text.split("\n") if line.strip()]
            st.session_state.follow_up_queue = lines
            st.session_state.follow_up_index = 0
            st.session_state.follow_up_answers = []
            
            # Replace the spinner message with the first follow-up question, if available.
            if lines:
                st.session_state.chat_history[spinner_index]["content"] = lines[0]
                st.session_state.follow_up_index = 1
            else:
                st.session_state.chat_history[spinner_index]["content"] = "No follow-up questions received."
            
            # Move to follow_up phase.
            st.session_state.phase = "follow_up"

        # --- PHASE 2: FOLLOW-UP ANSWERS ---
        elif st.session_state.phase == "follow_up":
            # User is answering a follow-up question.
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.follow_up_answers.append(user_input)
            
            # Check if there is another follow-up question.
            if st.session_state.follow_up_index < len(st.session_state.follow_up_queue):
                next_question = st.session_state.follow_up_queue[st.session_state.follow_up_index]
                st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                st.session_state.follow_up_index += 1
            else:
                # All follow-up questions for this preset have been answered.
                st.session_state.current_response["followup_answers"] = st.session_state.follow_up_answers
                st.session_state.responses.append(st.session_state.current_response)
                
                # Reset for the next preset question.
                st.session_state.current_response = {}
                st.session_state.follow_up_queue = []
                st.session_state.follow_up_index = 0
                st.session_state.follow_up_answers = []
                
                st.session_state.current_question_index += 1
                if st.session_state.current_question_index < len(QUESTIONS):
                    next_preset = QUESTIONS[st.session_state.current_question_index]
                    st.session_state.chat_history.append({"role": "assistant", "content": next_preset})
                    st.session_state.phase = "preset"
                else:
                    # All preset questions answered.
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "All preset questions have been answered! Type **final** to receive your final assessment."
                    })
                    st.session_state.phase = "final"

        # --- PHASE 3: FINAL ASSESSMENT ---
        elif st.session_state.phase == "final":
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            if user_input.strip().lower() == "final":
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
    
    # Finally, display the updated chat history.
    display_chat()

if __name__ == "__main__":
    main()