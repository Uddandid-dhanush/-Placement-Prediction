import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from collections import Counter

# =========================
# CUSTOM CSS FOR STYLING
# =========================
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
   
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-bottom: 1rem;
        border-left: 4px solid #4F46E5;
        padding-left: 1rem;
    }
   
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
        transition: transform 0.3s ease;
    }
   
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
   
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
   
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
   
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
   
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
   
    section[data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-weight: 500;
    }
   
    /* Chatbot styling */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        max-height: 500px;
        overflow-y: auto;
    }
   
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
   
    .bot-message {
        background: #F3F4F6;
        color: #374151;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 5px 0;
        max-width: 80%;
    }
   
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
   
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
   
    .stTabs [data-baseweb="tab"] {
        background-color: #F3F4F6;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
    }
   
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG
# =========================
DB_PATH = "data/placemate.db"
ADMIN_USERNAME = "faculty"
ADMIN_PASSWORD = "12345"

st.set_page_config(
    page_title="PlaceMate Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
os.makedirs("data", exist_ok=True)

# =========================
# BRANCH-SPECIFIC CONFIGURATION
# =========================
BRANCH_CONFIG = {
    "CSE": {
        "coding_required": True,
        "technical_skills": ["Python", "Java", "C++", "JavaScript", "SQL", "Data Structures", "Algorithms", "Machine Learning", "Web Development", "Mobile Development"],
        "tools": ["VS Code", "IntelliJ", "Git", "Docker", "AWS", "MySQL", "MongoDB", "React", "Node.js", "TensorFlow"],
        "companies": ["Google", "Microsoft", "Amazon", "Meta", "Adobe", "Oracle", "Intel", "Cisco", "TCS", "Infosys", "Wipro", "Accenture"],
        "career_paths": ["Software Engineer", "Data Scientist", "ML Engineer", "DevOps Engineer", "Cloud Architect", "Full Stack Developer"]
    },
    "ECE": {
        "coding_required": True,
        "technical_skills": ["Embedded Systems", "VLSI", "Digital Signal Processing", "PCB Design", "MATLAB", "Verilog", "VHDL", "IoT", "ARM Cortex"],
        "tools": ["Cadence", "Xilinx", "Multisim", "Keil", "Arduino", "Raspberry Pi", "Oscilloscope", "Logic Analyzer"],
        "companies": ["Intel", "Qualcomm", "Texas Instruments", "Samsung", "Broadcom", "NVIDIA", "AMD", "Huawei", "Ericsson"],
        "career_paths": ["VLSI Engineer", "Embedded Engineer", "Hardware Engineer", "RF Engineer", "Signal Processing Engineer"]
    },
    "Mechanical": {
        "coding_required": False,
        "technical_skills": ["AutoCAD", "CATIA", "SolidWorks", "ANSYS", "Finite Element Analysis", "Thermodynamics", "Fluid Mechanics", "Manufacturing Processes"],
        "tools": ["SolidWorks", "CATIA", "ANSYS", "AutoCAD", "MATLAB", "3D Printer", "CNC Machines"],
        "companies": ["TATA Motors", "Mahindra", "Bosch", "Schneider Electric", "Siemens", "General Electric", "John Deere"],
        "career_paths": ["Design Engineer", "Production Engineer", "Quality Engineer", "R&D Engineer", "Project Manager"]
    },
    "Civil": {
        "coding_required": False,
        "technical_skills": ["AutoCAD Civil", "STAAD Pro", "ETABS", "Primavera", "Construction Management", "Structural Analysis", "Surveying"],
        "tools": ["AutoCAD Civil 3D", "STAAD Pro", "ETABS", "Primavera P6", "MS Project", "ArcGIS"],
        "companies": ["L&T", "Shapoorji Pallonji", "GMR", "DLF", "Jacobs", "AECOM"],
        "career_paths": ["Structural Engineer", "Site Engineer", "Planning Engineer", "Quantity Surveyor", "Project Coordinator"]
    },
    "EEE": {
        "coding_required": False,
        "technical_skills": ["Power Systems", "Control Systems", "Electrical Machines", "Renewable Energy", "PLC Programming", "SCADA"],
        "tools": ["MATLAB Simulink", "ETAP", "LabVIEW", "AutoCAD Electrical", "PowerWorld"],
        "companies": ["Siemens", "ABB", "Schneider Electric", "BHEL", "NTPC", "Power Grid Corporation"],
        "career_paths": ["Power Systems Engineer", "Control Engineer", "Electrical Design Engineer", "Field Service Engineer"]
    },
    "Other": {
        "coding_required": False,
        "technical_skills": ["MS Office", "Communication", "Project Management", "Analytical Skills"],
        "tools": ["MS Office Suite", "Google Workspace", "Project Management Tools"],
        "companies": ["Various MNCs", "Startups", "Government Sector", "Public Sector Units"],
        "career_paths": ["Management Trainee", "Business Analyst", "Operations Executive", "Administrative Roles"]
    }
}

COMPANY_TYPES = ["MNC", "Startup", "Government", "Public Sector", "Mid-size Company"]
CERTIFICATION_LEVELS = ["Beginner", "Intermediate", "Advanced", "Professional"]

# =========================
# SIMPLIFIED PDF GENERATION FUNCTION (FIXED ENCODING)
# =========================
def generate_prediction_pdf(student, readiness, probability, status, company_suggestions, career_insights, branch_info):
    pdf = FPDF()
    pdf.add_page()
   
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "PlaceMate Pro - Placement Prediction Report", 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Official Placement Readiness Analysis", 0, 1, "C")
    pdf.ln(10)
   
    # Date
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "R")
    pdf.ln(5)
   
    # Student Information
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Student Information", 0, 1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(40, 10, "Student ID:", 0, 0)
    pdf.cell(0, 10, student.get('student_id', 'N/A'), 0, 1)
    pdf.cell(40, 10, "Student Name:", 0, 0)
    pdf.cell(0, 10, student.get('student_name', 'N/A'), 0, 1)
    pdf.cell(40, 10, "Branch:", 0, 0)
    pdf.cell(0, 10, student.get('branch', 'N/A'), 0, 1)
    pdf.cell(40, 10, "CGPA:", 0, 0)
    pdf.cell(0, 10, str(student.get('cgpa', 'N/A')), 0, 1)
    pdf.ln(5)
   
    # Skills Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Skills & Qualifications", 0, 1)
    pdf.set_font("Arial", "", 12)
   
    # Technical Skills
    tech_skills = student.get('technical_skills', '').split(',')
    pdf.cell(0, 10, "Technical Skills:", 0, 1)
    pdf.set_font("Arial", "", 11)
    for skill in tech_skills[:6]:
        if skill.strip():
            pdf.cell(10, 7, "", 0, 0)
            pdf.cell(0, 7, f"- {skill.strip()}", 0, 1)
   
    # Tools Known
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Tools Known:", 0, 1)
    pdf.set_font("Arial", "", 11)
    tools = student.get('tools_known', '').split(',')
    for tool in tools[:6]:
        if tool.strip():
            pdf.cell(10, 7, "", 0, 0)
            pdf.cell(0, 7, f"- {tool.strip()}", 0, 1)
   
    # Core Skills
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Core Skills:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(10, 7, "", 0, 0)
    pdf.cell(0, 7, f"Coding Skill: {student.get('coding_skill', 0)}/10", 0, 1)
    pdf.cell(10, 7, "", 0, 0)
    pdf.cell(0, 7, f"Communication: {student.get('communication_skill', 0)}/10", 0, 1)
    pdf.cell(10, 7, "", 0, 0)
    pdf.cell(0, 7, f"Problem Solving: {student.get('problem_solving', 0)}/10", 0, 1)
    pdf.cell(10, 7, "", 0, 0)
    pdf.cell(0, 7, f"Projects: {student.get('projects_count', 0)}", 0, 1)
    pdf.cell(10, 7, "", 0, 0)
    pdf.cell(0, 7, f"Internships: {student.get('internship_count', 0)}", 0, 1)
    pdf.ln(10)
   
    # Placement Prediction Results
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Placement Prediction Results", 0, 1, "C")
    pdf.ln(5)
   
    # Status
    pdf.set_font("Arial", "B", 14)
    if "PLACED" in status:
        pdf.set_text_color(0, 128, 0)  # Green
    else:
        pdf.set_text_color(255, 0, 0)  # Red
    pdf.cell(0, 10, f"Status: {status}", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)  # Reset to black
   
    # Scores
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Readiness Score: {readiness}/100", 0, 1, "C")
    pdf.cell(0, 10, f"Placement Probability: {probability:.0%}", 0, 1, "C")
    pdf.ln(10)
   
    # Company Suggestions
    if company_suggestions:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Recommended Companies", 0, 1)
        pdf.set_font("Arial", "", 11)
        for i, company in enumerate(company_suggestions[:6], 1):
            pdf.cell(10, 7, "", 0, 0)
            pdf.cell(0, 7, f"{i}. {company}", 0, 1)
        pdf.ln(5)
   
    # Career Insights
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Career Insights & Recommendations", 0, 1)
    pdf.set_font("Arial", "", 11)
    insights = career_insights.split(' | ')
    for insight in insights:
        pdf.multi_cell(0, 7, f"- {insight}")
    pdf.ln(5)
   
    # Career Paths
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Career Paths for {student.get('branch', 'Your')} Branch", 0, 1)
    pdf.set_font("Arial", "", 11)
    for path in branch_info['career_paths'][:5]:
        pdf.cell(10, 7, "", 0, 0)
        pdf.cell(0, 7, f"> {path}", 0, 1)
   
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 7, "Note: This report is generated based on your current profile data. Regularly update your skills and achievements for better predictions.")
   
    # Return PDF as bytes - FIXED ENCODING ISSUE
    try:
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except:
        return pdf.output(dest='S').encode('utf-8')

