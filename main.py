# ============================================
# PLACE MATE – STUDENT PLACEMENT SYSTEM (CLI)
# ============================================

import os
import pandas as pd

# --------------------------------------------
# FILE PATHS
# --------------------------------------------
DATA_PATH = "data/registered_students.csv"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# --------------------------------------------
# CSV CHECK
# --------------------------------------------
COLUMNS = [
    "student_id", "student_name", "branch", "cgpa",
    "coding_skill", "communication_skill", "aptitude_skill",
    "problem_solving", "projects_count", "internship_count",
    "certification_count", "internship_company_level",
    "certification_company_level", "technical_skills", "tools_known",
    "selected_career"
]

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_PATH, index=False)

df = pd.read_csv(DATA_PATH)

# --------------------------------------------
# BRANCH CONFIG
# --------------------------------------------
BRANCH_SKILLS = {
    "CSE": ["Python", "Java", "C++", "SQL", "ML", "Data Analytics"],
    "ECE": ["Embedded C", "VHDL", "MATLAB", "Python", "Arduino", "PCB Design"],
    "MECHANICAL": ["AutoCAD", "SolidWorks", "ANSYS", "MATLAB", "CATIA"],
    "CIVIL": ["AutoCAD Civil 3D", "STAAD.Pro", "Revit", "ETABS", "MS Project"],
    "ELECTRICAL": ["MATLAB", "Proteus", "ETAP", "Power Systems", "PLC"],
    "OTHER": ["Generic Skill 1", "Generic Skill 2"]
}

BRANCH_TOOLS = {
    "CSE": ["Git", "AWS", "Docker", "Linux", "Jupyter Notebook"],
    "ECE": ["Oscilloscope", "Multimeter", "PCB Etching Tools", "Proteus", "Arduino IDE"],
    "MECHANICAL": ["SolidWorks", "ANSYS", "MATLAB", "CATIA", "MS Excel"],
    "CIVIL": ["AutoCAD", "STAAD.Pro", "MS Project", "Revit", "Surveying Tools"],
    "ELECTRICAL": ["MATLAB", "Simulink", "Proteus", "ETAP", "Multimeter"],
    "OTHER": ["Generic Tool 1", "Generic Tool 2"]
}

BRANCH_COMPANIES = {
    "CSE": ["Google", "Microsoft", "Amazon", "TCS", "Infosys"],
    "ECE": ["Qualcomm", "Intel", "Texas Instruments", "TCS", "Infosys"],
    "MECHANICAL": ["L&T", "Siemens", "TATA Motors", "Mahindra", "Bosch"],
    "CIVIL": ["L&T", "Reliance Infrastructure", "Shapoorji Pallonji", "Afcons"],
    "ELECTRICAL": ["Siemens", "ABB", "BHEL", "GE Power", "TCS"],
    "OTHER": ["Generic Company A", "Generic Company B"]
}

CAREER_BY_STRENGTH = {
    "Coding": ["Software Developer", "Data Scientist"],
    "Aptitude": ["Data Analyst", "Research Analyst"],
    "Communication": ["HR", "Business Analyst", "Consultant"],
    "Problem Solving": ["Product Manager", "Consultant"],
    "Technical": ["Engineer", "Technician"]
}

PLACEMENT_THRESHOLD = 65  # Minimum readiness score to be placed

# --------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------
def detect_strength(student, branch):
    if branch in ["CSE", "ECE"]:
        skills = {
            "Coding": student.get("coding_skill", 0),
            "Aptitude": student.get("aptitude_skill", 0),
            "Communication": student.get("communication_skill", 0),
            "Problem Solving": student.get("problem_solving", 0)
        }
    else:
        skills = {
            "Aptitude": student.get("aptitude_skill", 0),
            "Communication": student.get("communication_skill", 0),
            "Problem Solving": student.get("problem_solving", 0),
            "Technical": len(student.get("technical_skills", "").split(", "))
        }
    return max(skills, key=skills.get)

def calculate_results(student, branch):
    tech_skill_score = len(student.get("technical_skills", "").split(", "))
    tools_score = len(student.get("tools_known", "").split(", "))

    score = (
        (student["cgpa"]/10)*20 +
        (student.get("communication_skill",0)/10)*10 +
        (student.get("aptitude_skill",0)/10)*15 +
        (student.get("problem_solving",0)/10)*15 +
        (student.get("projects_count",0)/5)*5 +
        (student.get("internship_count",0)/5)*5 +
        (student.get("internship_company_level",0)/3)*5 +
        (student.get("certification_count",0)/5)*3 +
        (student.get("certification_company_level",0)/3)*2 +
        tech_skill_score + tools_score
    )

    if branch in ["CSE","ECE"]:
        score += (student.get("coding_skill",0)/10)*20

    readiness = min(round(score,2),100)
    probability = round(readiness/100,2)
    status = "PLACED ✅" if readiness >= PLACEMENT_THRESHOLD else "NOT PLACED ❌"
    companies = BRANCH_COMPANIES.get(branch,[])
    eligible = [c for c in companies if student["cgpa"]>=6.0]
    strength = detect_strength(student, branch)
    return readiness, probability, status, strength, eligible

def career_insights(student, branch):
    strengths = []
    improvements = []

    if student["cgpa"] >= 7:
        strengths.append("Good Academic Performance")
    else:
        improvements.append("Improve CGPA")

    if branch in ["CSE", "ECE"]:
        if student["coding_skill"] >= 7:
            strengths.append("Strong Coding Skills")
        else:
            improvements.append("Practice Coding Daily")

    if student["projects_count"] >= 2:
        strengths.append("Good Project Exposure")
    else:
        improvements.append("Build More Real-Time Projects")

    if student["communication_skill"] >= 6:
        strengths.append("Decent Communication Skills")
    else:
        improvements.append("Improve Communication Skills")

    return strengths, improvements

def save_student(student):
    global df
    df = pd.concat([df, pd.DataFrame([student])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
    print("💾 Student saved successfully!")

def show_dashboard(student, branch):
    readiness, probability, status, strength, eligible = calculate_results(student, branch)
    strengths, improvements = career_insights(student, branch)

    print("\n📊 STUDENT DASHBOARD")
    print("="*50)
    print(f"Name                 : {student.get('student_name','N/A')}")
    print(f"Branch               : {student.get('branch','N/A')}")
    print(f"Strength             : {strength}")
    print(f"Selected Career      : {student.get('selected_career','N/A')}")
    print(f"Readiness Score      : {readiness}")
    print(f"Placement Probability: {probability}")
    print(f"Eligible Companies   : {', '.join(eligible)}")
    print(f"Status               : {status}")
    print("\n✅ Strengths:")
    for s in strengths:
        print(f" - {s}")
    print("\n⚠️ Areas to Improve:")
    for i in improvements:
        print(f" - {i}")
    print("="*50)

# --------------------------------------------
# MAIN LOOP
# --------------------------------------------
while True:
    print("\n====== PLACEMATE MENU ======")
    print("1️⃣ Student")
    print("2️⃣ Faculty")
    print("3️⃣ Exit")
    choice = input("Enter choice (1/2/3): ")

    if choice=="1":
        student_id = input("Student ID: ").strip()
        branch = input("Branch (CSE/ECE/Mechanical/Civil/Electrical/Other): ").strip().upper()
        existing = df[df["student_id"]==student_id]
        if not existing.empty:
            student = existing.iloc[0].to_dict()
            print(f"\n👋 Welcome back, {student.get('student_name','N/A')}!")
            show_dashboard(student, branch)
        else:
            print("\n📝 NEW STUDENT REGISTRATION")
            student = {"student_id": student_id, "branch": branch}
            student["student_name"] = input("Name: ")
            student["cgpa"] = float(input("CGPA (0-10): "))

            if branch in ["CSE","ECE"]:
                student["coding_skill"] = float(input("Coding Skill (0-10): "))
            else:
                student["coding_skill"] = 0

            student["communication_skill"] = float(input("Communication Skill (0-10): "))
            student["aptitude_skill"] = float(input("Aptitude Skill (0-10): "))
            student["problem_solving"] = float(input("Problem Solving (0-10): "))
            student["projects_count"] = int(input("Projects Completed: "))
            student["internship_count"] = int(input("Internships Done: "))
            student["internship_company_level"] = int(input("Internship Level (0-3): "))
            student["certification_count"] = int(input("Certifications: "))
            student["certification_company_level"] = int(input("Certification Level (0-3): "))

            print(f"Available Technical Skills: {', '.join(BRANCH_SKILLS.get(branch,[]))}")
            student["technical_skills"] = input("Technical Skills (comma-separated): ")

            print(f"Available Tools: {', '.join(BRANCH_TOOLS.get(branch,[]))}")
            student["tools_known"] = input("Tools Known (comma-separated): ")

            strength = detect_strength(student, branch)
            student["selected_career"] = CAREER_BY_STRENGTH.get(strength, ["Engineer"])[0]

            save_student(student)
            show_dashboard(student, branch)

    elif choice=="2":
        print("\n👨‍🏫 FACULTY DASHBOARD")
        print("="*60)
        print(df[["student_id","student_name","branch","cgpa","selected_career"]])
        print("="*60)

    elif choice=="3":
        print("👋 Thank you for using PlaceMate!")
        break
    else:
        print("❌ Invalid choice. Try again.")
