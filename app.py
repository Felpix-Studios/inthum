import os
import time
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
from scipy.stats import norm
import streamlit as st


logo_path = "new_plab_logo.png"


def scroll_to_top():
    components.html("""
        <script>
            function doScroll() {
                var container = null;
                try {
                    if (window.parent && window.parent.document) {
                        container = window.parent.document.querySelector('.stMainBlockContainer');
                    }
                } catch (e) {
                    container = document.querySelector('.stMainBlockContainer');
                }
                if (container) {
                    // Use scrollIntoView with block: 'start', then force scroll to top as a fallback
                    container.scrollIntoView({behavior: 'auto', block: 'start'});
                    setTimeout(function() {
                        if (window.parent && window.parent.scrollTo) {
                            window.parent.scrollTo({ top: 0, left: 0, behavior: 'auto' });
                        }
                        if (window.scrollTo) {
                            window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
                        }
                    }, 10);
                } else {
                    if (window.parent && window.parent.scrollTo) {
                        window.parent.scrollTo({ top: 0, left: 0, behavior: 'auto' });
                    }
                    if (window.scrollTo) {
                        window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
                    }
                }
            }
            if ('scrollRestoration' in history) {
                history.scrollRestoration = 'manual';
            }
            setTimeout(doScroll, 10);
        </script>
    """, height=0)

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
    
    if "current_question_index" in st.session_state:
        del st.session_state["current_question_index"]

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
    /* Reduce gap for stHorizontalBlock (Streamlit columns) on small screens and left-align buttons */
    @media (max-width: 600px) {
      .likert-group {
        gap: 0.05rem !important;
        justify-content: flex-start !important;
      }
      .stHorizontalBlock {
        gap: 0.05rem !important;
        justify-content: flex-start !important;
      }
      .stVerticalBlock {
        gap: 0.6rem !important;
      }
      .likert-group button,
      .force-active-button {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        display: block !important;
      }
      .likert-group .force-active-button {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        display: block !important;
        /* Ensure active button stays left-aligned and same size as others */
      }
      .center-button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        justify-content: flex-start !important;
      }
      .center-button button {
        margin-left: 0 !important;
        margin-right: auto !important;
      }
      .stButton > button {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        margin-left: 0 !important;
        margin-right: auto !important;
      }
    }
                
    .force-active-button {
        background-color: rgb(255, 75, 75) !important;
        color: white !important;
        border: 1px solid rgb(255, 75, 75) !important;
        box-shadow: 0 0 0 0.1rem rgba(255, 75, 75, 0.6) !important;
        cursor: default;
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        display: block !important;
                
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
    p:not(button p):not(.stAlertContainer p):not(.stAlertSuccess p):not(.stAlertInfo p):not(.stAlertError p) {
      margin-bottom: 0.5rem !important;
    }
    li{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }
    button[kind="primary"] {
      background-color: #6e32ce !important;
      color: white !important;
      border-color: #6e32ce !important;
    }
    button[kind="primary"]:hover {
      border-color: #5828A4 !important;
      color: white !important;
      background-color: #5828A4 !important;
    }
    button[kind="primary"]:active {
      background-color: white !important;
      color: #6e32ce !important;
      border-color: #6e32ce !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:50rem;
              padding-top: 1rem !important;
          }
      </style>
      """
    )
    
    st.title("Intellectual Humility Assessment")
    st.write(
        """
        **Do you have an intellectually humble mindset? Use this quiz to find out!**

        **What is intellectual humility?**
        - Being open to new ideas
        - Being willing to reconsider your beliefs when presented with new information or perspectives
        - Recognizing that you might not always have all the answers
        - Acknowledging that your knowledge and understanding can have limitations
        - Challenging your assumptions, biases, and level of certainty about something or someone

        **Why should I care about intellectual humility?**

        Research shows [intellectual humility](https://www.templeton.org/news/what-is-intellectual-humility) may enhance tolerance from other perspectives and promote inquiry.

        **Instructions**

        This quiz asks six questions to generate your intellectual humility score and will compare your score to the general public.

        *This quiz is based on the scale developed by [Leary et al.](https://pubmed.ncbi.nlm.nih.gov/28903672/) in their research on the features of intellectual humility. This quiz is currently experimental and was partially supported by the John Templeton Foundation. Please provide feedback and report any issues to [info@polarizationlab.com](mailto:info@polarizationlab.com).*
        """
    )

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Assessment", key="to_questions", use_container_width=True, type="primary"):
            st.session_state.current_page = "questions"
            st.rerun()
    




def questions_page():
    st.markdown("""
    <style>
    .likert-group button,
    .force-active-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 400;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        min-height: 2.5rem;
        margin: 0px;
        line-height: 1.6;
        text-transform: none;
        font-family: inherit;
        color: inherit;
        width: auto;
        cursor: pointer;
        user-select: none;
        background-color: #fff;
        border: 1px solid rgba(49, 51, 63, 0.2);
        box-sizing: border-box;
        text-align: left;
        box-shadow: none;
        transition: background 0.1s, border 0.1s;
    }
    .likert-group {
      max-width: 480px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 0.1rem;
    }
    

    .force-active-button {
        background-color: rgb(255, 75, 75) !important;
        color: white !important;
        border: 1px solid rgb(255, 75, 75) !important;
        box-shadow: 0 0 0 0.1rem rgba(255, 75, 75, 0.6) !important;
        cursor: default;
    }
    
    .question-text {
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .progress-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        height: 8px;
        margin-bottom: 1.5rem;
    }
    
    .progress-fill {
        background-color: rgb(255, 75, 75);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:50rem;
              padding-top: 1rem !important;
          }
      </style>
      """)
    
    # Initialize session state for question navigation
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "responses_temp" not in st.session_state:
        st.session_state.responses_temp = {}
    
    # Initialize all response keys
    for i in range(len(QUESTIONS)):
        if f"response_{i}" not in st.session_state:
            st.session_state[f"response_{i}"] = None
    
    current_index = st.session_state.current_question_index
    total_questions = len(QUESTIONS)
    current_question = QUESTIONS[current_index]
    
    likert_options = {
        1: "Not at All",
        2: "Not Well", 
        3: "Somewhat Well",
        4: "Well",
        5: "Very Well"
    }
    
    
    # Progress bar
    progress_percent = ((current_index + 1) / total_questions) * 100
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percent}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### How well does the following statement apply to you?")
    
    # Display current question
    st.markdown(f"<div class='question-text'>{current_question}</div>", unsafe_allow_html=True)
    
    # Display answer options
    st.markdown('<div class = "likert-group">', unsafe_allow_html=True)
    for j in range(1, 6):
        label = likert_options[j]
        btn_key = f"btn_{current_index}_{j}"
        is_selected = st.session_state[f"response_{current_index}"] == j
        if not is_selected:
            if st.button(label, key=btn_key):
                st.session_state[f"response_{current_index}"] = j
                st.session_state.responses_temp[current_question] = j
                st.rerun()
        else:
            st.markdown(
                f"<button class ='force-active-button'>{label}</button>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    if current_index == 0:
        # First question: Back to Introduction and Next
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Back to Introduction", key="back_intro", use_container_width=True):
                st.session_state.current_page = "intro"
                st.rerun()
        with col2:
            current_answer = st.session_state[f"response_{current_index}"]
            if current_answer is not None:
                if st.button("Next Question", key="next_question", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                st.button("Next Question", key="next_question_disabled", use_container_width=True, disabled=True)
                st.caption("Please select an answer to continue")
                
    elif current_index == total_questions - 1:
        # Last question: Previous and Submit All Answers
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous Question", key="prev_question", use_container_width=True):
                st.session_state.current_question_index -= 1
                st.rerun()
        with col2:
            current_answer = st.session_state[f"response_{current_index}"]
            if current_answer is not None:
                if st.button("Submit All Answers", key="submit_all", use_container_width=True):
                    # Check if all questions are answered
                    response_dict = {}
                    for i, question in enumerate(QUESTIONS):
                        response_dict[question] = st.session_state[f"response_{i}"]
                    
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
            else:
                st.button("Submit All Answers", key="submit_all_disabled", use_container_width=True, disabled=True)
    else:
        # Middle questions: Previous and Next
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous Question", key="prev_question", use_container_width=True):
                st.session_state.current_question_index -= 1
                st.rerun()
        with col2:
            current_answer = st.session_state[f"response_{current_index}"]
            if current_answer is not None:
                if st.button("Next Question", key="next_question", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                st.button("Next Question", key="next_question_disabled", use_container_width=True, disabled=True)
                
    
    scroll_to_top()

            
    

    

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
    p:not(button p):not(.stAlertContainer p):not(.stAlertSuccess p):not(.stAlertInfo p):not(.stAlertError p) {
      margin-bottom: 0.5rem !important;
    }
                

    </style>
    """, unsafe_allow_html=True)

    st.html("""
      <style>
          .stMainBlockContainer {
              max-width:50rem;
              padding-top: 1rem !important;
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

    st.markdown('<div id="scroll-anchor"></div>', unsafe_allow_html=True)
    st.title("Results: Intellectual Humility Assessment")
    st.write(f"### Your score is {total_score} out of {5 * len(scores)}")

    st.markdown("**How does your score compare to the average person?**")
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
        name='',
        hoverinfo='skip',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[mean_score, mean_score],
        y=[0, norm.pdf(mean_score, loc=mean_score, scale=std_dev)],
        mode='lines',
        line=dict(color='red', dash='dash', width=3),
        name='Population Average = 22.64',
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=[total_score, total_score],
        y=[0, 0.1],
        mode='lines',
        line=dict(color='green', dash='dot', width=3),
        name=f'Your Score = {total_score}',
        hoverinfo='skip'
    ))
    fig.update_layout(
        title='Estimated Distribution of Intellectual Humility Scores',
        xaxis_title='Total Score',
        yaxis_title='Distribution',
        yaxis=dict(showticklabels=False),
        xaxis=dict(range=[6, 30]),
        template='simple_white',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            xanchor='center',
            y= -0.4,
            x=0.5,
          ),
    )
    st.plotly_chart(fig, use_container_width=True)
    

    
    
    st.write("""
    **What Now?**
    
    Use our other tool, [Train your Intellectual Humility](https://inthum2.streamlit.app), to learn how to identify and use intellectually humble language.
    """)
    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Reset Test", key="reset_test", use_container_width=True):
            reset_test()
            st.session_state.current_page = "intro"
            st.rerun()
    scroll_to_top()
    


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