def create_download_link(pdf_bytes, filename):
    """Create a download link for the PDF"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'''
    <div style="text-align: center; margin: 20px 0;">
        <a href="data:application/pdf;base64,{b64}" download="{filename}"
           style="background-color: #4CAF50; color: white; padding: 12px 24px;
                  text-align: center; text-decoration: none; display: inline-block;
                  border-radius: 5px; font-weight: bold; font-size: 16px;">
           📥 Download Prediction Report (PDF)
        </a>
    </div>
    '''
    return href

# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if students table exists and has the correct structure
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    students_table_exists = cur.fetchone() is not None
   
    if students_table_exists:
        # Check if table has the new columns
        cur.execute("PRAGMA table_info(students)")
        columns = cur.fetchall()
        column_names = [col[1] for col in columns]
       
        # Add missing columns if needed
        if 'internship_type' not in column_names:
            cur.execute("ALTER TABLE students ADD COLUMN internship_type TEXT")
        if 'certifications_count' not in column_names:
            cur.execute("ALTER TABLE students ADD COLUMN certifications_count INTEGER")
        if 'certification_level' not in column_names:
            cur.execute("ALTER TABLE students ADD COLUMN certification_level TEXT")
        if 'created_at' not in column_names:
            cur.execute("ALTER TABLE students ADD COLUMN created_at TEXT")
    else:
        # Create students table with ALL fields (16 columns)
        cur.execute("""
        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT,
            branch TEXT,
            cgpa REAL,
            coding_skill INTEGER,
            communication_skill INTEGER,
            aptitude_skill INTEGER,
            problem_solving INTEGER,
            projects_count INTEGER,
            internship_count INTEGER,
            internship_type TEXT,
            certifications_count INTEGER,
            certification_level TEXT,
            technical_skills TEXT,
            tools_known TEXT,
            created_at TEXT
        )
        """)

    # Check if predictions table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
    predictions_table_exists = cur.fetchone() is not None
   
    if not predictions_table_exists:
        # Create predictions table with insights
        cur.execute("""
        CREATE TABLE predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            branch TEXT,
            status TEXT,
            probability REAL,
            readiness_score INTEGER,
            company_suggestions TEXT,
            career_insights TEXT,
            created_at TEXT
        )
        """)

    conn.commit()
    conn.close()

# Initialize database once
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# =========================
# ENHANCED PLACEMENT LOGIC - CORRECTED VERSION
# =========================
def calculate_results(student):
    branch = student["branch"]
    config = BRANCH_CONFIG[branch]

    tech_skills = [s.strip() for s in str(student["technical_skills"]).split(",") if s.strip()]
    tools = [t.strip() for t in str(student["tools_known"]).split(",") if t.strip()]

    # Initialize all return variables
    readiness = 0
    probability = 0
    status_display = ""
    company_suggestions = []
    insights = ""
    status = ""

    # ❌ HARD ELIGIBILITY RULES
    if student["cgpa"] < 6:
        status_display = "NOT PLACED ❌"
        status = "NOT PLACED"
        insights = "CGPA below 6.0 is not eligible for placements"
        return readiness, probability, status_display, company_suggestions, insights, status

    if config["coding_required"] and student["coding_skill"] < 4:
        status_display = "NOT PLACED ❌"
        status = "NOT PLACED"
        insights = f"Coding skill below 4 for {branch} branch"
        return readiness, probability, status_display, company_suggestions, insights, status

    if student["communication_skill"] < 4:
        status_display = "NOT PLACED ❌"
        status = "NOT PLACED"
        insights = "Communication skill below 4"
        return readiness, probability, status_display, company_suggestions, insights, status

    if len(tech_skills) == 0 or len(tools) == 0:
        status_display = "NOT PLACED ❌"
        status = "NOT PLACED"
        insights = "Technical skills or tools knowledge missing"
        return readiness, probability, status_display, company_suggestions, insights, status

    # ✅ SCORE CALCULATION WITH ENHANCED FACTORS
    score = (
        student["cgpa"] * 10 +
        student["communication_skill"] * 5 +
        student["aptitude_skill"] * 5 +
        student["problem_solving"] * 5 +
        student["projects_count"] * 3 +
        student["internship_count"] * 5 +
        student.get("certifications_count", 0) * 4 +
        len(tech_skills) * 3 +
        len(tools) * 2
    )

    # Bonus for internship type
    internship_type = student.get("internship_type", "None")
    if internship_type == "MNC":
        score += 10
    elif internship_type == "Startup":
        score += 7
    elif internship_type == "Government":
        score += 5
    elif internship_type == "Public Sector":
        score += 4
    elif internship_type == "Mid-size Company":
        score += 3

    # Bonus for certification level
    cert_level = student.get("certification_level", "None")
    if cert_level == "Professional":
        score += 8
    elif cert_level == "Advanced":
        score += 5
    elif cert_level == "Intermediate":
        score += 3

    if config["coding_required"]:
        score += student["coding_skill"] * 5

    readiness = min(score, 100)
    probability = round(readiness / 100, 2)
   
    # Determine placement status (remove emojis for PDF)
    if readiness >= 75:
        status = "HIGHLY PLACED"
        status_display = "HIGHLY PLACED ✅"
    elif readiness >= 60:
        status = "PLACED"
        status_display = "PLACED ✅"
    else:
        status = "NOT PLACED"
        status_display = "NOT PLACED ❌"

    # Generate company suggestions based on readiness
    if readiness >= 80:
        company_suggestions = config["companies"][:4]  # Top companies
    elif readiness >= 65:
        company_suggestions = config["companies"][4:8]  # Mid-level companies
    elif readiness >= 50:
        company_suggestions = config["companies"][8:]  # Entry-level companies

    # Generate career insights
    insights = generate_career_insights(student, readiness)
   
    return readiness, probability, status_display, company_suggestions, insights, status

def generate_career_insights(student, readiness):
    insights = []
   
    if student["cgpa"] >= 8.5:
        insights.append("Excellent academic record - can target core companies")
    elif student["cgpa"] >= 7.5:
        insights.append("Good academic performance - maintain current standards")
    else:
        insights.append("Consider improving CGPA for better opportunities")
   
    internship_count = student.get("internship_count", 0)
    if internship_count >= 2:
        insights.append("Good internship experience - highlight in interviews")
    elif internship_count == 1:
        insights.append("Consider one more internship for better exposure")
    else:
        insights.append("Look for internship opportunities to gain practical experience")
   
    if student["projects_count"] >= 3:
        insights.append("Strong project portfolio - showcase during placements")
    else:
        insights.append("Add more projects to your portfolio")
   
    cert_count = student.get("certifications_count", 0)
    if cert_count >= 2:
        insights.append("Certifications add value to your profile")
    else:
        insights.append("Consider getting industry-recognized certifications")
   
    if readiness >= 80:
        insights.append("You can target product-based companies and MNCs")
    elif readiness >= 65:
        insights.append("Focus on service-based companies and startups")
   
    return " | ".join(insights)

# =========================
# DATABASE FUNCTIONS
# =========================
def get_students():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM students", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def get_predictions():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM predictions ORDER BY created_at DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def save_student(student):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        student_values = (
            student["student_id"],
            student["student_name"],
            student["branch"],
            student["cgpa"],
            student["coding_skill"],
            student["communication_skill"],
            student["aptitude_skill"],
            student["problem_solving"],
            student["projects_count"],
            student["internship_count"],
            student.get("internship_type", "None"),
            student.get("certifications_count", 0),
            student.get("certification_level", "None"),
            student["technical_skills"],
            student["tools_known"],
            student.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
       
        cur.execute("""
        INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, student_values)
        conn.commit()
        st.success(f"✅ Student {student['student_name']} registered successfully!")
       
    except sqlite3.Error as e:
        st.error(f"❌ Database error: {e}")
    finally:
        conn.close()

