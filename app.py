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
        "bg_color": "#E8F1FA",
        "theme_color": "#0A3D62",
    },
    "Corporate Finance": {
        "password": "cf123",
        "bg_color": "#E8F5E9",
        "theme_color": "#1B5E20",
    },
    "Risk Management": {
        "password": "rm123",
        "bg_color": "#F3E5F5",
        "theme_color": "#4A148C",
    },
   "Business Analytics": {
        "password": "rm123",
        "bg_color": "#F3E5F5",
        "theme_color": "#4A148C",
    },
    "Corporate Finance": {
        "password": "rm123",
        "bg_color": "#F3E5F5",
        "theme_color": "#4A148C",
    },
    "Risk Management": {
        "password": "rm123",
        "bg_color": "#F3E5F5",
        "theme_color": "#4A148C",
    }
}
  
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# =====================================
# COURSE SELECTION
# =====================================

selected_course = st.selectbox("Select Course", list(COURSES.keys()))
course_config = COURSES[selected_course]
COURSE_PASSWORD = course_config["password"]

# =====================================
# FILE STRUCTURE
# =====================================

if not os.path.exists("results"):
    os.makedirs("results")

VISIT_FILE = f"results/{selected_course.replace(' ','_')}_visits.csv"
RESULT_FILE = f"results/{selected_course.replace(' ','_')}_results.csv"

if not os.path.exists(VISIT_FILE):
    pd.DataFrame(columns=["timestamp"]).to_csv(VISIT_FILE, index=False)

if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["timestamp","quiz","student_name","student_RRN","score"]).to_csv(RESULT_FILE, index=False)

# Record visit
visit_df = pd.read_csv(VISIT_FILE)
visit_df = pd.concat([visit_df, pd.DataFrame([{"timestamp": datetime.now()}])], ignore_index=True)
visit_df.to_csv(VISIT_FILE, index=False)

# =====================================
# LOGIN SYSTEM
# =====================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.markdown(f"<h2 style='text-align:center;'>Login – {selected_course}</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Enter Course Password", type="password")
    if st.button("Login"):
        if pwd == COURSE_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect Password")

if not st.session_state.authenticated:
    login()
    st.stop()

with st.sidebar:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# =====================================
# TITLE
# =====================================

st.markdown(
    f"<h1 style='text-align:center; color:{course_config['color']};'>{selected_course} Course Portal</h1>",
    unsafe_allow_html=True
)

menu = st.sidebar.selectbox(
    "Select Section",
    ["Course Overview","Modules","Case Study","Video Lectures","Activities & References","Assessment","Admin Analytics"]
)

# =====================================
# COURSE OVERVIEW
# =====================================

if menu == "Course Overview":
    st.header("Course Overview")

    st.markdown("""
**Investment Banking & Financial Services** is a 4 credit undergraduate course designed for BBA Financial Services students.  
The course covers **60 total hours** including lectures and tutorials.

This course introduces students to the structure and functioning of the Indian Financial System with special focus on investment banking and financial services in India.

### Students will learn about:

- Indian Financial System and role of investment and merchant banking  
- SEBI regulations and issue management process  
- Public issues, book building and investor protection  
- Leasing and hire purchase systems with practical applications  
- Housing and mortgage finance in India  
- Venture capital, private equity and alternative investments  
- Insurance concepts and regulatory framework  

The course helps students understand financial market operations, regulatory guidelines and modern developments in the financial services sector.
""")

# =====================================
# ASSESSMENT SECTION
# =====================================

