import os
import time
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -- Open-ended Questions --
QUESTIONS = [
    #"Can you describe a time you realized you were wrong about something important? How did you come to that realization, and what did you do afterward?",
    #"What’s a topic you used to feel very certain about, but now feel less certain—or even uncertain—about? What made you reconsider?",
    #"When you’re in a debate and you encounter evidence that contradicts your view, how do you usually respond?",
    #"In areas you’re most knowledgeable about, do you ever worry that you might still have blind spots? How do you watch out for them?",
    #"How do you decide which sources of information you trust and which you don’t?"
    "What are your primary sources of information when you are trying to learn about new issue or event?",
    "How do you decide which perspectives are worth engaging with or considering on social media?",
    "How do you typically react when someone challenges your beliefs or opinions on social media?"
]

# -- Easy Questions --
EASY_QUESTIONS = [
    {
        "type": "describe",
        "instruction": "How well do the following describe you? (Scale: Very well, Fairly well, Slightly well, Not well at all)",
        "scale": ["Very well", "Fairly well", "Slightly well", "Not well at all"],
        "questions": [
            "I recognize and appreciate the expertise of others in areas where I lack knowledge.",
            "I find it difficult to express my opinion if I think others won’t agree with what I say.",
            "When others disagree with my ideas, I feel like I'm being personally attacked.",
            #"I believe changing my mind would be a sign of weakness.",
            #"Even when I disagree with others, I can recognize when they have sound points.",
            #"I try to avoid engaging with people I think I’ll disagree with."
        ]
    },
    {
        "type": "frequency",
        "instruction": "How often do you do each of the following? (Scale: Often, Sometimes, Rarely, Never)",
        "scale": ["Often", "Sometimes", "Rarely", "Never"],
        "questions": [
            "Seek out perspectives that differ from my own.",
            "Approach someone with whom I disagree with curiosity.",
            #"Quickly dismiss viewpoints that differ from my own if I come across them online.",
            #"Hear others out, even if I disagree with them.",
            #"Reflect on whether my online sources and beliefs may be biased or incomplete."
        ]
    }
]

# -- Helper Functions --