def save_prediction(student, status, probability, readiness, company_suggestions, career_insights):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO predictions (student_id, student_name, branch, status, probability,
                                readiness_score, company_suggestions, career_insights, created_at)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            student["student_id"],
            student["student_name"],
            student["branch"],
            status,
            probability,
            readiness,
            ", ".join(company_suggestions) if company_suggestions else "None",
            career_insights,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        st.success("✅ Prediction saved successfully!")
    except sqlite3.Error as e:
        st.error(f"❌ Database error: {e}")
    finally:
        conn.close()

# =========================
# CHATBOT CONFIGURATION
# =========================
class PlacementChatbot:
    def __init__(self):
        self.knowledge_base = {
            "placement": {
                "questions": [
                    "What is placement?",
                    "How to prepare for placements?",
                    "What companies visit our campus?",
                    "Placement process?"
                ],
                "responses": [
                    "Placement is the process where companies recruit students from colleges for employment opportunities.",
                    """To prepare for placements:
                    1. Build a strong resume
                    2. Practice coding regularly
                    3. Work on communication skills
                    4. Prepare for aptitude tests
                    5. Do mock interviews""",
                    "Top companies include Google, Microsoft, Amazon, TCS, Infosys, Wipro, and many MNCs based on your branch.",
                    "Placement process: Registration → Resume Submission → Aptitude Test → Technical Interview → HR Interview → Job Offer"
                ]
            },
            "resume": {
                "questions": [
                    "How to make a good resume?",
                    "Resume format?",
                    "What to include in resume?"
                ],
                "responses": [
                    """A good resume should be:
                    • 1-2 pages maximum
                    • Clean and professional format
                    • Include relevant skills
                    • Highlight projects and achievements
                    • Quantify your accomplishments""",
                    "Use reverse chronological format. Include: Contact Info, Education, Skills, Projects, Internships, Certifications, Achievements.",
                    "Include: Personal details, Education, Technical Skills, Projects, Internships, Certifications, Extra-curricular activities, References (optional)."
                ]
            },
            "interview": {
                "questions": [
                    "Interview preparation?",
                    "Common interview questions?",
                    "Technical interview tips?"
                ],
                "responses": [
                    """Interview preparation:
                    1. Research the company
                    2. Practice common questions
                    3. Prepare your introduction
                    4. Review your projects
                    5. Dress professionally""",
                    """Common questions:
                    • Tell me about yourself
                    • Why should we hire you?
                    • What are your strengths/weaknesses?
                    • Where do you see yourself in 5 years?
                    • Why do you want to work here?""",
                    """Technical interview tips:
                    1. Practice coding on platforms like LeetCode
                    2. Understand time and space complexity
                    3. Explain your thought process
                    4. Ask clarifying questions
                    5. Test your solution with examples"""
                ]
            },
            "skills": {
                "questions": [
                    "What skills are important?",
                    "How to improve coding skills?",
                    "Soft skills required?"
                ],
                "responses": [
                    """Important skills:
                    • Technical: Programming, Tools, Domain knowledge
                    • Soft: Communication, Teamwork, Problem-solving
                    • Aptitude: Quantitative, Logical, Verbal""",
                    """To improve coding:
                    1. Practice daily on platforms
                    2. Build projects
                    3. Learn data structures
                    4. Participate in contests
                    5. Read other's code""",
                    """Essential soft skills:
                    • Communication (written & verbal)
                    • Team collaboration
                    • Time management
                    • Adaptability
                    • Leadership"""
                ]
            },
            "cgpa": {
                "questions": [
                    "Is CGPA important?",
                    "Minimum CGPA requirement?",
                    "Low CGPA tips?"
                ],
                "responses": [
                    "CGPA is important as many companies have eligibility criteria, but skills and projects also matter significantly.",
                    "Most companies require minimum 6.0 CGPA, top companies may require 7.5+ CGPA.",
                    """With low CGPA:
                    1. Focus on building strong skills
                    2. Create impressive projects
                    3. Get certifications
                    4. Do internships
                    5. Network effectively"""
                ]
            }
        }
       
        self.greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening"
        ]
       
        self.farewells = [
            "bye", "goodbye", "see you", "thanks", "thank you"
        ]
   
    def get_response(self, user_input):
        user_input = user_input.lower().strip()
       
        # Check for greetings
        if any(greet in user_input for greet in self.greetings):
            return "Hello! I'm your Placement Assistant. How can I help you today? You can ask about placements, resume, interviews, skills, or CGPA."
       
        # Check for farewells
        if any(farewell in user_input for farewell in self.farewells):
            return "You're welcome! Best of luck with your placements. Feel free to ask if you have more questions!"
       
        # Check knowledge base
        for category, data in self.knowledge_base.items():
            for question in data["questions"]:
                if any(keyword in user_input for keyword in question.lower().split()):
                    index = data["questions"].index(question)
                    return data["responses"][index]
       
        # Check for specific keywords
        if "placement" in user_input:
            return self.knowledge_base["placement"]["responses"][0]
        elif "resume" in user_input or "cv" in user_input:
            return self.knowledge_base["resume"]["responses"][0]
        elif "interview" in user_input:
            return self.knowledge_base["interview"]["responses"][0]
        elif "skill" in user_input:
            return self.knowledge_base["skills"]["responses"][0]
        elif "cgpa" in user_input or "grade" in user_input:
            return self.knowledge_base["cgpa"]["responses"][0]
        elif "company" in user_input:
            return "Top recruiting companies vary by branch. For CSE: Google, Microsoft, Amazon. For ECE: Intel, Qualcomm. For Mechanical: TATA, Bosch. For Civil: L&T, GMR. Check the dashboard for more details."
        elif "salary" in user_input or "package" in user_input:
            return "Average packages vary: MNCs (8-20 LPA), Service-based (3-6 LPA), Startups (5-12 LPA). Depends on skills, location, and role."
       
        # Default response
        suggestions = [
            "placement preparation", "resume building", "interview tips",
            "skill development", "CGPA importance"
        ]
        return f"I'm not sure about that. You can ask about: {', '.join(suggestions)}. Or try rephrasing your question."

