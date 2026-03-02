import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

import portalocker 

# -----------------------
# CONFIG
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_CSV = os.path.join(BASE_DIR, "questions.csv")
RESPONSES_CSV = os.path.join(BASE_DIR, "user_responses.csv")
METADATA_CSV = os.path.join(BASE_DIR, "user_metadata.csv")
MAX_QUESTIONS_PER_USER = 15


def locked_csv_append(df, csv_path):

    dir_path = os.path.dirname(csv_path)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        portalocker.lock(f, portalocker.LOCK_EX)

        write_header = f.tell() == 0  # file is empty

        df.to_csv(
            f,
            header=write_header,
            index=False
        )

        f.flush()
        os.fsync(f.fileno())

        portalocker.unlock(f)






st.set_page_config(page_title="LLM Confidence Study", layout="wide")

# -----------------------
# CUSTOM STYLING - BALANCED & PROFESSIONAL
# -----------------------
st.markdown("""
<style>
    /* Reduce top padding */
    .main {
        background-color: #fafafa;
        padding-top: 2rem !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Typography */
    h1, .main h1, [data-testid="stHeader"] h1 {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        line-height: 1.8 !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0.5rem !important;
        padding: 0.3rem 0 !important;
        display: block !important;
        visibility: visible !important;
        overflow: visible !important;
    }
    
    h2 {
        color: #333333;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    h3 {
        color: #444444;
        font-weight: 600;
    }
    
    /* Make selectboxes more compact */
    .stSelectbox {
        max-width: 500px;
    }
    
    /* Answer boxes */
    .answer-box {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #e5e5e5;
        margin: 6px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .answer-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 10px;
        border-radius: 4px 4px 0 0;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: -6px;
    }
    
    /* Confidence badge */
    .confidence-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    
    /* Question box */
    .question-box {
        background-color: #ffffff;
        border-left: 4px solid #667eea;
        padding: 8px;
        border-radius: 4px;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Info boxes */
    .info-box {
        background-color: #eff6ff;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        margin: 10px 0;
        color: #1e40af;
    }
    
    .success-box {
        background-color: #f0fdf4;
        padding: 18px;
        border-radius: 6px;
        border-left: 3px solid #10b981;
        margin: 16px 0;
        color: #065f46;
    }
    
    .warning-box {
        background-color: #fffbeb;
        padding: 18px;
        border-radius: 6px;
        border-left: 3px solid #f59e0b;
        margin: 16px 0;
        color: #78350f;
    }
    
    /* Section headers */
    .section-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #667eea;
        padding: 4px 0;
        margin: 4px 0 6px 0;
        border-bottom: 2px solid #e0e7ff;
    }
    
    /* Evaluation section header */
    .eval-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #d97706;
        padding: 8px 0 4px 0;
        margin: 12px 0 8px 0;
        border-bottom: 3px solid #f59e0b;
    }
    
    /* Progress text */
    .progress-text {
        color: #667eea;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 4px 0;
    }
    
    /* Labels */
    .stRadio > label, .stSelectbox > label, .stTextArea > label {
        font-weight: 600;
        color: #374151;
        font-size: 0.95rem;
    }
    
    /* Captions */
    .stCaption {
        color: #6b7280 !important;
        font-size: 0.875rem;
    }
    
    /* Button - compact and styled */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
        font-size: 0.95rem;
        border-radius: 6px;
        transition: all 0.2s;
        width: auto !important;
        min-width: 200px;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transform: translateY(-1px);
    }
    
    /* Checkbox */
    .stCheckbox > label {
        font-weight: 500;
        color: #374151;
    }
    
    /* Divider */
    hr {
        margin: 10px 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Compact radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    /* Remove excessive container width */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }

    /* NLI cards (Entail / Contradict / Neutral) */
    .nli-card {
        padding: 18px;
        border-radius: 6px;
        height: 100%;
    }
    .nli-entail {
        background-color: #f0fdf4;
        border-left: 3px solid #10b981;
        color: #065f46;
    }
    .nli-entail h4 { color: #065f46; }
    .nli-contradict {
        background-color: #fef2f2;
        border-left: 3px solid #ef4444;
        color: #991b1b;
    }
    .nli-contradict h4 { color: #991b1b; }
    .nli-neutral {
        background-color: #f5f5f5;
        border-left: 3px solid #6b7280;
        color: #374151;
    }
    .nli-neutral h4 { color: #374151; }

    /* ---- DARK MODE OVERRIDES ---- */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #0e1117 !important;
        }

        h1, .main h1, [data-testid="stHeader"] h1 {
            color: #e0e0e0 !important;
        }

        h2 { color: #d0d0d0 !important; }
        h3 { color: #c0c0c0 !important; }

        /* Ensure all text inside custom boxes is light */
        .answer-box p, .answer-box div, .answer-box strong,
        .question-box p, .question-box strong,
        .info-box p, .info-box strong, .info-box li, .info-box ol,
        .success-box p, .success-box strong,
        .warning-box p, .warning-box strong {
            color: inherit !important;
        }

        .answer-box {
            background-color: #1e1e2e !important;
            border-color: #3a3a4a !important;
            color: #e0e0e0 !important;
        }

        .question-box {
            background-color: #1e1e2e !important;
            color: #e0e0e0 !important;
            box-shadow: 0 1px 3px rgba(255,255,255,0.05) !important;
        }

        .info-box {
            background-color: #1a2332 !important;
            border-left-color: #5b9cf6 !important;
            color: #93bbf5 !important;
        }
        .info-box h3 { color: #93bbf5 !important; }

        .success-box {
            background-color: #162b1f !important;
            border-left-color: #34d399 !important;
            color: #6ee7b7 !important;
        }

        .warning-box {
            background-color: #2b2310 !important;
            border-left-color: #fbbf24 !important;
            color: #fcd34d !important;
        }

        .section-header {
            color: #93a8f5 !important;
            border-bottom-color: #3a3f6b !important;
        }

        .eval-header {
            color: #fbbf24 !important;
            border-bottom-color: #b58900 !important;
        }

        .progress-text {
            color: #93a8f5 !important;
        }

        .stRadio > label, .stSelectbox > label, .stTextArea > label {
            color: #d0d0d0 !important;
        }

        .stCaption {
            color: #9ca3af !important;
        }

        .stCheckbox > label {
            color: #d0d0d0 !important;
        }

        hr {
            border-top-color: #3a3a4a !important;
        }

        .nli-card { color: #e0e0e0 !important; }
        .nli-entail { background-color: #162b1f !important; border-left-color: #34d399 !important; }
        .nli-entail h4 { color: #6ee7b7 !important; }
        .nli-contradict { background-color: #2b1515 !important; border-left-color: #f87171 !important; }
        .nli-contradict h4 { color: #fca5a5 !important; }
        .nli-neutral { background-color: #1e1e2e !important; border-left-color: #9ca3af !important; }
        .nli-neutral h4 { color: #d1d5db !important; }

        .study-complete-title { color: #e0e0e0 !important; }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_questions():
    """Load questions from CSV and add question IDs"""
    try:
        df = pd.read_csv(QUESTIONS_CSV)
        df = df.reset_index(drop=True)
        df["question_id"] = df.index
        return df
    except FileNotFoundError:
        st.error(f"Error: {QUESTIONS_CSV} not found. Please ensure the file exists.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        st.stop()

df = load_questions()

# -----------------------
# INITIALIZE SESSION STATE
# -----------------------
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0

# -----------------------
# SAVE RESPONSE FUNCTION
# -----------------------
def save_response(row, responses):
    """Save user response to CSV"""
    record = {
        # Meta
        "timestamp": datetime.now().isoformat(),
        "user_id": st.session_state.user_id,
        "question_id": row["question_id"],
        
        # Dataset info
        "dataset": row.get("dataset", ""),
        "category": row.get("category", ""),
        
        # Question + model outputs
        "question": row["question"],
        "answer_only": row["answer_only"],
        "answer_conf": row["answer_conf"],
        "explanation": row["explanation"],
        
        # Model confidence signals (NOT shown to user)
        "self_reported_confidence": row.get("self_reported_confidence", None),
        "mean_chosen_token_prob": row.get("mean_chosen_token_prob", None),
        "mean_logit_margin": row.get("mean_logit_margin", None),
        
        # User responses
        **responses
    }
    
    df_out = pd.DataFrame([record])
    #write_header = not os.path.exists(RESPONSES_CSV)
    #df_out.to_csv(RESPONSES_CSV, mode="a", header=write_header, index=False)
    locked_csv_append(df_out, RESPONSES_CSV)

# -----------------------
# STAGE 1: WELCOME & INSTRUCTIONS
# -----------------------
if st.session_state.stage == "welcome":
    st.title("AI Answer Evaluation Study")
    
    st.markdown("""
    <div class="info-box">
    <h3 style="margin-top: 0;">Welcome!</h3>
    <p>Thank you for taking part in this study. This survey takes approximately <strong>10–15 minutes</strong>.</p>
    <p>We are researching how people perceive AI-generated answers when they are presented in different ways.
    Your feedback will help us understand what makes AI responses more trustworthy and useful.</p>
    <p style="margin-bottom: 0;"><strong>No prior AI or technical knowledge is needed.</strong> We are interested in your honest opinion — there are no right or wrong answers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### What will you do?")
    
    st.markdown("""
    You will be shown **15 questions** that were answered by an AI system. For each question, you will see **two versions** of the AI's answer side by side:
    
    - **Left side — "Answer Only"**: Just the AI's short answer with no extra detail.
    - **Right side — "Answer with Explanation"**: The same answer, but with a confidence level and an explanation of why the AI chose that answer.
    
    After reading both, you will rate things like which format you prefer, how much you trust the answer, and how helpful the explanation was.
    """)
    
    st.markdown("### Sample — Here's what a question will look like")
    
    st.markdown('<div class="question-box"><strong>Question:</strong> What is the capital of France?</div>', unsafe_allow_html=True)
    
    sample_col1, sample_col2 = st.columns(2, gap="small")
    
    with sample_col1:
        st.markdown('<div class="answer-header">Answer Only</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="answer-box">
        Paris
        </div>
        """, unsafe_allow_html=True)
    
    with sample_col2:
        st.markdown('<div class="answer-header">Answer with Explanation</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="answer-box">
        <div style="margin-bottom: 14px;"><strong>Answer:</strong> Paris</div>
        <div class="confidence-badge">Model Confidence: High (95%)</div>
        <div style="margin-top: 14px;"><strong>Explanation:</strong><br>Paris has been the capital of France since the 10th century and is the seat of the French government.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""
    <div class="info-box steps-box">
    <strong>After seeing both answers, you will be asked to:</strong>
    <ol style="margin-bottom: 0;">
        <li>Choose which answer format you prefer (left or right)</li>
        <li>Rate how much you trust the answer (0–5)</li>
        <li>Rate how helpful the explanation was (0–5)</li>
        <li>Rate whether the AI's confidence matched your own feeling (0–5)</li>
        <li>Note if you spotted any issues</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""
    <div class="warning-box">
    <strong>Privacy Notice:</strong> No personally identifiable information is collected in this study.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("I understand — Continue", type="primary"):
            st.session_state.stage = "demographics"
            st.rerun()
    
    st.stop()

# -----------------------
# STAGE 2: DEMOGRAPHICS
# -----------------------
if st.session_state.stage == "demographics":
    st.title("About You")
    
    st.markdown("""
    <div class="info-box">
    <p style="margin: 0;">Before we begin, please tell us a little about yourself. This helps us understand how different groups of people perceive AI answers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Participant Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        age_range = st.selectbox(
            "Age range",
            ["12-17","18-24", "25-34", "35-44", "45+", "Prefer not to say"]
        )
        
        education = st.selectbox(
            "Highest education level",
            [
                "High school or below",
                "Undergraduate student",
                "Postgraduate student",
                "Working professional",
                "Other"
            ]
        )
        
        english_level = st.selectbox(
            "English proficiency",
            [
                "English is my first language",
                "English is my primary working language",
                "English is not my primary language"
            ]
        )
        
        ai_usage = st.selectbox(
            "How often do you use AI tools (ChatGPT, Copilot, etc.)?",
            ["Daily", "Weekly", "Occasionally", "Rarely", "Never"]
        )
        
        st.markdown("**How familiar are you with AI systems?**")
        st.caption("1 = Not familiar  •  5 = Very familiar")
        ai_familiarity = st.radio(
            "Select your familiarity level:",
            options=[1, 2, 3, 4, 5],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    consent = st.checkbox(
        "I understand the purpose of the study and consent to participate"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Continue to Study", type="primary"):
            if not consent:
                st.warning("Please provide consent to continue.")
            else:
                # Save demographics
                st.session_state.user_metadata = {
                    "user_id": st.session_state.user_id,
                    "timestamp": datetime.now().isoformat(),
                    "age_range": age_range,
                    "education_level": education,
                    "english_proficiency": english_level,
                    "ai_usage_frequency": ai_usage,
                    "ai_familiarity_score": ai_familiarity
                }
                
                meta_df = pd.DataFrame([st.session_state.user_metadata])
                locked_csv_append(meta_df, METADATA_CSV)
                
                st.session_state.stage = "intro"
                st.rerun()
    
    st.stop()

# -----------------------
# STAGE 3: TERMINOLOGY & KEY TERMS
# -----------------------
if st.session_state.stage == "intro":
    st.title("Study Instructions")
    
    st.markdown("""
    <div class="info-box">
    <p style="margin: 0;"><strong>Please read the following information carefully before beginning.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Understanding Key Terms")
    
    st.markdown("""
    Some questions in this study use specific terminology. Here's what these terms mean:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nli-card nli-entail">
        <h4 style="margin-top: 0;">✓ Entail</h4>
        <p style="margin-bottom: 8px;"><strong>The premise clearly supports the hypothesis</strong></p>
        <p style="font-size: 0.9rem; margin-bottom: 0;">
        <strong>Example:</strong><br>
        Premise: A man is running.<br>
        Hypothesis: A man is moving.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="nli-card nli-contradict">
        <h4 style="margin-top: 0;">✗ Contradict</h4>
        <p style="margin-bottom: 8px;"><strong>The premise clearly conflicts with the hypothesis</strong></p>
        <p style="font-size: 0.9rem; margin-bottom: 0;">
        <strong>Example:</strong><br>
        Premise: A man is standing still.<br>
        Hypothesis: A man is running.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="nli-card nli-neutral">
        <h4 style="margin-top: 0;">○ Neutral</h4>
        <p style="margin-bottom: 8px;"><strong>The premise does not provide enough information</strong></p>
        <p style="font-size: 0.9rem; margin-bottom: 0;">
        <strong>Example:</strong><br>
        Premise: A man is pointing at a woman.<br>
        Hypothesis: A man is smiling.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <p style="margin: 0;"><strong>Important:</strong> There are no right or wrong answers. We are interested in your personal judgment and evaluation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Begin Study", type="primary"):
            st.session_state.stage = "questions"
            st.rerun()
    
    st.stop()

# -----------------------
# STAGE 4: QUESTIONS
# -----------------------
if st.session_state.stage == "questions":
    
    # Initialize questions on first entry to this stage
    if "questions" not in st.session_state:
        # Sample 5 from each dataset
        cose = df[df["dataset"] == "CoSE"].sample(n=5, random_state=None)
        esnli = df[df["dataset"] == "eSNLI"].sample(n=5, random_state=None)
        truthfulqa = df[df["dataset"] == "TruthfulQA"].sample(n=5, random_state=None)
        
        # Combine and shuffle
        combined = pd.concat([cose, esnli, truthfulqa])
        combined = combined.sample(frac=1).reset_index(drop=True)
        
        st.session_state.questions = combined
    
    # Dict to hold all responses until study is complete
    if "all_responses" not in st.session_state:
        st.session_state.all_responses = {}
    
    # Check if study is complete
    if st.session_state.q_idx >= min(len(st.session_state.questions), MAX_QUESTIONS_PER_USER):
        # Save ALL responses to CSV now
        for idx, resp in st.session_state.all_responses.items():
            q_row = st.session_state.questions.iloc[idx]
            save_response(q_row, resp)
        
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
        <h1 class="study-complete-title" style="font-size: 2.5rem;">Study Complete</h1>
        <div class="success-box" style="margin: 20px auto; max-width: 600px;">
        <p style="font-size: 1.1rem; margin: 0;"><strong>Thank you for your participation!</strong></p>
        <p style="margin-top: 12px; margin-bottom: 0;">Your responses have been saved successfully. You may now close this window.</p>
        </div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        st.stop()
    
    # -----------------------
    # DISPLAY CURRENT QUESTION
    # -----------------------
    row = st.session_state.questions.iloc[st.session_state.q_idx]
    qid = row["question_id"]
    cur_idx = st.session_state.q_idx
    
    # Load previously saved answers for this question (if user navigated back)
    prev = st.session_state.all_responses.get(cur_idx, {})
    
    st.title("AI Answer Evaluation Study")
    
    # Progress indicator
    progress_pct = (st.session_state.q_idx) / MAX_QUESTIONS_PER_USER
    st.progress(progress_pct)
    st.markdown(f'<div class="progress-text">Question {st.session_state.q_idx + 1} of {MAX_QUESTIONS_PER_USER}</div>', unsafe_allow_html=True)
    
    # Question display
    st.markdown(f'<div class="question-box"><strong>Question:</strong> {row["question"]}</div>', unsafe_allow_html=True)
    
    # -----------------------
    # ANSWERS SIDE BY SIDE
    # -----------------------
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        st.markdown('<div class="answer-header">Answer Only</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="answer-box">
        {row["answer_only"]}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="answer-header">Answer with Explanation</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="answer-box">
        <div style="margin-bottom: 14px;"><strong>Answer:</strong> {row["answer_conf"]}</div>
        """, unsafe_allow_html=True)
        
        if "self_reported_confidence" in row and not pd.isna(row["self_reported_confidence"]):
            # Display confidence as-is from the file (don't convert)
            st.markdown(f"""
            <div class="confidence-badge">
            Model Confidence: {row["self_reported_confidence"]}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-top: 14px;"><strong>Explanation:</strong><br>{row["explanation"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # -----------------------
    # USER FEEDBACK (pre-filled if revisiting)
    # -----------------------
    st.markdown('<div class="eval-header">📝 Your Evaluation</div>', unsafe_allow_html=True)
    
    pref_options = ["Answer only", "Answer with explanation", "Disagree with both"]
    pref_default = pref_options.index(prev["preferred_answer"]) if "preferred_answer" in prev else 0
    
    trust_options = [0, 1, 2, 3, 4, 5]
    trust_default = trust_options.index(prev["trust_score"]) if "trust_score" in prev else 0
    
    help_options = [0, 1, 2, 3, 4, 5]
    help_default = help_options.index(prev["helpfulness_score"]) if "helpfulness_score" in prev else 0
    
    align_options = [0, 1, 2, 3, 4, 5]
    align_default = align_options.index(prev["confidence_alignment"]) if "confidence_alignment" in prev else 0
    
    issue_options = ["No", "Yes", "Not sure"]
    issue_default = issue_options.index(prev["noticed_issue"]) if "noticed_issue" in prev else 0
    
    # First row of feedback - 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Which answer format do you prefer?**")
        preferred = st.radio(
            "Preference:",
            pref_options,
            index=pref_default,
            horizontal=True,
            key=f"pref_{qid}_{cur_idx}",
            label_visibility="collapsed"
        )
        
        st.markdown("**How much do you trust this answer?**")
        st.caption("0 = Not at all  •  5 = Completely")
        trust = st.radio(
            "Trust level:",
            options=trust_options,
            index=trust_default,
            horizontal=True,
            key=f"trust_{qid}_{cur_idx}",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**How helpful was the explanation?**")
        st.caption("0 = Not helpful  •  5 = Very helpful")
        helpfulness = st.radio(
            "Helpfulness:",
            options=help_options,
            index=help_default,
            horizontal=True,
            key=f"help_{qid}_{cur_idx}",
            label_visibility="collapsed"
        )
        
        st.markdown("**Did the model's confidence level match your own confidence?**")
        st.caption("0 = Not at all  •  5 = Perfectly aligned")
        confidence_alignment = st.radio(
            "Alignment:",
            options=align_options,
            index=align_default,
            horizontal=True,
            key=f"align_{qid}_{cur_idx}",
            label_visibility="collapsed"
        )
    
    # Second row - full width
    st.markdown("**Did you notice any issues with the explanation?**")
    noticed_issue = st.radio(
        "Issues:",
        issue_options,
        index=issue_default,
        horizontal=True,
        key=f"noticed_{qid}_{cur_idx}",
        label_visibility="collapsed"
    )
    
    issue_comment = ""
    if noticed_issue == "Yes":
        issue_comment = st.text_area(
            "Please describe the issue:",
            value=prev.get("issue_comment", ""),
            key=f"issue_comment_{qid}_{cur_idx}",
            placeholder="Describe any issues you noticed...",
            height=60
        )
    
    free_text = st.text_area(
        "Additional comments (optional):",
        value=prev.get("comments", ""),
        key=f"comment_{qid}_{cur_idx}",
        placeholder="Any other thoughts or feedback...",
        height=60
    )
    
    # -----------------------
    # Helper to capture current answers
    # -----------------------
    def _collect_responses():
        return {
            "preferred_answer": preferred,
            "trust_score": trust,
            "helpfulness_score": helpfulness,
            "confidence_alignment": confidence_alignment,
            "noticed_issue": noticed_issue,
            "issue_comment": issue_comment,
            "comments": free_text
        }
    
    # -----------------------
    # NAVIGATION BUTTONS
    # -----------------------
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if cur_idx > 0:
            if st.button("← Previous Question"):
                st.session_state.all_responses[cur_idx] = _collect_responses()
                st.session_state.q_idx -= 1
                st.rerun()
    with col2:
        btn_label = "Submit & Finish" if cur_idx == MAX_QUESTIONS_PER_USER - 1 else "Next Question →"
        if st.button(btn_label, type="primary"):
            st.session_state.all_responses[cur_idx] = _collect_responses()
            st.session_state.q_idx += 1
            st.rerun()