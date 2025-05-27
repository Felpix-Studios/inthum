import os
import time
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import streamlit as st

QUESTIONS = [
    "I question my own opinions, positions, and viewpoints because they could be wrong.",
    "I reconsider my opinions when presented with new evidence.",
    "I recognize the value in opinions that are different from my own.",
    "I accept that my beliefs and attitudes may be wrong.",
    "In the face of conflicting evidence, I am open to changing my opinions.",
    "I like finding out new information that differs from what I already think is true",
]


def reset_test():
    for i in range(len(QUESTIONS)):
        response_key = f"response_{i}"
        if response_key in st.session_state:
            del st.session_state[response_key]
    
    if "responses_temp" in st.session_state:
        del st.session_state["responses_temp"]

      

    for key in ['chat_history', 'responses', 'submitted_all', 'final_generated']:
        if key in st.session_state:
            st.session_state[key] = []
    st.session_state.submitted_all = False
    st.session_state.final_generated = False

# -- Streamlit Application --
def intro_page():
    st.markdown("""
    <style>
    .likert-group button,
    .force-active-button {
        width: auto;
        padding: 0.25rem 0.75rem;
        font-weight: 500;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0 auto;
        display: block;
    }
    .likert-group {
      max-width: 800px;
      margin: 0 auto;
      gap: 0.1rem !important;
    }
    @media (max-width: 600px) {
      .likert-group {
        gap: 0.05rem !important;
      }
      .stHorizontalBlock {
        gap: 0.05rem !important;
      }
      .likert-group button,
      .likert-group .force-active-button {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
      }
      .center-button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
      }
      .stButton > button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
      }
    }
    .force-active-button {
        background-color: rgb(255, 75, 75) !important;
        color: white !important;
        border: 1px solid rgb(255, 75, 75) !important;
        box-shadow: 0 0 0 0.1rem rgba(255, 75, 75, 0.6) !important;
        cursor: default;
    }
    .center-button {
      display: flex !important;
      justify-content: center !important;
    }
    .center-button button {
      margin: 0 auto !important;
    }
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:72rem;
          }
      </style>
      """
    )
    logo_path = "new_plab_logo.png"
    st.logo(logo_path, size = "large")
    st.title("Intellectual Humility Assessment")
    st.write(
        """
        Do you have an intellectually humble mindset? Use this tool to find out.

        **What is intellectual humility?**
        - Being open to new ideas
        - Being willing to reconsider your beliefs when presented with new information or perspectives
        - Recognizing that you might not always have all the answers
        - Acknowledging that your knowledge and understanding can have limitations
        - Challenging your assumptions, biases, and level of certainty about something or someone

        **Why should I care about intellectual humility?**

        Research suggests that [intellectual humility](https://www.templeton.org/news/what-is-intellectual-humility) may improve well-being, enhance tolerance from other perspectives, and promote inquiry and learning. Understanding our intellectual humility is an important step in learning about our own blindspots.

        **Instructions**

        This tool will ask you a series of questions to generate your intellectual humility score. Your score is then compared to the average score from a previous [study](https://psycnet.apa.org/record/2016-23828-044) on intellectual humility. For each question, please select the option that indicates how well, if at all, you believe the phrase applies to yourself. 

        This quiz is based on the scale developed by [Leary et al.](https://pubmed.ncbi.nlm.nih.gov/28903672/) in their research on the features of intellectual humility. This tool is currently experimental and was partially supported by the John Templeton Foundation. Please provide feedback and report any issues to [info@polarizationlab.com](mailto:info@polarizationlab.com).
        """
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Assessment", key="to_questions", use_container_width=True):
            st.session_state.current_page = "questions"
            st.rerun()


def questions_page():
    st.markdown("""
    <style>
    .likert-group button,
    .force-active-button {
        width: auto;
        padding: 0.25rem 0.75rem;
        font-weight: 500;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0 auto;
        display: block;
    }
    .likert-group {
      max-width: 800px;
      margin: 0 auto;
      gap: 0.1rem !important;
    }
    /* Reduce gap for stHorizontalBlock (Streamlit columns) on small screens */
    @media (max-width: 600px) {
      .likert-group {
        gap: 0.05rem !important;
      }
      .stHorizontalBlock {
        gap: 0.05rem !important;
      }
      .stVerticalBlock {
        gap: 0.6rem !important;
      }
      .likert-group button,
      .likert-group .force-active-button {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
      }
      .center-button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
      }
      .stButton > button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
      }
    }
    .force-active-button {
        background-color: rgb(255, 75, 75) !important;
        color: white !important;
        border: 1px solid rgb(255, 75, 75) !important;
        box-shadow: 0 0 0 0.1rem rgba(255, 75, 75, 0.6) !important;
        cursor: default;
    }
    
    .center-button {
      display: flex !important;
      justify-content: center !important;
    }
    .center-button button {
      margin: 0 auto !important;
    }
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:72rem;
          }
      </style>
      """
    )
    response_dict = {}
    likert_options = {
        1: "Not at All",
        2: "Not Well",
        3: "Somewhat Well",
        4: "Well",
        5: "Very Well"
    }
    if "responses_temp" not in st.session_state:
        st.session_state.responses_temp = {}
    for i, question in enumerate(QUESTIONS):
        st.markdown(f"**Q{i + 1}. {question}**")
        if f"response_{i}" not in st.session_state:
            st.session_state[f"response_{i}"] = None
        st.markdown('<div class = "likert-group">', unsafe_allow_html=True)
        button_cols = st.columns(7)
        labels = list(likert_options.values())
        for j in range(7):
            with button_cols[j]:
                if 1 <= j <= 5:
                    label = labels[j-1]
                    btn_key = f"btn_{i}_{j}"
                    is_selected = st.session_state[f"response_{i}"] == j
                    st.markdown('<div class="center-button">', unsafe_allow_html=True)
                    if not is_selected:
                        if(st.button(label, key=btn_key)):
                            st.session_state[f"response_{i}"] = j
                            st.session_state.responses_temp[question] = j
                            st.rerun()
                    else:
                        st.markdown(
                            f"<button class ='force-active-button'>{label}</button>",
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.write("")
        st.markdown("</div>", unsafe_allow_html=True) 
        response_dict[question] = st.session_state[f"response_{i}"]
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_clicked = st.button("Submit All Answers", use_container_width=True, key="submit_all")

        if st.button("Back to Introduction", key="back_intro", use_container_width=True):
          st.session_state.current_page = "intro"
          st.rerun()
    if submit_clicked:
        missing = [q for q, ans in response_dict.items() if ans is None]
        if missing:
            st.error("Please answer all questions before submitting.")
        else:
            st.session_state.responses = []
            for idx, (q, ans) in enumerate(response_dict.items()):
                st.session_state.responses.append({
                    "question": q,
                    "scale_answer": int(ans)
                })
            st.session_state.submitted_all = True
            st.session_state.current_page = "results"
            st.rerun()
    


def results_page():
    st.markdown("""
    <style>
    .likert-group button,
    .force-active-button {
        width: auto;
        padding: 0.25rem 0.75rem;
        font-weight: 500;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0 auto;
        display: block;
    }
    .force-active-button {
        background-color: rgb(255, 75, 75) !important;
        color: white !important;
        border: 1px solid rgb(255, 75, 75) !important;
        box-shadow: 0 0 0 0.1rem rgba(255, 75, 75, 0.6) !important;
        cursor: default;
    }
    .center-button {
      display: flex !important;
      justify-content: center !important;
    }
    .center-button button {
      margin: 0 auto !important;
    }
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:72rem;
          }
      </style>
      """
    )
    if not st.session_state.get("submitted_all", False):
        st.warning("You must answer all questions first.")
        if st.button("Go to Questions", key="to_questions_from_results"):
            st.session_state.current_page = "questions"
            st.rerun()
        return
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

    st.write("""
    The average score is based on the mean intellectual humility score of 22.64 reported by Deffler, Leary, and Hoyle (2016).  
    """
    )
    mean_score = 22.64
    std_dev = 3.98
    x_vals_cut = np.linspace(6, 30, 500)
    y_vals_cut = norm.pdf(x_vals_cut, loc=mean_score, scale=std_dev)
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
        y=[0, 0.1],
        mode='lines',
        line=dict(color='green', dash='dot'),
        name=f'Your Score = {total_score}',
        hoverinfo='skip'
    ))
    fig.update_layout(
        title='Estimated Density of Intellectual Humility Scores',
        xaxis_title='Total Score',
        yaxis_title='Density',
        xaxis=dict(range=[6, 30]),
        template='simple_white',
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
    

    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Reset Test", key="reset_test", use_container_width=True):
            reset_test()
            st.session_state.current_page = "intro"
            st.rerun()
        
    st.write("---")
    st.write("""
    **What Should I Do Next?**
             
    By now, we hope you've learned a little bit about your intellectual humility. If you didn't score as high as you had hoped, click here to use our other tool, [Train your Intellectual Humility](https://inthum2.streamlit.app). Here, you can start practicing identifying intellectually humble language. 
    """)

# -- Streamlit Application --
def main():
    if "submitted_all" not in st.session_state:
        st.session_state.submitted_all = False
    if "final_generated" not in st.session_state:
        st.session_state.final_generated = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "intro"
    page = st.session_state.current_page
    if page == "intro":
        intro_page()
    elif page == "questions":
        questions_page()
    elif page == "results":
        results_page()

    
if __name__ == "__main__":
    main()