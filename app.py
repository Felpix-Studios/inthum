import os
import time
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -- Preset Questions --
QUESTIONS = [
    #"Can you describe a time you realized you were wrong about something important? How did you come to that realization, and what did you do afterward?",
    #"What’s a topic you used to feel very certain about, but now feel less certain—or even uncertain—about? What made you reconsider?",
    #"When you’re in a debate and you encounter evidence that contradicts your view, how do you usually respond?",
    #"In areas you’re most knowledgeable about, do you ever worry that you might still have blind spots? How do you watch out for them?",
    #"How do you decide which sources of information you trust and which you don’t?"
    "What are your primary sources of information when you are trying to learn about new issue or event?",
    "How do you decide which perspectives are worth engaging with or considering on social media?"
    "How do you typically react when someone challenges your beliefs or opinions on social media?"
]

# -- Helper Functions --

# Function to generate follow-up questions based on user response to a preset question.
def get_assistant_follow_up(preset_question, user_response, chat_history):
    prompt = (
        f"Previous conversation: \"{chat_history}\"\n"
        f"The user was asked: \"{preset_question}\"\n"
        f"And responded: \"{user_response}\"\n\n"
        "You are an expert psycologist analyzing the user's response for their potential of intellectual humulity"
        "Please provide exactly 1 short, and only 1 follow-up questions (each on its own line) with no extra formatting, "
        "no numbering, no bullet points, and no styling. Then on a separate line, provide one final scale question "
        "from 1 to 5 about how strongly the user agrees with a relevant statement. "
        "Your questions should be open-ended and designed to elicit more information about the user's thought process without any bias or leading language."
        "You should also not try to have 2 follow-up questions or combine several questions into one. Only send one follow-up question."
        "Do not be repetitive or ask the same question in a different way, and ensure that the questions are relevant to the user's responses."
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


# Function to generate the final assessment, prompt based on Volfovsky's repo
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
        "and provide a final score on a scale from 1 (low intellectual humility) to 10 (high intellectual humility) along with a short explanation for the score. If a user makes no attempt to answer the question, you may assign them a score of 1 with a short explanation.\n\n"
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
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.chat_message("user").write(msg["content"])

  
# Main Streamlit Application
def main():
    logo_path = "plab_logo.png"
    st.logo(logo_path, size = "large")
    st.title("Intellectual Humility Chat Assessment")
    st.image(logo_path, width = 520)
    st.write(
        """
        Do you have an intellectually humble mindset?  Use this tool to find out.


      
        This app will ask you a series of introspective questions via a chat interface.
        
        **Flow**:
        1. You’ll first answer a preset question.
        2. The AI will generate a queue of follow-up questions (including the final scale question).
        3. You answer each follow-up one by one.
        4. Once all preset questions are complete, the final assessment is automatically generated after a 1 second pause.

        This app is currently experimental and uses generative AI! Please provide feedback and report any issues.
        """
    )
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "phase" not in st.session_state:
        st.session_state.phase = "preset"
    if "responses" not in st.session_state:
        st.session_state.responses = []
    if "current_response" not in st.session_state:
        st.session_state.current_response = {}
    if "follow_up_queue" not in st.session_state:
        st.session_state.follow_up_queue = []
    if "follow_up_index" not in st.session_state:
        st.session_state.follow_up_index = 0
    if "follow_up_answers" not in st.session_state:
        st.session_state.follow_up_answers = []
    if "final_generated" not in st.session_state:
        st.session_state.final_generated = False

    if not st.session_state.chat_history and st.session_state.current_question_index < len(QUESTIONS):
        first_question = QUESTIONS[st.session_state.current_question_index]
        st.session_state.chat_history.append({"role": "assistant", "content": first_question})
    
    user_input = st.chat_input("Your message:")
    if user_input:
        if st.session_state.phase == "preset":
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.current_response["preset_answer"] = user_input
            st.session_state.current_response["question"] = QUESTIONS[st.session_state.current_question_index]
            
            # Insert a temporary spinner message in-line.
            spinner_index = len(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": "Generating follow-up questions..."})
            
            follow_up_text = get_assistant_follow_up(
                QUESTIONS[st.session_state.current_question_index],
                user_input,
                st.session_state.chat_history
            )
            lines = [line.strip() for line in follow_up_text.split("\n") if line.strip()]
            st.session_state.follow_up_queue = lines
            st.session_state.follow_up_index = 0
            st.session_state.follow_up_answers = []
            
            if lines:
                st.session_state.chat_history[spinner_index]["content"] = lines[0]
                st.session_state.follow_up_index = 1
            else:
                st.session_state.chat_history[spinner_index]["content"] = "No follow-up questions received."
            
            st.session_state.phase = "follow_up"
        
        elif st.session_state.phase == "follow_up":
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.follow_up_answers.append(user_input)
            if st.session_state.follow_up_index < len(st.session_state.follow_up_queue):
                next_question = st.session_state.follow_up_queue[st.session_state.follow_up_index]
                st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                st.session_state.follow_up_index += 1
            else:
                st.session_state.current_response["followup_answers"] = st.session_state.follow_up_answers
                st.session_state.responses.append(st.session_state.current_response)
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
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "All preset questions have been answered! Your final assessment is being generated..."
                    })
                    st.session_state.phase = "final"
        
    if st.session_state.phase == "final" and not st.session_state.final_generated:
        time.sleep(0.5)
        final_assessment = get_final_score(st.session_state.responses)
        print(st.session_state.chat_history)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "## Final Assessment\n" + final_assessment
        })

        api.push(chat_history=st.session_state.chat_history)
        st.session_state.final_generated = True

    display_chat()

if __name__ == "__main__":
    main()