elif menu == "Assessment":

    quiz_option = st.selectbox("Select Quiz", ["Quiz 1","Quiz 2","Quiz 3"])

    student_name = st.text_input("Student Name")
    student_RRN = st.text_input("Student RRN")

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = {}

    def run_quiz(quiz_key, questions, correct_answers):

        if quiz_key not in st.session_state.quiz_data:
            st.session_state.quiz_data[quiz_key] = {"submitted":False,"score":0}

        quiz_state = st.session_state.quiz_data[quiz_key]

        if not quiz_state["submitted"]:
            answers = {}
            for i,(q,opts) in enumerate(questions.items()):
                answers[f"q{i+1}"] = st.radio(q,opts,key=f"{quiz_key}_{i}")

            if st.button("Submit Quiz"):
                if student_name=="" or student_RRN=="":
                    st.warning("Enter student details")
                else:
                    score=0
                    for key in correct_answers:
                        if answers[key]==correct_answers[key]:
                            score+=1

                    quiz_state["submitted"]=True
                    quiz_state["score"]=score

                    result_df=pd.read_csv(RESULT_FILE)
                    new_row=pd.DataFrame([{
                        "timestamp":datetime.now(),
                        "quiz":quiz_key,
                        "student_name":student_name,
                        "student_RRN":student_RRN,
                        "score":score
                    }])
                    result_df=pd.concat([result_df,new_row],ignore_index=True)
                    result_df.to_csv(RESULT_FILE,index=False)

                    st.rerun()

        else:
            score=quiz_state["score"]
            total=len(correct_answers)
            st.success(f"Score: {score}/{total}")

            percentage = (score / total) * 100

            if percentage >= 75:
                grade = "Distinction"
            elif percentage >= 60:
                grade = "First Class"
            elif percentage >= 50:
                grade = "Second Class"
            else:
                grade = "Pass"

            certificate_id = str(uuid.uuid4())[:8].upper()

            pdf_file=f"{quiz_key}_certificate.pdf"
            doc=SimpleDocTemplate(pdf_file,pagesize=landscape(A4))
            elements=[]
            styles=getSampleStyleSheet()

            gold_title = ParagraphStyle(
                name="GoldTitle",
                parent=styles["Title"],
                alignment=TA_CENTER,
                fontSize=26,
                textColor=colors.HexColor("#B8860B")
            )

            center_style = ParagraphStyle(
                name="Center",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                fontSize=15
            )

            big_name = ParagraphStyle(
                name="BigName",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                fontSize=24,
                textColor=colors.darkblue
            )

            qr_code = qr.QrCodeWidget(f"Certificate ID: {certificate_id}")
            bounds = qr_code.getBounds()
            size = 90
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            qr_drawing = Drawing(size, size, transform=[size/width,0,0,size/height,0,0])
            qr_drawing.add(qr_code)

            header_table = Table([[qr_drawing, Paragraph("", styles["Normal"])]],
                                 colWidths=[1.5*inch, 9*inch])

            elements.append(header_table)
            elements.append(Spacer(1,0.3*inch))

            elements.append(Paragraph(selected_course, gold_title))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph("Certificate of Achievement", center_style))
            elements.append(Spacer(1,0.5*inch))
            elements.append(Paragraph("This certificate is proudly presented to", center_style))
            elements.append(Spacer(1,0.4*inch))
            elements.append(Paragraph(f"<b>{student_name}</b>", big_name))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(f"Student RRN: {student_RRN}", center_style))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(
                f"For successfully completing {quiz_option} with a score of {score}/{total}.",
                center_style
            ))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(f"Grade Awarded: <b>{grade}</b>", center_style))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(f"Certificate ID: {certificate_id}", center_style))
            elements.append(Spacer(1,0.3*inch))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", center_style))

            doc.build(elements)

            with open(pdf_file,"rb") as f:
                st.download_button("Download Certificate",f,file_name=pdf_file)

            if st.button("Reset Quiz"):
                st.session_state.quiz_data[quiz_key]["submitted"]=False
                st.rerun()

    if quiz_option=="Quiz 1":
        questions={
            "RBI is the:":["Central Bank","Commercial Bank","Insurance Company","Stock Exchange"]
        }
        correct={"q1":"Central Bank"}
        run_quiz("quiz1",questions,correct)

# =====================================
# ADMIN ANALYTICS
# =====================================

elif menu == "Admin Analytics":

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated=False

    if not st.session_state.admin_authenticated:
        admin_pwd=st.text_input("Enter Admin Password",type="password")
        if st.button("Login as Admin"):
            if admin_pwd==ADMIN_PASSWORD:
                st.session_state.admin_authenticated=True
                st.rerun()
            else:
                st.error("Incorrect Admin Password")
    else:
        st.header("Admin Dashboard")

        visit_df=pd.read_csv(VISIT_FILE)
        result_df=pd.read_csv(RESULT_FILE)

        st.write(f"Total App Opens: {len(visit_df)}")
        st.write(f"Total Quiz Attempts: {len(result_df)}")

        if not result_df.empty:
            st.dataframe(result_df)

        if st.button("Logout Admin"):
            st.session_state.admin_authenticated=False

            st.rerun()