# Function to generate follow-up questions based on user response to a preset question.
def get_assistant_follow_up(preset_question, user_response, chat_history):
    prompt = (
        f"Previous conversation: \"{chat_history}\"\n"
        f"The user was asked: \"{preset_question}\"\n"
        f"And responded: \"{user_response}\"\n\n"
        "You are an expert psycologist analyzing the user's response for their potential of intellectual humulity "
        "Please provide exactly 1 short, and only 1 follow-up question (each on its own line) with no extra formatting, "
        "no numbering, no bullet points, and no styling. Then on a separate line, provide one final scale question "
        "from 1 to 5 about how strongly the user agrees with a relevant statement. "
        "Your questions should be open-ended and designed to elicit more information about the user's thought process without any bias or leading language. "
        "You should also not try to have 2 follow-up questions or combine several questions into one. Only send one follow-up question. "
        "Do not be repetitive or ask the same question in a different way, and ensure that the questions are relevant to the user's responses. "
        "Return only the plain question text."
    )
    messages = [
        {"role": "system", "content": "You are a curious and thoughtful assistant."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages,
        temperature=0.5
    )
    return response.choices[0].message.content

# Function to generate the final assessment based on user responses. Prompt may need adjusting (should the scale questions be numerically calculated?)
def get_final_score(responses):
    prompt = (
        "You are an expert psychologist. Your task is to interpret how the user's answers and responses reflect their intellectual "
        "humility. Use the following definition of intellectual humility: Intellectual humility is the recognition that our knowledge and "
        "understanding are always limited and subject to growth or change. It involves acknowledging that we can be wrong, while staying open "
        "to learning from new information or perspectives. Individuals who exhibit intellectual humility demonstrate curiosity, actively seeking "
        "out opposing viewpoints to refine their own thinking. They also tend to be self-reflective about their cognitive biases and willing to "
        "correct mistakes in pursuit of truth. In essence, intellectual humility emphasizes understanding over ego, valuing the collaborative "
        "search for accuracy above the need to be right. Evaluate the following user responses to the questions and their follow-ups, "
        "and provide a final score on a scale from 1 (low intellectual humility) to 10 (high intellectual humility) along with a short explanation "
        "for the score. If a user makes no attempt to answer the question, you may assign them a score of 1 with a short explanation.\n\n"
        "User responses:\n\n"
    )
    for idx, resp in enumerate(responses, start=1):
        prompt += f"Question {idx}:\n"
        if 'preset_answer' in resp:
            prompt += f"Preset Answer: {resp.get('preset_answer', '')}\n"
            if 'followup_answers' in resp:
                for i, ans in enumerate(resp['followup_answers'], start=1):
                    prompt += f"Follow-up {i} Answer: {ans}\n"
        else:
            prompt += f"Q: {resp.get('question', '')}\n"
            prompt += f"A: {resp.get('answer', '')}\n"
        prompt += "\n"
    messages = [
        {"role": "system", "content": "You are an expert psychologist."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
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

# -- Streamlit Application --
def main():
    logo_path = "new_plab_logo.png"
    st.logo(logo_path, size="large")
    st.title("Intellectual Humility Chat Assessment")
    st.image(logo_path, width=520)
    st.write(
        """
        ### How Intellectually Humble Are You?
        Do you have an intellectually humble mindset? Use this tool to find out.

        Take this quiz to get your intellectual humility score! This app will ask you a series of questions to generate your intellectual humility score.

        This app is currently experimental and uses generative AI! Please provide feedback and report any issues.

        **What is intellectual humility?**
        - Being open to new ideas
        - Being willing to reconsider your beliefs when presented with new information or perspectives
        - Recognizing that you might not always have all the answers
        - Acknowledging that your knowledge and understanding can have limitations
        - Challenging your assumptions, biases, and level of certainty about something or someone

        **Why should I care about intellectual humility?** 
        - Researchers have found that [intellectual humility](https://constructivedialogue.org/assets/10651-Article-102975-1-10-20230821.pdf) is associated with positive traits like openness to new ideas and political views, greater scrutiny of misinformation, prosocial values, and empathy.
        - Understanding and improving our own intellectual humility is a critical step in understanding political polarization and misinformation.
        """
    )
    
    # -- Session State Initialization --
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "responses" not in st.session_state:
        st.session_state.responses = []
    if "phase" not in st.session_state:
        st.session_state.phase = "preset"  # used for preset question phases ("preset", "follow_up", "final")
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

    # New session state variable to control which question set is active: "easy" or "open-ended"
    if "question_style" not in st.session_state:
        st.session_state.question_style = "easy"

    if st.session_state.question_style == "easy":
        if "current_easy_group_index" not in st.session_state:
            st.session_state.current_easy_group_index = 0
        if "current_easy_question_index" not in st.session_state:
            st.session_state.current_easy_question_index = 0
    else:
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0

    # If chat history is empty, display the first question based on the current question_style.
    if not st.session_state.chat_history:
        if st.session_state.question_style == "easy":
            current_group = EASY_QUESTIONS[st.session_state.current_easy_group_index]
            current_question = current_group["questions"][st.session_state.current_easy_question_index]
            full_question_text = f"{current_group['instruction']}\n\n{current_question}"
            st.session_state.chat_history.append({"role": "assistant", "content": full_question_text})
        else:
            first_question = QUESTIONS[st.session_state.current_question_index]
            st.session_state.chat_history.append({"role": "assistant", "content": first_question})
    
    user_input = st.chat_input("Your message:")
    if user_input:
        # Always add the user's response to the chat history.
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # --- Easy Questions Branch ---
        if st.session_state.question_style == "easy":
            current_group = EASY_QUESTIONS[st.session_state.current_easy_group_index]
            current_question = current_group["questions"][st.session_state.current_easy_question_index]
            # Save the easy question response
            st.session_state.responses.append({
                "question": current_question,
                "answer": user_input
            })
            # Update indices for easy questions
            if st.session_state.current_easy_question_index < len(current_group["questions"]) - 1:
                st.session_state.current_easy_question_index += 1
                # Display the next easy question
                current_group = EASY_QUESTIONS[st.session_state.current_easy_group_index]
                next_question = current_group["questions"][st.session_state.current_easy_question_index]
                full_question_text = f"{current_group['instruction']}\n\n{next_question}"
                st.session_state.chat_history.append({"role": "assistant", "content": full_question_text})
            else:
                if st.session_state.current_easy_group_index < len(EASY_QUESTIONS) - 1:
                    st.session_state.current_easy_group_index += 1
                    st.session_state.current_easy_question_index = 0
                    current_group = EASY_QUESTIONS[st.session_state.current_easy_group_index]
                    next_question = current_group["questions"][st.session_state.current_easy_question_index]
                    full_question_text = f"{current_group['instruction']}\n\n{next_question}"
                    st.session_state.chat_history.append({"role": "assistant", "content": full_question_text})
                else:
                    st.session_state.question_style = "preset"
                    st.session_state.current_question_index = 0
                    st.session_state.phase = "preset"
                    first_preset = QUESTIONS[st.session_state.current_question_index]
                    st.session_state.chat_history.append({"role": "assistant", "content": first_preset})
        
        # --- Preset Questions Branch (with Follow-up) ---
        elif st.session_state.question_style == "preset":
            if st.session_state.phase == "preset":
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
    
    # Final Phase: Generate final assessment after all preset questions have been completed.
    if st.session_state.phase == "final" and not st.session_state.final_generated:
        time.sleep(0.5)
        final_assessment = get_final_score(st.session_state.responses)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "## Final Assessment\n" + final_assessment
        })

        # Save final assessment + responses to external API/source?

        st.session_state.final_generated = True

    display_chat()

if __name__ == "__main__":
    main()