import streamlit as st
import os
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
import uuid

st.set_page_config(page_title="Academic Course Portal", layout="wide")

# =====================================
# COURSE CONFIGURATION
# =====================================

COURSES = {
    "Investment Banking": {
        "password": "ib123",
        "theme_color": "#0A3D62",
        "overview": """
### Investment Banking

This course introduces students to the structure of the financial system,
investment banking operations, public issues, underwriting, mergers and acquisitions,
venture capital, and regulatory framework in India.

**Key Learning Areas:**
- Financial system structure
- SEBI regulations
- Issue management process
- Mergers and acquisitions
- Venture capital and private equity
"""
    },

    "Corporate Finance": {
        "password": "cf123",
        "theme_color": "#1B5E20",
        "overview": """
### Corporate Finance

This course focuses on financial decision making within corporations.
Students learn capital budgeting, cost of capital, dividend policy,
financial analysis, and working capital management.

**Key Learning Areas:**
- Capital structure decisions
- Investment appraisal
- Risk return analysis
- Financial ratio analysis
- Dividend policy
"""
    },

    "Risk Management": {
        "password": "rm123",
        "theme_color": "#4A148C",
        "overview": """
### Risk Management

This course covers identification, measurement, and control of financial risks.
Students explore market risk, credit risk, operational risk,
derivatives, and risk mitigation strategies.

**Key Learning Areas:**
- Types of financial risk
- Hedging techniques
- Derivatives usage
- Basel norms
- Enterprise risk management
"""
    }
}

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# =====================================
# MAIN MENU
# =====================================

main_menu = st.selectbox("Main Website", ["Home", "Courses"])

# =====================================
# HOME
# =====================================

if main_menu == "Home":
    st.title("Academic Course Portal")
    st.write("Welcome to the official academic website.")
    st.write("Go to Courses to access your dashboard.")
    st.stop()

# =====================================
# COURSES PAGE
# =====================================

st.title("Courses")

selected_course = st.selectbox(
    "Step 1: Select Your Course",
    list(COURSES.keys())
)

course_config = COURSES[selected_course]
COURSE_PASSWORD = course_config["password"]

# =====================================
# LOGIN SYSTEM
# =====================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Step 2: Enter Course Password", type="password")

    if st.button("Login"):
        if pwd == COURSE_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect Password")

    st.stop()

with st.sidebar:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# =====================================
# FILE STRUCTURE AFTER LOGIN
# =====================================

if not os.path.exists("results"):
    os.makedirs("results")

VISIT_FILE = f"results/{selected_course.replace(' ','_')}_visits.csv"
RESULT_FILE = f"results/{selected_course.replace(' ','_')}_results.csv"

if not os.path.exists(VISIT_FILE):
    pd.DataFrame(columns=["timestamp"]).to_csv(VISIT_FILE, index=False)

if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["timestamp","quiz","student_name","student_RRN","score"]).to_csv(RESULT_FILE, index=False)

visit_df = pd.read_csv(VISIT_FILE)
visit_df = pd.concat(
    [visit_df, pd.DataFrame([{"timestamp": datetime.now()}])],
    ignore_index=True
)
visit_df.to_csv(VISIT_FILE, index=False)

# =====================================
# COURSE TITLE
# =====================================

st.markdown(
    f"<h1 style='text-align:center; color:{course_config['theme_color']};'>"
    f"{selected_course} Course Dashboard</h1>",
    unsafe_allow_html=True
)

# =====================================
# SIDEBAR MENU
# =====================================

menu = st.sidebar.selectbox(
    "Select Section",
    [
        "Course Overview",
        "Modules",
        "Case Study",
        "Video Lectures",
        "Activities and References",
        "Assessment",
        "Admin Analytics"
    ]
)

# =====================================
# COURSE OVERVIEW
# =====================================

if menu == "Course Overview":
    st.header("Course Overview")
    st.markdown(course_config["overview"])


#===================================
# module 
#==================================
# =====================================
# MODULES
# =====================================
elif menu == "Modules":
    st.header("Module Wise Content")

    # Path to the course folder
    course_folder = os.path.join("modules", selected_course.replace(' ','_'))
    
    # Check if folder exists
    if not os.path.exists(course_folder):
        st.warning("No modules uploaded yet.")
    else:
        # Get all subfolders (modules)
        modules = sorted(
            [m for m in os.listdir(course_folder)
             if os.path.isdir(os.path.join(course_folder, m)) and not m.startswith('.')]
        )
        
        if not modules:
            st.warning("No modules available.")
        else:
            selected_module = st.selectbox("Select Module", modules)
            module_path = os.path.join(course_folder, selected_module)
            
            # Get all PDF and Word files in this module
            files = sorted(
                [f for f in os.listdir(module_path)
                 if os.path.isfile(os.path.join(module_path, f)) 
                 and f.lower().endswith(('.pdf', '.docx', '.doc'))]
            )
            
            if not files:
                st.info("No files in this module.")
            else:
                st.subheader(f"{selected_module} Materials")
                
                # Show download buttons for each file
                for file in files:
                    file_path = os.path.join(module_path, file)
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"Download {file}",
                            data=f,
                            file_name=file,
                            mime="application/octet-stream"
                        )
# =====================================
# ASSESSMENT
# =====================================

elif menu == "Assessment":

    quiz_option = st.selectbox("Select Quiz", ["Quiz 1"])

    student_name = st.text_input("Student Name")
    student_RRN = st.text_input("Student RRN")

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = {}

    def run_quiz():

        if "submitted" not in st.session_state.quiz_data:
            st.session_state.quiz_data["submitted"] = False
            st.session_state.quiz_data["score"] = 0

        if not st.session_state.quiz_data["submitted"]:

            answer = st.radio(
                "RBI is the:",
                ["Central Bank","Commercial Bank","Insurance Company","Stock Exchange"]
            )

            if st.button("Submit Quiz"):
                if student_name == "" or student_RRN == "":
                    st.warning("Enter student details")
                else:
                    score = 1 if answer == "Central Bank" else 0

                    st.session_state.quiz_data["submitted"] = True
                    st.session_state.quiz_data["score"] = score

                    result_df = pd.read_csv(RESULT_FILE)
                    new_row = pd.DataFrame([{
                        "timestamp": datetime.now(),
                        "quiz": quiz_option,
                        "student_name": student_name,
                        "student_RRN": student_RRN,
                        "score": score
                    }])

                    result_df = pd.concat([result_df,new_row],ignore_index=True)
                    result_df.to_csv(RESULT_FILE,index=False)

                    st.rerun()

        else:
            score = st.session_state.quiz_data["score"]
            st.success(f"Score: {score}/1")

            if st.button("Reset Quiz"):
                st.session_state.quiz_data["submitted"] = False
                st.rerun()

    run_quiz()

# =====================================
# ADMIN ANALYTICS
# =====================================

elif menu == "Admin Analytics":

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_pwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Login as Admin"):
            if admin_pwd == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Admin Password")
    else:
        st.header("Admin Dashboard")

        visit_df = pd.read_csv(VISIT_FILE)
        result_df = pd.read_csv(RESULT_FILE)

        st.write(f"Total App Opens: {len(visit_df)}")
        st.write(f"Total Quiz Attempts: {len(result_df)}")

        if not result_df.empty:
            st.dataframe(result_df)

        if st.button("Logout Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()





