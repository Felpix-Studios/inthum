import os
import time
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
#from dotenv import load_dotenv
import streamlit as st
# from openai import OpenAI

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -- Open-ended Questions --
QUESTIONS = [
    #"Can you describe a time you realized you were wrong about something important? How did you come to that realization, and what did you do afterward?",
    #"What's a topic you used to feel very certain about, but now feel less certain—or even uncertain—about? What made you reconsider?",
    #"When you're in a debate and you encounter evidence that contradicts your view, how do you usually respond?",
    #"In areas you're most knowledgeable about, do you ever worry that you might still have blind spots? How do you watch out for them?",
    #"How do you decide which sources of information you trust and which you don't?"
    # "What are your primary sources of information when you are trying to learn about new issue or event?",
    # "How do you decide which perspectives are worth engaging with or considering on social media?"
    # "How do you typically react when someone challenges your beliefs or opinions on social media?"
    "I question my own opinions, positions, and viewpoints because they could be wrong.",
    "I reconsider my opinions when presented with new evidence.",
    "I recognize the value in opinions that are different from my own.",
    "I accept that my beliefs and attitudes may be wrong.",
    "In the face of conflicting evidence, I am open to changing my opinions.",
    "I like finding out new information that differs from what I already think is true",
]

# -- Easy Questions --
EASY_QUESTIONS = [
    {
        "type": "describe",
        "instruction": "How well do the following describe you? (Scale: Very well, Fairly well, Slightly well, Not well at all)",
        "scale": ["Very well", "Fairly well", "Slightly well", "Not well at all"],
        "questions": [
            "I recognize and appreciate the expertise of others in areas where I lack knowledge.",
            "I find it difficult to express my opinion if I think others won't agree with what I say.",
            "When others disagree with my ideas, I feel like I'm being personally attacked.",
            #"I believe changing my mind would be a sign of weakness.",
            #"Even when I disagree with others, I can recognize when they have sound points.",
            #"I try to avoid engaging with people I think I'll disagree with."
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
# def get_assistant_follow_up(preset_question, user_response, chat_history):
#     prompt = (
#         f"Previous conversation: \"{chat_history}\"\n"
#         f"The user was asked: \"{preset_question}\"\n"
#         f"And responded: \"{user_response}\"\n\n"
#         "You are an expert psycologist analyzing the user's response for their potential of intellectual humulity"
#         "Please provide exactly 1 short, and only 1 follow-up questions (each on its own line) with no extra formatting, "
#         "no numbering, no bullet points, and no styling. Then on a separate line, provide one final scale question "
#         "from 1 to 5 about how strongly the user agrees with a relevant statement. "
#         "Your questions should be open-ended and designed to elicit more information about the user's thought process without any bias or leading language."
#         "You should also not try to have 2 follow-up questions or combine several questions into one. Only send one follow-up question."
#         "Do not be repetitive or ask the same question in a different way, and ensure that the questions are relevant to the user's responses."
#         "Return only the plain question text."
#     )
#     messages = [
#         {"role": "system", "content": "You are a curious and thoughtful assistant."},
#         {"role": "user", "content": prompt}
#     ]
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=messages,
#         temperature=0.5
#     )
#     return response.choices[0].message.content


# Function to generate the final assessment, prompt based on Volfovsky's repo
# def get_final_score(responses):
#     prompt = (
#         "You are an expert psychologist. Your task is to interpret how the user's answers and responses reflect thier intellectual"
#         "humility. Use the following definition of intellectual humility: Intellectual humility is the "
#         "recognition that our knowledge and understanding are always limited and subject to growth or change." 
#         "It involves acknowledging that we can be wrong, while staying open to learning from new information or perspectives."
#         "Individuals who exhibit intellectual humility demonstrate curiosity, actively seeking out opposing viewpoints to refine their own thinking."
#         "They also tend to be self-reflective about their cognitive biases and willing to correct mistakes in pursuit of truth."
#         "In essence, intellectual humility emphasizes understanding over ego, valuing the collaborative search for accuracy above the need to be right."
#         "Evaluate the following user responses to the questions and their follow-ups, "
#         "and provide a final score on a scale from 1 (low intellectual humility) to 10 (high intellectual humility) along with a short explanation for the score. If a user makes no attempt to answer the question, you may assign them a score of 1 with a short explanation.\n\n"
#         "User responses:\n\n"
#     )
#     for idx, resp in enumerate(responses, start=1):
#         prompt += f"Question {idx}:\n"
#         prompt += f"Preset Answer: {resp.get('preset_answer', '')}\n"
#         if 'followup_answers' in resp:
#             for i, ans in enumerate(resp['followup_answers'], start=1):
#                 prompt += f"Follow-up {i} Answer: {ans}\n"
#         prompt += "\n"
#     messages = [
#         {"role": "system", "content": "You are an expert psychologist."},
#         {"role": "user", "content": prompt}
#     ]
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=messages,
#         temperature=0.9
#     )
#     return response.choices[0].message.content

def display_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.chat_message("user").write(msg["content"])

def reset_test():
    for key in ['chat_history', 'responses', 'submitted_all', 'final_generated']:
        if key in st.session_state:
            st.session_state[key] = []
    st.session_state.submitted_all = False
    st.session_state.final_generated = False

# -- Streamlit Application --
def main():
    st.markdown("""
      <style>
      /* Target the radio group container */
      div[role="radiogroup"] {
          display: flex;
          justify-content: space-between;
          gap: 15%; /* Adjust this for spacing between buttons */
          width: 100%;
          padding: 0px 0px;
      }

      /* Center and evenly space radio button labels */
      div[role="radiogroup"] > label {
          flex: 1;
          text-align: center;
      }
      </style>
    """, unsafe_allow_html=True)

    logo_path = "new_plab_logo.png"
    st.logo(logo_path, size = "large")
    st.title("Intellectual Humility Chat Assessment")
    st.image(logo_path, width=520)
    st.write(
        """
        ### How Intellectually Humble Are You?
        Do you have an intellectually humble mindset? Use this tool to find out.

        Take this quiz to get your intellectual humility score! This app will ask you a series of questions to generate your intellectual humility score. Please rate how much you agree with each statement on a scale from 1 (strongly disagree) to 5 (strongly agree).

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
    if "submitted_all" not in st.session_state:
        st.session_state.submitted_all = False
    if "final_generated" not in st.session_state:
        st.session_state.final_generated = False

    # -- Show all questions at once --
    if not st.session_state.submitted_all:
        st.markdown("### Questions")
        response_dict = {}

        # Define Likert scale options
        likert_options = {
            1: "Strongly Disagree",
            2: "Disagree", 
            3: "Neither Agree nor Disagree",
            4: "Agree",
            5: "Strongly Agree"
        }

        for i, question in enumerate(QUESTIONS):
            st.markdown(f"**Q{i + 1}. {question}**")

            # Create containers with better spacing and alignment
            container = st.container()



            

            left,center_col,right = container.columns([1.5, 10, 1])
            with center_col:
              selected_value = st.radio(
                label="",
                options=[1, 2, 3, 4, 5],
                index = None,
                format_func = lambda x: "",
                horizontal=True,
                key=f"radio{i}",
              )

            

            

            # Update the selected label to be bold
            label_update_cols = container.columns(5)
            for j, (col, label) in enumerate(zip(label_update_cols, ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"])):
                with col:
                    if j+1 == selected_value:
                        st.markdown(f"<div style='text-align: center; font-size: 0.8em; font-weight: bold; color: #1E90FF;'>{label}</div>",     unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='text-align: center; font-size: 0.8em; color: #666;'>{label}</div>", unsafe_allow_html=True)

            # Add some spacing
            st.write("")


            st.write("---")

            response_dict[question] = selected_value

        # Create a styled submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_clicked = st.button("Submit All Answers", use_container_width=True, key="submit_all")
            if submit_clicked:
                missing = [q for q, ans in response_dict.items() if ans is None]
                if missing:
                  st.error("Please answer all questions before submitting.")
                else:
                    # Append responses to session state
                    for q, ans in response_dict.items():
                        st.session_state.responses.append({
                            "question": q,
                            "scale_answer": int(ans)
                        })
                    st.session_state.submitted_all = True
                    st.rerun()



    # --- Final assessment ---
    elif not st.session_state.final_generated:
        st.write("✅ All questions answered! Generating your final score...")
        scores = [resp["scale_answer"] for resp in st.session_state.responses]
        total_score = sum(scores)
        average_score = round(total_score / len(scores), 2)

        st.session_state.final_generated = True
        st.markdown("## Final Assessment")
        st.write(f"**Total Score:** {total_score} out of {5 * len(scores)}")

        st.markdown("#### How does your score compare to the average person?")
        if total_score >= 25:
            st.success("Your score places you in the **top 25%** for intellectual humility. 💡")
        elif total_score <= 20:
            st.error("Your score is in the **bottom 25%**, suggesting low intellectual humility.")
        else:
            st.info("Your score is in the **middle range**. You may be intellectually humble in some situations more than others.")
        mean_score = 22.64
        std_dev = 3.98
        x_vals_cut = np.linspace(13, 30, 500)
        y_vals_cut = norm.pdf(x_vals_cut, loc=mean_score, scale=std_dev)

        # Create the plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_vals_cut,
            y=y_vals_cut,
            mode='lines',
            line=dict(color='skyblue'),
            fill='tozeroy',
            name='Density',
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=[mean_score, mean_score],
            y=[0, norm.pdf(mean_score, loc=mean_score, scale=std_dev)],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Mean = 22.64',
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=[total_score, total_score],
            y=[0, norm.pdf(total_score, loc=mean_score, scale=std_dev)],
            mode='lines',
            line=dict(color='green', dash='dot'),
            name=f'Your Score = {total_score}',
            hoverinfo='skip'
        ))


        fig.update_layout(
            title='Estimated Density of Intellectual Humility Scores',
            xaxis_title='Total Score (13–30)',
            yaxis_title='Density',
            xaxis=dict(range=[13, 30]),
            template='simple_white',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add Reset Test button
        if st.button("Reset Test"):
            reset_test()
            st.rerun()
    else:
        # Show final assessment again with reset button
        scores = [resp["scale_answer"] for resp in st.session_state.responses]
        total_score = sum(scores)
        
        st.markdown("## Final Assessment")
        st.write(f"**Total Score:** {total_score} out of {5 * len(scores)}")

        st.markdown("#### How does your score compare to the average person?")
        if total_score >= 25:
            st.success("Your score places you in the **top 25%** for intellectual humility. 💡")
        elif total_score <= 20:
            st.error("Your score is in the **bottom 25%**, suggesting low intellectual humility.")
        else:
            st.info("Your score is in the **middle range**. You may be intellectually humble in some situations more than others.")
        
        mean_score = 22.64
        std_dev = 3.98
        x_vals_cut = np.linspace(13, 30, 500)
        y_vals_cut = norm.pdf(x_vals_cut, loc=mean_score, scale=std_dev)

        # Create the plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_vals_cut,
            y=y_vals_cut,
            mode='lines',
            line=dict(color='skyblue'),
            fill='tozeroy',
            name='Density',
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=[mean_score, mean_score],
            y=[0, norm.pdf(mean_score, loc=mean_score, scale=std_dev)],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Mean = 22.64',
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=[total_score, total_score],
            y=[0, norm.pdf(total_score, loc=mean_score, scale=std_dev)],
            mode='lines',
            line=dict(color='green', dash='dot'),
            name=f'Your Score = {total_score}',
            hoverinfo='skip'
        ))

        fig.update_layout(
            title='Estimated Density of Intellectual Humility Scores',
            xaxis_title='Total Score (13–30)',
            yaxis_title='Density',
            xaxis=dict(range=[13, 30]),
            template='simple_white',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add Reset Test button
        if st.button("Reset Test"):
            reset_test()
            st.rerun()

    display_chat()

    # if not st.session_state.chat_history and st.session_state.current_question_index < len(QUESTIONS):
    #     first_question = QUESTIONS[st.session_state.current_question_index]
    #     st.session_state.chat_history.append({"role": "assistant", "content": first_question})
    

        # if st.session_state.phase == "preset":
        #     st.session_state.chat_history.append({"role": "user", "content": user_input})
        #     st.session_state.current_response["preset_answer"] = user_input
        #     st.session_state.current_response["question"] = QUESTIONS[st.session_state.current_question_index]
            
        #     # Insert a temporary spinner message in-line.
        #     spinner_index = len(st.session_state.chat_history)
        #     st.session_state.chat_history.append({"role": "assistant", "content": "Generating follow-up questions..."})
            
        #     follow_up_text = get_assistant_follow_up(
        #         QUESTIONS[st.session_state.current_question_index],
        #         user_input,
        #         st.session_state.chat_history
        #     )
        #     lines = [line.strip() for line in follow_up_text.split("\n") if line.strip()]
        #     st.session_state.follow_up_queue = lines
        #     st.session_state.follow_up_index = 0
        #     st.session_state.follow_up_answers = []
            
        #     if lines:
        #         st.session_state.chat_history[spinner_index]["content"] = lines[0]
        #         st.session_state.follow_up_index = 1
        #     else:
        #         st.session_state.chat_history[spinner_index]["content"] = "No follow-up questions received."
            
        #     st.session_state.phase = "follow_up"
        
        # elif st.session_state.phase == "follow_up":
        #     st.session_state.chat_history.append({"role": "user", "content": user_input})
        #     st.session_state.follow_up_answers.append(user_input)
        #     if st.session_state.follow_up_index < len(st.session_state.follow_up_queue):
        #         next_question = st.session_state.follow_up_queue[st.session_state.follow_up_index]
        #         st.session_state.chat_history.append({"role": "assistant", "content": next_question})
        #         st.session_state.follow_up_index += 1
        #     else:
        #         st.session_state.current_response["followup_answers"] = st.session_state.follow_up_answers
        #         st.session_state.responses.append(st.session_state.current_response)
        #         st.session_state.current_response = {}
        #         st.session_state.follow_up_queue = []
        #         st.session_state.follow_up_index = 0
        #         st.session_state.follow_up_answers = []
        #         st.session_state.current_question_index += 1
        #         if st.session_state.current_question_index < len(QUESTIONS):
        #             next_preset = QUESTIONS[st.session_state.current_question_index]
        #             st.session_state.chat_history.append({"role": "assistant", "content": next_preset})
        #             st.session_state.phase = "preset"
        #         else:
        #             st.session_state.chat_history.append({
        #                 "role": "assistant",
        #                 "content": "All preset questions have been answered! Your final assessment is being generated..."
        #             })
        #             st.session_state.phase = "final"
        
    # if st.session_state.phase == "final" and not st.session_state.final_generated:
    #     time.sleep(0.5)
    #     final_assessment = get_final_score(st.session_state.responses)
    #     st.session_state.final_generated = True
    #     st.markdown("## Final Assessment")
    #     st.write(final_assessment)
        # print(st.session_state.chat_history)
        # st.session_state.chat_history.append({
        #     "role": "assistant",
        #     "content": "## Final Assessment\n" + final_assessment
        # })

        # api.push(chat_history=st.session_state.chat_history)
        # st.session_state.final_generated = True


if __name__ == "__main__":
    main()