# Initialize chatbot
chatbot = PlacementChatbot()

# =========================
# ENHANCED DASHBOARD FUNCTIONS
# =========================
def create_dashboard_metrics(students_df, predictions_df):
    """Create comprehensive dashboard metrics"""
   
    col1, col2, col3, col4 = st.columns(4)
   
    with col1:
        total_students = len(students_df)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #4F46E5; margin-bottom: 0.5rem;">👥 Total Students</h3>
            <h1 style="font-size: 2.5rem; color: #1F2937; margin: 0;">{total_students}</h1>
            <p style="color: #6B7280; margin-top: 0.5rem;">Registered in system</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        placed_count = len(predictions_df[predictions_df['status'].str.contains('PLACED', case=False)]) if not predictions_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #10B981; margin-bottom: 0.5rem;">✅ Placed Students</h3>
            <h1 style="font-size: 2.5rem; color: #1F2937; margin: 0;">{placed_count}</h1>
            <p style="color: #6B7280; margin-top: 0.5rem;">Based on predictions</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col3:
        avg_cgpa = students_df['cgpa'].mean() if not students_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #F59E0B; margin-bottom: 0.5rem;">📊 Average CGPA</h3>
            <h1 style="font-size: 2.5rem; color: #1F2937; margin: 0;">{avg_cgpa:.2f}</h1>
            <p style="color: #6B7280; margin-top: 0.5rem;">Across all students</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col4:
        top_branch = students_df['branch'].mode()[0] if not students_df.empty and not students_df['branch'].mode().empty else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #EF4444; margin-bottom: 0.5rem;">🏆 Top Branch</h3>
            <h1 style="font-size: 2.5rem; color: #1F2937; margin: 0;">{top_branch}</h1>
            <p style="color: #6B7280; margin-top: 0.5rem;">Most registrations</p>
        </div>
        """, unsafe_allow_html=True)

def create_charts(students_df, predictions_df):
    """Create interactive charts for dashboard"""
   
    if students_df.empty:
        return
   
    # Create tabs for different charts
    tab1, tab2, tab3 = st.tabs(["📈 Branch Distribution", "📊 CGPA Analysis", "🎯 Placement Status"])
   
    with tab1:
        # Branch distribution pie chart
        branch_counts = students_df['branch'].value_counts()
        fig1 = px.pie(
            values=branch_counts.values,
            names=branch_counts.index,
            title="Student Distribution by Branch",
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
   
    with tab2:
        # CGPA distribution histogram
        fig2 = px.histogram(
            students_df,
            x='cgpa',
            title="CGPA Distribution",
            nbins=20,
            color_discrete_sequence=['#4F46E5']
        )
        fig2.update_layout(
            xaxis_title="CGPA",
            yaxis_title="Number of Students",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
       
        # CGPA statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Highest CGPA", f"{students_df['cgpa'].max():.2f}")
        with col2:
            st.metric("Lowest CGPA", f"{students_df['cgpa'].min():.2f}")
        with col3:
            st.metric("Median CGPA", f"{students_df['cgpa'].median():.2f}")
   
    with tab3:
        if not predictions_df.empty and 'status' in predictions_df.columns:
            # Placement status chart
            status_counts = predictions_df['status'].value_counts()
            colors = ['#10B981' if 'PLACED' in str(status) else '#EF4444' for status in status_counts.index]
           
            fig3 = go.Figure(data=[
                go.Bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    marker_color=colors,
                    text=status_counts.values,
                    textposition='auto',
                )
            ])
           
            fig3.update_layout(
                title="Placement Status Distribution",
                xaxis_title="Status",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)

def create_skill_analysis(students_df):
    """Analyze and visualize skills distribution"""
    if students_df.empty:
        return
   
    st.markdown('<h3 class="sub-header">🔧 Skills Analysis</h3>', unsafe_allow_html=True)
   
    # Extract skills from all students
    all_skills = []
    if 'technical_skills' in students_df.columns:
        for skills in students_df['technical_skills'].dropna():
            skill_list = [skill.strip() for skill in str(skills).split(',')]
            all_skills.extend(skill_list)
   
    # Get top 10 skills
    if all_skills:
        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(10)
       
        # Create horizontal bar chart
        skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
        fig = px.bar(
            skills_df,
            y='Skill',
            x='Count',
            orientation='h',
            title="Top 10 Technical Skills",
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# ENHANCED SIDEBAR WITH ICONS
# =========================
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h1 style="color: white; font-size: 1.8rem; margin-bottom: 0.5rem;">🎓 PlaceMate Pro</h1>
    <p style="color: rgba(255, 255, 255, 0.8); font-size: 0.9rem;">AI-Powered Placement Prediction System</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📝 Student Registration", "🎯 Placement Prediction", "💬 Chat Assistant", "👨‍🏫 Faculty Login"]
)

# =========================
# CHATBOT INTERFACE - SIMPLIFIED FIXED VERSION
# =========================
def chatbot_interface():
    st.markdown('<h2 class="main-header">💬 Placement Chat Assistant</h2>', unsafe_allow_html=True)
   
    col1, col2 = st.columns([2, 1])
   
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
            <h3 style="color: white; margin-bottom: 1rem;">🤖 How can I help you?</h3>
            <p>I can assist you with:</p>
            <ul>
                <li>Placement preparation tips</li>
                <li>Resume building guidance</li>
                <li>Interview preparation</li>
                <li>Skill development</li>
                <li>CGPA and eligibility queries</li>
                <li>Company information</li>
            </ul>
            <p style="margin-top: 1rem;">Try asking: <em>"How to prepare for placements?"</em> or <em>"What skills are important?"</em></p>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h4 style="color: #4F46E5;">Quick Questions</h4>
            <ul style="color: #6B7280; padding-left: 1.2rem;">
                <li>Placement process?</li>
                <li>Resume format?</li>
                <li>Interview tips?</li>
                <li>CGPA importance?</li>
                <li>Top companies?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
   
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
   
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
   
    # Display chat history
    for message in st.session_state.chat_history:
        if message['sender'] == 'user':
            st.markdown(f'<div class="user-message">{message["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["text"]}</div>', unsafe_allow_html=True)
   
    st.markdown('</div>', unsafe_allow_html=True)
   
    # Quick action buttons - SIMPLIFIED APPROACH
    st.markdown("### Quick Actions")
    quick_cols = st.columns(4)
    quick_questions = [
        "How to prepare for placements?",
        "Resume format tips?",
        "Common interview questions?",
        "Is CGPA important?"
    ]
   
    # Use a callback approach instead of rerun
    for idx, question in enumerate(quick_questions):
        if quick_cols[idx].button(question, key=f"quick_{idx}"):
            response = chatbot.get_response(question)
            st.session_state.chat_history.append({'sender': 'user', 'text': question})
            st.session_state.chat_history.append({'sender': 'bot', 'text': response})
   
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your question:", placeholder="Ask me about placements...", key="chat_input")
    with col2:
        send_button = st.button("Send", use_container_width=True, key="send_button")
   
    # Process user input
    if send_button and user_input.strip():
        response = chatbot.get_response(user_input)
        st.session_state.chat_history.append({'sender': 'user', 'text': user_input})
        st.session_state.chat_history.append({'sender': 'bot', 'text': response})
        # Clear the input field by using a session state trick
        if 'chat_input_clear' not in st.session_state:
            st.session_state.chat_input_clear = True
        else:
            st.session_state.chat_input_clear = not st.session_state.chat_input_clear
   
    # Clear chat button
    if st.button("Clear Chat History", type="secondary", key="clear_chat"):
        st.session_state.chat_history = []

# =========================
# ENHANCED DASHBOARD PAGE
# =========================
if menu == "🏠 Dashboard":
    st.markdown('<h1 class="main-header">📊 Placement Dashboard</h1>', unsafe_allow_html=True)
   
    # Get data
    students_df = get_students()
    predictions_df = get_predictions()
   
    # Create metrics cards
    create_dashboard_metrics(students_df, predictions_df)
   
    st.markdown("---")
   
    # Charts section
    st.markdown('<h3 class="sub-header">📈 Analytics Overview</h3>', unsafe_allow_html=True)
    create_charts(students_df, predictions_df)
   
    # Skills analysis
    create_skill_analysis(students_df)
   
    st.markdown("---")
   
    # Recent Activity Section
    st.markdown('<h3 class="sub-header">🔄 Recent Activity</h3>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
   
    with col1:
        # Recent Students
        st.markdown("##### Recent Registrations")
        if not students_df.empty:
            recent_students = students_df.sort_values('created_at', ascending=False).head(5)
            for _, student in recent_students.iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #4F46E5;">
                    <strong>{student['student_name']}</strong> ({student['student_id']})<br>
                    <small>{student['branch']} • CGPA: {student['cgpa']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent registrations")
   
    with col2:
        # Recent Predictions
        st.markdown("##### Recent Predictions")
        if not predictions_df.empty:
            recent_pred = predictions_df.head(5)
            for _, pred in recent_pred.iterrows():
                status_color = "#10B981" if "PLACED" in str(pred['status']) else "#EF4444"
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {status_color};">
                    <strong>{pred['student_name']}</strong><br>
                    <small>Status: <span style="color: {status_color};">{pred['status']}</span> • Probability: {pred['probability']:.0%}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No predictions yet")
   
    # Branch-wise insights
    st.markdown("---")
    st.markdown('<h3 class="sub-header">🎯 Branch-wise Insights</h3>', unsafe_allow_html=True)
   
    if not students_df.empty:
        branch_tabs = st.tabs(list(BRANCH_CONFIG.keys()))
       
        for i, (branch, config) in enumerate(BRANCH_CONFIG.items()):
            with branch_tabs[i]:
                branch_students = students_df[students_df['branch'] == branch]
               
                if not branch_students.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"{branch} Students", len(branch_students))
                    with col2:
                        st.metric("Avg CGPA", f"{branch_students['cgpa'].mean():.2f}")
                    with col3:
                        st.metric("Top Skill", config['technical_skills'][0])
                   
                    st.markdown("**Top Companies:**")
                    company_cols = st.columns(4)
                    for idx, company in enumerate(config['companies'][:4]):
                        with company_cols[idx]:
                            st.info(company)
                else:
                    st.info(f"No {branch} students registered yet")

# =========================
# ENHANCED STUDENT REGISTRATION PAGE
# =========================
elif menu == "📝 Student Registration":
    st.markdown('<h1 class="main-header">📝 Student Registration</h1>', unsafe_allow_html=True)
   
    # Show statistics
    students_df = get_students()
    total_students = len(students_df)
   
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registered", total_students)
    with col2:
        st.metric("Today's Date", datetime.now().strftime("%d %b %Y"))
    with col3:
        if not students_df.empty:
            st.metric("Latest ID", students_df['student_id'].iloc[-1])
        else:
            st.metric("Latest ID", "N/A")
   
    # Registration form in a card-like container
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-top: 2rem;">
    """, unsafe_allow_html=True)
   
    with st.form("registration_form"):
        st.markdown("### 🎓 Student Information")
       
        col1, col2 = st.columns(2)
       
        with col1:
            student_id = st.text_input("Student ID*", placeholder="Enter unique student ID")
            name = st.text_input("Full Name*", placeholder="Enter student's full name")
            branch = st.selectbox("Branch*", list(BRANCH_CONFIG.keys()))
            cgpa = st.number_input("CGPA*", 0.0, 10.0, 7.0, step=0.1,
                                   help="Enter CGPA out of 10")
           
            # Coding skill with conditional display
            if branch and BRANCH_CONFIG[branch]["coding_required"]:
                coding = st.slider("Coding Skill (1-10)*", 1, 10, 5,
                                   help="Rate your coding proficiency")
            else:
                st.info("💡 Coding skill not required for this branch")
                coding = 0
           
            projects = st.number_input("Projects Count*", 0, 20, 1,
                                       help="Number of academic/personal projects")
            internships = st.number_input("Internships Count*", 0, 10, 0,
                                          help="Number of internships completed")
           
        with col2:
            comm = st.slider("Communication Skill (1-10)*", 1, 10, 5)
            aptitude = st.slider("Aptitude Skill (1-10)*", 1, 10, 5)
            problem = st.slider("Problem Solving (1-10)*", 1, 10, 5)
           
            internship_type = st.selectbox("Internship Type",
                                          ["Select"] + COMPANY_TYPES,
                                          help="Type of company for your internship")
            certifications = st.number_input("Certifications Count", 0, 10, 0)
            certification_level = st.selectbox("Highest Certification Level",
                                              ["Select"] + CERTIFICATION_LEVELS)
           
            # Dynamic skills based on branch
            if branch:
                tech_skills = BRANCH_CONFIG[branch]["technical_skills"]
                selected_tech = st.multiselect("Technical Skills*", tech_skills,
                                              default=tech_skills[:2],
                                              help="Select relevant technical skills")
                tech_input = st.text_input("Add custom technical skills (comma separated)")
               
                tools = BRANCH_CONFIG[branch]["tools"]
                selected_tools = st.multiselect("Tools Known*", tools,
                                               default=tools[:2],
                                               help="Select tools you're familiar with")
                tools_input = st.text_input("Add custom tools (comma separated)")
       
        # Form submission
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Register Student", use_container_width=True)
       
        if submitted:
            # Validation and registration logic (same as before)
            if not student_id or not name:
                st.error("⚠️ Please fill in required fields (marked with *)")
            else:
                # Combine skills
                final_tech = list(selected_tech)
                if tech_input:
                    final_tech.extend([s.strip() for s in tech_input.split(",") if s.strip()])
               
                final_tools = list(selected_tools)
                if tools_input:
                    final_tools.extend([t.strip() for t in tools_input.split(",") if t.strip()])
               
                student = {
                    "student_id": student_id,
                    "student_name": name,
                    "branch": branch,
                    "cgpa": cgpa,
                    "coding_skill": coding,
                    "communication_skill": comm,
                    "aptitude_skill": aptitude,
                    "problem_solving": problem,
                    "projects_count": projects,
                    "internship_count": internships,
                    "internship_type": internship_type if internship_type != "Select" else "None",
                    "certifications_count": certifications,
                    "certification_level": certification_level if certification_level != "Select" else "None",
                    "technical_skills": ", ".join(final_tech),
                    "tools_known": ", ".join(final_tools),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
               
                save_student(student)
               
                # Show success animation
                st.balloons()
                st.success(f"✅ Student **{name}** registered successfully!")
   
    st.markdown("</div>", unsafe_allow_html=True)
   
    # Show registered students in a nice table
    st.markdown("---")
    st.markdown('<h3 class="sub-header">📋 Registered Students</h3>', unsafe_allow_html=True)
   
    if not students_df.empty:
        # Use columns for better display
        display_df = students_df[['student_id', 'student_name', 'branch', 'cgpa', 'created_at']]
        st.dataframe(
            display_df.style
            .background_gradient(subset=['cgpa'], cmap='YlOrRd')
            .set_properties(**{'text-align': 'left'})
        )
    else:
        st.info("📭 No students registered yet. Use the form above to add students.")

# =========================
# ENHANCED PLACEMENT PREDICTION PAGE
# =========================
elif menu == "🎯 Placement Prediction":
    st.markdown('<h1 class="main-header">🎯 Placement Prediction</h1>', unsafe_allow_html=True)
   
    students = get_students()
   
    if students.empty:
        st.warning("""
        <div style="background: #FEF3C7; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #F59E0B;">
            <h4 style="color: #92400E; margin: 0;">⚠️ No Students Found</h4>
            <p style="color: #92400E; margin: 0.5rem 0 0 0;">
                Please register students first in the <strong>Student Registration</strong> section.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Student selection with search
        selected_name = st.selectbox("👤 Select Student", students["student_name"].tolist())
       
        if selected_name:
            student_data = students[students["student_name"] == selected_name]
            if not student_data.empty:
                student = student_data.iloc[0].to_dict()
               
                # Display student profile in cards
                st.markdown('<h3 class="sub-header">📋 Student Profile</h3>', unsafe_allow_html=True)
               
                # Profile cards in 3 columns
                col1, col2, col3 = st.columns(3)
               
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #6B7280;">🎓 Basic Info</h4>
                        <p><strong>ID:</strong> {student['student_id']}</p>
                        <p><strong>Name:</strong> {student['student_name']}</p>
                        <p><strong>Branch:</strong> {student['branch']}</p>
                        <p><strong>CGPA:</strong> {student['cgpa']}</p>
                    </div>
                    """, unsafe_allow_html=True)
               
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #6B7280;">📊 Experience</h4>
                        <p><strong>Projects:</strong> {student['projects_count']}</p>
                        <p><strong>Internships:</strong> {student['internship_count']}</p>
                        <p><strong>Intern Type:</strong> {student.get('internship_type', 'None')}</p>
                        <p><strong>Certifications:</strong> {student.get('certifications_count', 0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
               
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #6B7280;">💪 Skills Rating</h4>
                        <p><strong>Coding:</strong> {student['coding_skill']}/10</p>
                        <p><strong>Communication:</strong> {student['communication_skill']}/10</p>
                        <p><strong>Aptitude:</strong> {student['aptitude_skill']}/10</p>
                        <p><strong>Problem Solving:</strong> {student['problem_solving']}/10</p>
                    </div>
                    """, unsafe_allow_html=True)
               
                # Skills display
                st.markdown('<h4 style="margin-top: 2rem;">🔧 Skills & Tools</h4>', unsafe_allow_html=True)
               
                skill_col1, skill_col2 = st.columns(2)
                with skill_col1:
                    tech_skills = [s.strip() for s in str(student["technical_skills"]).split(",") if s.strip()]
                    if tech_skills:
                        st.markdown("**Technical Skills:**")
                        for skill in tech_skills[:5]:
                            st.markdown(f"• {skill}")
                        if len(tech_skills) > 5:
                            with st.expander(f"Show all {len(tech_skills)} skills"):
                                for skill in tech_skills[5:]:
                                    st.markdown(f"• {skill}")
               
                with skill_col2:
                    tools = [t.strip() for t in str(student["tools_known"]).split(",") if t.strip()]
                    if tools:
                        st.markdown("**Tools Known:**")
                        for tool in tools[:5]:
                            st.markdown(f"• {tool}")
                        if len(tools) > 5:
                            with st.expander(f"Show all {len(tools)} tools"):
                                for tool in tools[5:]:
                                    st.markdown(f"• {tool}")
               
                # Prediction button
                st.markdown("---")
                predict_col1, predict_col2, predict_col3 = st.columns([1, 2, 1])
                with predict_col2:
                    if st.button("🔮 Generate Placement Prediction", use_container_width=True, type="primary"):
                        with st.spinner("🤖 Analyzing profile and generating insights..."):
                            # Your existing prediction logic here
                            readiness, probability, status_display, company_suggestions, career_insights, status = calculate_results(student)
                           
                            # Save prediction
                            save_prediction(student, status_display, probability, readiness, company_suggestions, career_insights)
                           
                            # Display results with enhanced styling
                            st.markdown("---")
                           
                            # Results header
                            st.markdown('<h2 class="main-header" style="font-size: 2rem;">📊 Prediction Results</h2>', unsafe_allow_html=True)
                           
                            # Status card
                            if "PLACED" in status_display:
                                status_color = "#10B981"
                                status_icon = "✅"
                            else:
                                status_color = "#EF4444"
                                status_icon = "❌"
                           
                            st.markdown(f"""
                            <div style="background: white; padding: 2rem; border-radius: 15px; border: 2px solid {status_color};
                                        text-align: center; margin: 1rem 0;">
                                <h1 style="color: {status_color}; font-size: 2.5rem; margin: 0;">
                                    {status_icon} {status.replace('✅', '').replace('❌', '')}
                                </h1>
                            </div>
                            """, unsafe_allow_html=True)
                           
                            # Scores in columns
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3 style="color: #4F46E5;">Readiness Score</h3>
                                    <h1 style="font-size: 3rem; color: #1F2937; margin: 1rem 0;">{readiness}/100</h1>
                                    <div style="background: #E5E7EB; height: 10px; border-radius: 5px; overflow: hidden;">
                                        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                                                    width: {readiness}%; height: 100%;"></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                           
                            with col2:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3 style="color: #4F46E5;">Placement Probability</h3>
                                    <h1 style="font-size: 3rem; color: #1F2937; margin: 1rem 0;">{probability:.0%}</h1>
                                    <div style="background: #E5E7EB; height: 10px; border-radius: 5px; overflow: hidden;">
                                        <div style="background: linear-gradient(90deg, #10B981 0%, #059669 100%);
                                                    width: {probability*100}%; height: 100%;"></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                           
                            # Company suggestions
                            if company_suggestions:
                                st.markdown('<h3 class="sub-header">🏢 Recommended Companies</h3>', unsafe_allow_html=True)
                               
                                # Display companies in cards
                                cols = st.columns(min(4, len(company_suggestions)))
                                for idx, company in enumerate(company_suggestions):
                                    with cols[idx % 4]:
                                        st.markdown(f"""
                                        <div style="background: white; padding: 1rem; border-radius: 10px;
                                                    border: 1px solid #E5E7EB; text-align: center;">
                                            <h4 style="margin: 0; color: #1F2937;">{company}</h4>
                                            <p style="color: #6B7280; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                                                {student['branch']} Opportunities
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                           
                            # Career insights
                            st.markdown('<h3 class="sub-header">💡 Career Insights</h3>', unsafe_allow_html=True)
                           
                            insight_col1, insight_col2 = st.columns(2)
                            insights = career_insights.split(' | ')
                           
                            with insight_col1:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
                                            padding: 1.5rem; border-radius: 10px;">
                                    <h4 style="color: #065F46;">✅ Strengths</h4>
                                """, unsafe_allow_html=True)
                               
                                if student['cgpa'] >= 8:
                                    st.write("• Strong Academic Record")
                                if student.get('internship_count', 0) >= 2:
                                    st.write("• Good Industry Exposure")
                                if student['projects_count'] >= 3:
                                    st.write("• Practical Project Experience")
                                if student.get('certifications_count', 0) >= 2:
                                    st.write("• Certified Professional")
                               
                                st.markdown("</div>", unsafe_allow_html=True)
                           
                            with insight_col2:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
                                            padding: 1.5rem; border-radius: 10px;">
                                    <h4 style="color: #991B1B;">📈 Improvement Areas</h4>
                                """, unsafe_allow_html=True)
                               
                                if student['cgpa'] < 7.5:
                                    st.write("• Improve CGPA")
                                if student.get('internship_count', 0) == 0:
                                    st.write("• Get an Internship")
                                if student.get('certifications_count', 0) < 2:
                                    st.write("• Obtain Certifications")
                                if student.get('internship_type') == "None":
                                    st.write("• Aim for MNC/Startup Internship")
                               
                                st.markdown("</div>", unsafe_allow_html=True)
                           
                            # Branch-specific guidance
                            st.markdown('<h3 class="sub-header">🎯 Branch-specific Guidance</h3>', unsafe_allow_html=True)
                            branch_info = BRANCH_CONFIG[student['branch']]
                            st.write(f"**Career Paths for {student['branch']}:**")
                            for path in branch_info['career_paths'][:3]:
                                st.write(f"- {path}")
                           
                            # PDF DOWNLOAD SECTION
                            st.markdown("---")
                            st.subheader("📄 Download Your Prediction Report")
                           
                            # Generate PDF
                            try:
                                pdf_bytes = generate_prediction_pdf(
                                    student,
                                    readiness,
                                    probability,
                                    status,  # Use status without emojis for PDF
                                    company_suggestions,
                                    career_insights,
                                    branch_info
                                )
                               
                                # Create download link with custom styling
                                filename = f"placement_report_{student['student_id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
                                html_link = create_download_link(pdf_bytes, filename)
                               
                                # Display download button
                                st.markdown(html_link, unsafe_allow_html=True)
                                st.info("📋 The report includes your prediction results, company recommendations, and career insights.")
                               
                            except Exception as e:
                                st.error(f"❌ Error generating PDF: {str(e)}")
                                st.info("Try restarting the application or check if fpdf is installed correctly.")
                           
                            # View Prediction History
                            predictions_df = get_predictions()
                            student_pred = predictions_df[predictions_df['student_id'] == student['student_id']].head(3)
                            if not student_pred.empty:
                                st.subheader("📈 Recent Predictions")
                                # Display only important columns
                                display_cols = ['created_at', 'status', 'probability', 'readiness_score']
                                available_cols = [col for col in display_cols if col in student_pred.columns]
                               
                                if available_cols:
                                    st.dataframe(student_pred[available_cols].reset_index(drop=True))
                                else:
                                    st.dataframe(student_pred.reset_index(drop=True))
                           
                            # View All Predictions Option
                            if st.checkbox("Show all predictions in database"):
                                all_predictions = get_predictions()
                                if not all_predictions.empty:
                                    st.subheader("📊 All Predictions in Database")
                                    st.dataframe(all_predictions)
                                else:
                                    st.info("No predictions in database yet.")

# =========================
# CHATBOT PAGE
# =========================
elif menu == "💬 Chat Assistant":
    chatbot_interface()

# =========================
# ENHANCED FACULTY LOGIN PAGE
# =========================
elif menu == "👨‍🏫 Faculty Login":
    st.markdown('<h1 class="main-header">👨‍🏫 Faculty Portal</h1>', unsafe_allow_html=True)
   
    # Login form in a centered card
    col1, col2, col3 = st.columns([1, 2, 1])
   
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2.5rem; border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="color: #4F46E5; margin-bottom: 2rem;">🔐 Faculty Login</h2>
        """, unsafe_allow_html=True)
       
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter faculty username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
           
            login_button = st.form_submit_button("🚀 Login to Dashboard", use_container_width=True)
       
        st.markdown("</div>", unsafe_allow_html=True)
       
        if login_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
   
    # If logged in, show admin dashboard
    if st.session_state.get("logged_in", False):
        st.markdown("---")
       
        # Admin dashboard with tabs
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📊 Overview", "👥 Student Management", "⚙️ Database"])
       
        with admin_tab1:
            st.markdown('<h3 class="sub-header">📈 System Overview</h3>', unsafe_allow_html=True)
           
            students_df = get_students()
            predictions_df = get_predictions()
           
            if not students_df.empty:
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", len(students_df))
                with col2:
                    placed = len(predictions_df[predictions_df['status'].str.contains('PLACED', case=False)]) if not predictions_df.empty else 0
                    st.metric("Predicted Placements", placed)
                with col3:
                    avg_cgpa = students_df['cgpa'].mean()
                    st.metric("Average CGPA", f"{avg_cgpa:.2f}")
                with col4:
                    st.metric("Branches", students_df['branch'].nunique())
               
                # Charts
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Branch Distribution', 'CGPA Distribution'),
                    specs=[[{'type': 'pie'}, {'type': 'histogram'}]]
                )
               
                # Pie chart
                branch_counts = students_df['branch'].value_counts()
                fig.add_trace(
                    go.Pie(labels=branch_counts.index, values=branch_counts.values),
                    row=1, col=1
                )
               
                # Histogram
                fig.add_trace(
                    go.Histogram(x=students_df['cgpa'], nbinsx=20),
                    row=1, col=2
                )
               
                fig.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
       
        with admin_tab2:
            st.markdown('<h3 class="sub-header">👥 Student Management</h3>', unsafe_allow_html=True)
           
            if not students_df.empty:
                # Search and filter
                search_col1, search_col2 = st.columns(2)
                with search_col1:
                    search_term = st.text_input("🔍 Search students")
                with search_col2:
                    filter_branch = st.selectbox("Filter by branch", ["All"] + list(students_df['branch'].unique()))
               
                # Filter data
                display_df = students_df.copy()
                if search_term:
                    display_df = display_df[display_df['student_name'].str.contains(search_term, case=False) |
                                          display_df['student_id'].str.contains(search_term, case=False)]
                if filter_branch != "All":
                    display_df = display_df[display_df['branch'] == filter_branch]
               
                # Display table
                st.dataframe(display_df, use_container_width=True)
               
                # Export options
                if st.button("📥 Export Students to CSV"):
                    csv = students_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="students_export.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No students in database")
       
        with admin_tab3:
            st.markdown('<h3 class="sub-header">⚙️ Database Management</h3>', unsafe_allow_html=True)
           
            col1, col2 = st.columns(2)
           
            with col1:
                st.markdown("""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #E5E7EB;">
                    <h4 style="color: #4F46E5;">📊 Database Stats</h4>
                    <p><strong>Students Table:</strong> {students_count} records</p>
                    <p><strong>Predictions Table:</strong> {predictions_count} records</p>
                    <p><strong>Database Size:</strong> {db_size} KB</p>
                </div>
                """.format(
                    students_count=len(students_df),
                    predictions_count=len(predictions_df) if not predictions_df.empty else 0,
                    db_size=os.path.getsize(DB_PATH)//1024 if os.path.exists(DB_PATH) else 0
                ), unsafe_allow_html=True)
           
            with col2:
                st.markdown("""
                <div style="background: #FEF3C7; padding: 1.5rem; border-radius: 10px; border: 1px solid #F59E0B;">
                    <h4 style="color: #92400E;">⚠️ Danger Zone</h4>
                    <p>These actions cannot be undone.</p>
                </div>
                """, unsafe_allow_html=True)
               
                if st.button("🗑️ Clear All Data", type="secondary"):
                    confirm = st.checkbox("I understand this will delete ALL data permanently")
                    if confirm:
                        if st.button("✅ Confirm Delete ALL Data", type="primary"):
                            try:
                                conn = sqlite3.connect(DB_PATH)
                                cur = conn.cursor()
                                cur.execute("DELETE FROM students")
                                cur.execute("DELETE FROM predictions")
                                conn.commit()
                                conn.close()
                                st.error("⚠️ All data has been deleted!")
                                st.session_state.logged_in = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
       
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully!")
            st.rerun()

# =========================
# FOOTER
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 1rem 0;">
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem;"><strong>PlaceMate Pro v2.5</strong></p>
    <p style="font-size: 0.8rem;">AI-Powered Placement Assistant</p>
    <div style="margin-top: 1rem; font-size: 0.8rem;">
        <p>✅ Enhanced Dashboard</p>
        <p>🤖 Chat Assistant</p>
        <p>📊 Analytics</p>
        <p>📄 PDF Reports</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    # Initialize session states
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []