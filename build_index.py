"""
Build unified article index from Excel and scraped data.
Generates articles.json for the searchable HTML page.
"""

import pandas as pd
import json
import re

# Read Excel data
print("Reading Excel data...")
excel_df = pd.read_excel('cswep_articles_index.xlsx')

# Normalize Excel data
excel_articles = []
for _, row in excel_df.iterrows():
    article = {
        'title': str(row['Article Title']).strip() if pd.notna(row['Article Title']) else '',
        'author': str(row['Author 1']).strip() if pd.notna(row['Author 1']) else '',
        'issue': f"{row['Quarter']} {row['Year']}" if pd.notna(row['Quarter']) else str(row['Year']),
        'year': int(row['Year']) if pd.notna(row['Year']) else 0,
        'topic': str(row['Topic1']).strip() if pd.notna(row['Topic1']) else '',
        'audience': str(row['Audience1']).strip() if pd.notna(row['Audience1']) else '',
        'url': str(row['URL']).strip() if pd.notna(row['URL']) and str(row['URL']).startswith('http') else '',
        'source': 'excel'
    }
    if article['title']:
        excel_articles.append(article)

print(f"Excel articles: {len(excel_articles)}")

# Issue focus topics - maps issue name to its primary focus topic
ISSUE_TOPICS = {
    # 2025
    "Issue IV 2025": "Fertility",
    "Issue III 2025": "Visibility & Voice",
    "Issue II 2025": "Women in Leadership",
    "Issue I 2025": "Status of Women",
    # 2024
    "Issue IV 2024": "Publishing",
    "Issue III 2024": "Job Market",
    "Issue II 2024": "Retention",
    "Issue I 2024": "Status of Women",
    # 2023
    "Issue IV 2023": "Sexual Harassment",
    "Issue III 2023": "Abortion Access",
    "Issue II 2023": "Undergraduate Experience",
    "Issue I 2023": "Status of Women",
    # 2022
    "Issue IV 2022": "Seminar Dynamics",
    "Issue III 2022": "PhD Admissions",
    "Issue II 2022": "Non-Tenure Track",
    "Issue I 2022": "Status of Women",
    # 2021
    "Issue IV 2021": "Research Funding",
    "Issue III 2021": "International Perspective",
    "Issue II 2021": "Alternative Career Paths",
    "Issue I 2021": "Status of Women",
    # 2020
    "Issue IV 2020": "COVID Impact",
    "Issue III 2020": "Job Market",
    "Issue II 2020": "Professional Development",
    "Issue I 2020": "Status of Women",
    # 2019
    "Issue III 2019": "Career Challenges",
    "Issue II 2019": "Job Market",
    "Issue I 2019": "Mentoring",
    # 2018
    "Issue III 2018": "Diversity & Inclusion",
    "Issue II 2018": "Media Relations",
}

# Scraped data (from topics page) - manually structured from the WebFetch output
# This represents the key articles scraped from the topics page
# Note: "topic" field contains article-specific topics; issue topic is added automatically
scraped_articles = [
    # 2025 Issue IV - Focus on Fertility
    {"title": "Focus on Fertility (Introduction)", "author": "Caitlin Myers", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},
    {"title": "Parenting, Academia, and Perspective", "author": "Kosali Simon", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},
    {"title": "The Miracles and Challenges of Assistive Reproductive Therapies", "author": "Kelly M. Jones", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},
    {"title": "On Being a Christian Economist Adoptive Special-Needs Mom", "author": "Sarah Hamersma", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},
    {"title": "It's All About Choice", "author": "Sarah Baird", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},
    {"title": "Lessons from Almost Dying in Childbirth at Conference", "author": "Jialan Wang", "issue": "Issue IV 2025", "year": 2025, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23837"},

    # 2025 Other Issues
    # 2025 Issue II - Focus on Women in Leadership
    {"title": "Introduction: Focus on Women in Leadership", "author": "Francisca Antman", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Remain Open To the Unexpected—and Keep Learning Along the Way", "author": "Susan M. Collins", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Lead From Where You Are", "author": "Mary C. Daly", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Be Open-Minded and True to Yourself", "author": "Cecilia Elena Rouse", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "How to Embrace Uncertainty in Your Career", "author": "Daryl Fairweather", "issue": "Issue II 2025", "year": 2025, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Learning by Doing: Leadership Lessons from My Journey", "author": "Shanthi Nataraj", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Moving from Academia to Policy to Management and Back", "author": "Lisa M. Lynch", "issue": "Issue II 2025", "year": 2025, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "A Non-Traditional Pathway to Academic Leadership", "author": "Marie T. Mora", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    {"title": "Academic Leadership in a Liberal Arts College", "author": "", "issue": "Issue II 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22528"},
    # 2025 Issue I - Status of Women Report
    {"title": "Interview: Carolyn Shaw Bell Award Winner Sandra Black", "author": "Marika Cabral", "issue": "Issue I 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22059"},
    {"title": "Interview: Elaine Bennett Award Winner Maryam Farboodi", "author": "Monika Piazzesi", "issue": "Issue I 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22059"},
    {"title": "CSWEP Annual Report", "author": "Linda Tesar", "issue": "Issue I 2025", "year": 2025, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22059"},
    {"title": "Survey Report on the Status of Women in the Economics Profession", "author": "Joanne Hsu", "issue": "Issue I 2025", "year": 2025, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=22059"},

    # 2025 Issue III - Visibility and Voice in the Profession
    {"title": "Introduction: Focus on Visibility and Voice in the Profession", "author": "Olga Shurchkov", "issue": "Issue III 2025", "year": 2025, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "Mission Impossible: Self-Promotion", "author": "Christine Exley", "issue": "Issue III 2025", "year": 2025, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "Making Ourselves Seen: Visibility in the Economics Profession", "author": "Olga Stoddard", "issue": "Issue III 2025", "year": 2025, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "Engaging in Public Scholarship: the Process of Writing and Publishing a Trade Press Book", "author": "Corinne Low", "issue": "Issue III 2025", "year": 2025, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "Building Visibility on Academic Social Media", "author": "Khoa Vu", "issue": "Issue III 2025", "year": 2025, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "From the Chair", "author": "Linda Tesar", "issue": "Issue III 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "In Memoriam: Marina von Neumann Whitman (1935-2025)", "author": "", "issue": "Issue III 2025", "year": 2025, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},
    {"title": "CSWEP's Mid-Career Peer-to-Peer Mentoring Program", "author": "Kasey Buckles", "issue": "Issue III 2025", "year": 2025, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=23379"},

    # 2024
    # 2024 Issue IV - Journal Editors as Gatekeepers
    {"title": "Gatekeepers of Progress: Historical View and Advice on Research from Current Women Editors in Economics", "author": "Rohan Williamson", "issue": "Issue IV 2024", "year": 2024, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21767"},
    {"title": "Gender, Gatekeeping and the Editorial Process: Then and Now", "author": "Ann Mari May", "issue": "Issue IV 2024", "year": 2024, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21767"},
    {"title": "Junior Faculty and the Role of Journal Editors", "author": "Toni M. Whited", "issue": "Issue IV 2024", "year": 2024, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21767"},
    {"title": "Navigating the Publishing Landscape", "author": "Antoinette Schoar", "issue": "Issue IV 2024", "year": 2024, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21767"},
    # 2024 Issue III - Post-Pandemic Job Market in Economics
    {"title": "Introduction to Market Version N.0", "author": "Orgul Ozturk", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    {"title": "The Post-COVID Job Market for New Ph.D. Economists", "author": "John Cawley, Sammy Gold", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    {"title": "How to Deal with the New Post-COVID Job Market", "author": "Anne M. Burton", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    {"title": "The Post-COVID Academic Job Market from a Search Chair Perspective", "author": "Mike Kofoed", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    {"title": "Pulling the Curtain Behind the Academic Job Market", "author": "Sebastian Tello Trillo", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    {"title": "The Rise of the Economics Teaching Specialist", "author": "Todd Yarbrough", "issue": "Issue III 2024", "year": 2024, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=21393"},
    # 2024 Issue II - Why Are Women Leaving?
    {"title": "Introduction: Why Are Women Leaving?", "author": "Ina Ganguli, Anna Paulson", "issue": "Issue II 2024", "year": 2024, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20893"},
    {"title": "Gendered Devaluation and Retention Among U.S. Faculty", "author": "Katie Spoon, Aaron Clauset", "issue": "Issue II 2024", "year": 2024, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20893"},
    {"title": "Climbing the Ladder or Falling off the Cliff?", "author": "Marieke Kleemans, Rebecca Thornton", "issue": "Issue II 2024", "year": 2024, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20893"},
    {"title": "Gender Balance in the Academic Finance Profession", "author": "Mila Getmansky Sherman, Heather Tookes", "issue": "Issue II 2024", "year": 2024, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20893"},
    {"title": "Mid-Career: The Few and the Forgotten", "author": "Kasey Buckles", "issue": "Issue II 2024", "year": 2024, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20893"},
    # 2024 Issue I - Status of Women Report
    {"title": "Interview: Carolyn Shaw Bell Award Winner Kaye Husbands Fealing", "author": "Marionette Holmes", "issue": "Issue I 2024", "year": 2024, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20292"},
    {"title": "Interview: Elaine Bennett Award Winner Maya Rossin-Slater", "author": "Kosali Simon", "issue": "Issue I 2024", "year": 2024, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20292"},
    {"title": "CSWEP Annual Report", "author": "Anusha Chari", "issue": "Issue I 2024", "year": 2024, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20292"},
    {"title": "Survey Report on the Status of Women in the Economics Profession", "author": "Margaret Levenstein", "issue": "Issue I 2024", "year": 2024, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=20292"},

    # 2023
    # 2023 Issue IV - What the AEA is Doing About Sexual Harassment
    {"title": "Introduction: What the AEA is Doing About Sexual Harassment", "author": "Donna Ginther", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    {"title": "Some AEA Policy Updates", "author": "", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    {"title": "Sexual Harassment in the Economics Profession: the Context and the AEA's Approach", "author": "Ben S. Bernanke", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    {"title": "The Current State of the AEA's Professional Climate Measures and Ideas for Making Further Progress", "author": "Christina D. Romer", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    {"title": "Sexual Harassment in the Economics Profession: Lessons Learned and the Way Forward", "author": "Audrey J. Anderson", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    {"title": "Organizational Actions to Address Gender Harassment in STEM", "author": "Billy M. Williams", "issue": "Issue IV 2023", "year": 2023, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19848"},
    # 2023 Issue III - The Changed Landscape of Abortion Access
    {"title": "Introduction: The Changed Landscape of Abortion Access", "author": "Yana van der Meulen Rodgers", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    {"title": "The Shifting Landscape of Abortion Access", "author": "Caitlin Myers", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    {"title": "In the Wake of Dobbs: Abortion Practice and Reproductive Justice", "author": "Taida Wolfe", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    {"title": "Legal Perspective on Dobbs", "author": "Naomi Cahn", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    {"title": "Restrictions on Health Care Endanger Patients Everywhere", "author": "Alison Stuebe", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    {"title": "What Universities and Faculty Can Do To Support Students In States With Abortion Bans", "author": "Janet K. Levi", "issue": "Issue III 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=19347"},
    # 2023 Issue II - Focus on the Undergraduate Experience
    {"title": "Introduction: Focus on the Undergraduate Experience", "author": "Marionette Holmes", "issue": "Issue II 2023", "year": 2023, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18540"},
    {"title": "Mentoring to Strengthen the Pipeline", "author": "Sarah Jacobson", "issue": "Issue II 2023", "year": 2023, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18540"},
    {"title": "Pipeline Problem Interventions", "author": "Rebecca Sen Choudhoury, Bola Olaniyan", "issue": "Issue II 2023", "year": 2023, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18540"},
    {"title": "Non-Traditional Students", "author": "Marie T. Mora", "issue": "Issue II 2023", "year": 2023, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18540"},
    {"title": "Pathways to Research and Doctoral Careers", "author": "Stephen Lamb, Pietro Veronesi", "issue": "Issue II 2023", "year": 2023, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18540"},
    # 2023 Issue I - Status of Women Report
    {"title": "Interview: Carolyn Shaw Bell Award Winner Martha J. Bailey", "author": "Sara Heller", "issue": "Issue I 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18271"},
    {"title": "Interview: Elaine Bennett Award Winner Rebecca Diamond", "author": "Kathryn Shaw", "issue": "Issue I 2023", "year": 2023, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18271"},
    {"title": "CSWEP Annual Report", "author": "Anusha Chari", "issue": "Issue I 2023", "year": 2023, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18271"},
    {"title": "Survey Report on the Status of Women in the Economics Profession", "author": "Margaret Levenstein", "issue": "Issue I 2023", "year": 2023, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=18271"},

    # 2022
    # 2022 Issue IV - Economics Seminar Dynamics Revisited
    {"title": "Introduction: Economics Seminar Dynamics Revisited", "author": "Katherine Silz Carson", "issue": "Issue IV 2022", "year": 2022, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17929"},
    {"title": "How Can We Change the Seminar Culture in Economics?", "author": "Alicia Sasser Modestino", "issue": "Issue IV 2022", "year": 2022, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17929"},
    {"title": "Seminar Dynamics in Economics: A View from a Member of the Seminar Dynamics Collective", "author": "Silvia Vanutelli", "issue": "Issue IV 2022", "year": 2022, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17929"},
    {"title": "An Invitation to Speaker Diversity", "author": "Jose Fernandez", "issue": "Issue IV 2022", "year": 2022, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17929"},
    # 2022 Issue III - Navigating the Ph.D. Admissions Process
    {"title": "Introduction: Navigating the Ph.D. Admissions Process", "author": "Kasey Buckles", "issue": "Issue III 2022", "year": 2022, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17488"},
    {"title": "Helping Faculty Help Students Get Into Ph.D. Programs in Economics", "author": "Dick Startz", "issue": "Issue III 2022", "year": 2022, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17488"},
    {"title": "The Path to an Economics PhD: Advising Students About Pre-Docs", "author": "Olga Shurchkov", "issue": "Issue III 2022", "year": 2022, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17488"},
    {"title": "Insight from Graduate Admissions Committee Chairs and Members", "author": "Kasey Buckles", "issue": "Issue III 2022", "year": 2022, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17488"},
    {"title": "Top 10 Tips and Insights to Share with Students", "author": "", "issue": "Issue III 2022", "year": 2022, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=17488"},
    # 2022 Issue II - A Guide for Non-Tenure Track Faculty
    {"title": "Introduction: A Guide for Non-Tenure Track Faculty", "author": "Shreyasee Das, Seth Gitter", "issue": "Issue II 2022", "year": 2022, "topic": "Tenure & Promotion", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    {"title": "The Job Market for Non-Tenure Track Academic Economists", "author": "Gina Pieters, Chris Roark", "issue": "Issue II 2022", "year": 2022, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    {"title": "Publishing Without a Tenure Clock", "author": "Jadrian Wooten", "issue": "Issue II 2022", "year": 2022, "topic": "Publishing", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    {"title": "Navigating a New Fishbowl: Exploring the Non-Tenure Track Role", "author": "Kim Holder", "issue": "Issue II 2022", "year": 2022, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    {"title": "The Role of the Director of Undergraduate Studies", "author": "Melanie Fox", "issue": "Issue II 2022", "year": 2022, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    {"title": "Strategies to Stay Relevant Outside the Classroom", "author": "Darshak Patel", "issue": "Issue II 2022", "year": 2022, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16549"},
    # 2022 Issue I - Status of Women Report
    {"title": "Interview: 2021 Carolyn Shaw Bell Award Winner Joyce P. Jacobsen", "author": "Richard S. Grossman", "issue": "Issue I 2022", "year": 2022, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16197"},
    {"title": "2021 Report on the Status of Women in the Economics Profession", "author": "Judith Chevalier, Margaret Levenstein", "issue": "Issue I 2022", "year": 2022, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=16197"},

    # 2021
    # 2021 Issue IV - Getting Funding for Your Research
    {"title": "Introduction: Getting Funding for Your Research", "author": "Jennifer Doleac", "issue": "Issue IV 2021", "year": 2021, "topic": "Funding", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15929"},
    {"title": "Advice from Funders", "author": "Oriana Bandiera, Tyler Cowen, Korin Davis, Adam Gamoran, Stephen Glauser, Pace Phillips, Mark Steinmeyer", "issue": "Issue IV 2021", "year": 2021, "topic": "Funding", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15929"},
    {"title": "Advice from Scholars", "author": "Anjali Adukia, Beth Akers, Laura Gee, Sara Heller, Manisha Shah, Laura Wherry", "issue": "Issue IV 2021", "year": 2021, "topic": "Funding", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15929"},
    # 2021 Issue III - Women in Economics: An International Perspective
    {"title": "Introduction: Focus on Women in Economics: An International Perspective", "author": "Karen Pence", "issue": "Issue III 2021", "year": 2021, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15374"},
    {"title": "The Canadian Economics Profession: How are the Women Faring?", "author": "Elizabeth Dhuey", "issue": "Issue III 2021", "year": 2021, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15374"},
    {"title": "Women in UK Economics", "author": "Erin Hengel, Almudena Sevilla, Sarah Smith", "issue": "Issue III 2021", "year": 2021, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15374"},
    {"title": "Gender Equity in Academia: Ten Years of Support in Australia and New Zealand", "author": "Kathleen Walsh, Anna von Reibnitz, Jacquelyn Humphrey", "issue": "Issue III 2021", "year": 2021, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=15374"},
    # 2021 Issue II - Jobs for Economists in DC / Alternative Career Paths
    {"title": "A Conversation with Stephanie Aaronson", "author": "Judith Chevalier", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "Introduction: Focus on Alternative Career Paths in Economics", "author": "Gray Kimbrough", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "The Transition from the Ivory Tower to the Halls of Government", "author": "Olugbenga Ajilore", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "Working at the Federal Reserve Board", "author": "Laura Feiveson", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "Conducting Research and Informing Policy at the USDA", "author": "Laura Tiehen", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "Road to the U.S. Census Bureau", "author": "Dani Sandler", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    {"title": "More Than a Job", "author": "Jevay Grooms", "issue": "Issue II 2021", "year": 2021, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=14468"},
    # 2021 Issue I - Status of Women Report
    {"title": "Interview: 2020 Elaine Bennett Research Prize Winner Stefanie Stantcheva", "author": "David Cutler", "issue": "Issue I 2021", "year": 2021, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13968"},
    {"title": "Interview: 2020 Carolyn Shaw Bell Award Winner Nancy L. Rose", "author": "Mar Reguant", "issue": "Issue I 2021", "year": 2021, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13968"},
    {"title": "2020 Report on the Status of Women in the Economics Profession", "author": "Judith Chevalier, Margaret Levenstein", "issue": "Issue I 2021", "year": 2021, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13968"},

    # 2020
    # 2020 Issue IV - Ideas for Mitigating the Disparate Impact of COVID in Economics
    {"title": "Introduction: Ideas for Mitigating the Disparate Impact of COVID in Economics", "author": "Jonathan Guryan, Petra Moser", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    {"title": "COVID-19 Gave My Career Mild Depression", "author": "Misty L. Heggeness", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    {"title": "COVID-19 and the New Normal", "author": "Jevay Grooms", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    {"title": "One Dean's View on Faculty Work During COVID", "author": "Trevon Logan", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    {"title": "COVID-19 Has Long-Term Implications for Gender Disparities in Economics", "author": "Jenna Stearns", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    {"title": "Strategies to Stem the Disparate Impact of COVID-19 on Faculty of Color", "author": "Dania V. Francis", "issue": "Issue IV 2020", "year": 2020, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13540"},
    # 2020 Issue III - Advice for Job Seekers and Early Career Folks
    {"title": "Introduction: Advice for Job Seekers and Early Career Folks", "author": "Sarah Jacobson", "issue": "Issue III 2020", "year": 2020, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    {"title": "The Job Search and Institutional Culture", "author": "Linda M. Hooks", "issue": "Issue III 2020", "year": 2020, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    {"title": "Being at a Liberal Arts College with High Research Expectations", "author": "Melanie Khamis", "issue": "Issue III 2020", "year": 2020, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    {"title": "Balancing Research and Policy Work in Government Jobs", "author": "Erin Troland", "issue": "Issue III 2020", "year": 2020, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    {"title": "Transitioning between Academic and Non-Academic Jobs", "author": "Kelly M. Jones", "issue": "Issue III 2020", "year": 2020, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    {"title": "Research, Publishing, and Tenure", "author": "Susan Vroman", "issue": "Issue III 2020", "year": 2020, "topic": "Tenure & Promotion", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=13085"},
    # 2020 Issue II - Tips for Surviving and Thriving as an Academic Economist
    {"title": "Introduction: Tips for Surviving and Thriving as an Academic Economist", "author": "Karen Conway", "issue": "Issue II 2020", "year": 2020, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11887"},
    {"title": "Tips for Surviving and Thriving as an Academic Economist", "author": "Laura Argys, Susan Averett, Hope Corman, Dhaval Dave, Joyce Jacobsen, Amanda Ross", "issue": "Issue II 2020", "year": 2020, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11887"},
    # 2020 Issue I - Status of Women Report
    {"title": "Interview: 2019 Carolyn Shaw Bell Award Winner Yan Chen", "author": "Elizabeth (Betsy) Hoffman", "issue": "Issue I 2020", "year": 2020, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11630"},
    {"title": "2019 Report on the Status of Women in the Economics Profession", "author": "Judith Chevalier, Margaret Levenstein", "issue": "Issue I 2020", "year": 2020, "topic": "Status of Women", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11630"},

    # 2019 Issue III - Academic Career Challenges and Opportunities
    {"title": "Interview with Rohini Pande", "author": "Natalia Rigol", "issue": "Issue III 2019", "year": 2019, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Interview with Melissa Dell", "author": "Nathan Nunn", "issue": "Issue III 2019", "year": 2019, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Introduction: Academic Career Challenges and Opportunities", "author": "Abigail Wozniak", "issue": "Issue III 2019", "year": 2019, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Do's and Don'ts at Work and Not", "author": "Kala Krishna", "issue": "Issue III 2019", "year": 2019, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Building Confidence in the Economics Classroom", "author": "Ying Zhen", "issue": "Issue III 2019", "year": 2019, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Having Babies while Under the Tenure Clock", "author": "Alicia Rosburg", "issue": "Issue III 2019", "year": 2019, "topic": "Work-Life Balance", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    {"title": "Reinventing Yourself at Mid-Career", "author": "Prathibha Joshi", "issue": "Issue III 2019", "year": 2019, "topic": "Careers in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=11135"},
    # 2019 Issue II - Advice for Job Seekers
    {"title": "Interview with AEA Ombudsperson Leto Copeley", "author": "Sharon Oster", "issue": "Issue II 2019", "year": 2019, "topic": "Discrimination & Sexual Harassment", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "Introduction: Advice for Job Seekers", "author": "Shahina Amin", "issue": "Issue II 2019", "year": 2019, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "Who Said Being a PhD Job Market Candidate Would Be Easy? Finding that Perfect-for-You Job", "author": "Misty L. Heggeness", "issue": "Issue II 2019", "year": 2019, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "Advice for Job Seekers: Insights from an R1 University", "author": "Kasey Buckles", "issue": "Issue II 2019", "year": 2019, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "Industry Interviews on the Job Market", "author": "Evan Buntrock", "issue": "Issue II 2019", "year": 2019, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "How to Handle an Interview: On-site versus Skype", "author": "Gowun Park", "issue": "Issue II 2019", "year": 2019, "topic": "Job Market", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},
    {"title": "In Memoriam: Alice Rivlin", "author": "", "issue": "Issue II 2019", "year": 2019, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=10740"},

    # 2019 Issue I - Mentoring Underrepresented Minority Women in Economics
    {"title": "Introduction: Mentoring Underrepresented Minority Women in Economics", "author": "Marie T. Mora", "issue": "Issue I 2019", "year": 2019, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=9317"},
    {"title": "An Intersectional Framework for Effectively Mentoring Women of Color in Academia: A Best Practices Guide", "author": "Rosalynn Vega", "issue": "Issue I 2019", "year": 2019, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=9317"},
    {"title": "You Belong Here: Promoting a Sense of Belonging among Underrepresented Minority Women in Economics", "author": "India Johnson", "issue": "Issue I 2019", "year": 2019, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=9317"},
    {"title": "Mentoring Undergraduate Women Who are Students of Color", "author": "Lisa D. Cook", "issue": "Issue I 2019", "year": 2019, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=9317"},
    {"title": "Mentoring as Environmental Stewardship", "author": "Beronda L. Montgomery", "issue": "Issue I 2019", "year": 2019, "topic": "Mentoring", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=9317"},

    # 2018 Issue III - Proactive Efforts to Increase Diversity and Inclusion
    {"title": "Interview with Bell Award Winner Rachel T. A. Croson", "author": "Tanya Rosenblat", "issue": "Issue III 2018", "year": 2018, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8644"},
    {"title": "Introduction: Proactive Efforts to Increase Diversity and Inclusion", "author": "Elizabeth Klee", "issue": "Issue III 2018", "year": 2018, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8644"},
    {"title": "A Perspective from the Federal Reserve Board", "author": "Daniel Coveitz, Karen Pence", "issue": "Issue III 2018", "year": 2018, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8644"},
    {"title": "Applying Lessons from First-Generation Students to Women in Economics", "author": "Fernanda Nechio", "issue": "Issue III 2018", "year": 2018, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8644"},
    {"title": "Countering Gender Bias and Improving Gender Balance", "author": "David Romer, Justin Wolfers", "issue": "Issue III 2018", "year": 2018, "topic": "Women in Economics", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8644"},

    # 2018 Issue II - Working With the Media
    {"title": "Introduction: Working With the Media", "author": "Catalina Amuedo-Dorantes", "issue": "Issue II 2018", "year": 2018, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8051"},
    {"title": "Tips & Tricks for Working with the Media", "author": "Gina Jacobs", "issue": "Issue II 2018", "year": 2018, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8051"},
    {"title": "Talking To the Media About Your Academic Research", "author": "Joni Hersch", "issue": "Issue II 2018", "year": 2018, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8051"},
    {"title": "Tips on Publishing Newspaper Op-Eds", "author": "Paul H. Rubin", "issue": "Issue II 2018", "year": 2018, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8051"},
    {"title": "When Your Research Goes Viral", "author": "Jennifer Bennett Shinall", "issue": "Issue II 2018", "year": 2018, "topic": "Professional Development", "url": "https://docs.google.com/viewer?url=https://www.aeaweb.org/content/file?id=8051"},
]

# Add source field and apply issue topics to scraped articles
for article in scraped_articles:
    article['source'] = 'scraped'
    article['audience'] = ''

    # Build topics list: start with issue topic, add article-specific topic if different
    issue_topic = ISSUE_TOPICS.get(article['issue'], '')
    article_topic = article.get('topic', '')

    topics = []
    if issue_topic:
        topics.append(issue_topic)
    if article_topic and article_topic != issue_topic:
        topics.append(article_topic)

    article['topics'] = topics
    article['topic'] = ', '.join(topics) if topics else ''

print(f"Scraped articles: {len(scraped_articles)}")

# Merge articles
all_articles = excel_articles + scraped_articles

# Deduplicate by title similarity (case-insensitive)
def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())

seen_titles = set()
unique_articles = []
for article in all_articles:
    norm_title = normalize_title(article['title'])
    if norm_title not in seen_titles and len(norm_title) > 5:
        seen_titles.add(norm_title)
        unique_articles.append(article)

# Sort by year (descending), then by title
unique_articles.sort(key=lambda x: (-x['year'], x['title']))

print(f"Unique articles after deduplication: {len(unique_articles)}")

# Get unique individual topics and years for filters
# Collect individual topics from the topics array, not the compound topic string
all_topics = set()
for a in unique_articles:
    if 'topics' in a and a['topics']:
        all_topics.update(a['topics'])
    elif a.get('topic'):
        # Fallback for Excel articles without topics array
        all_topics.add(a['topic'])
topics = sorted(all_topics)
years = sorted(set(a['year'] for a in unique_articles if a['year']), reverse=True)
audiences = sorted(set(a['audience'] for a in unique_articles if a['audience']))

# Build output
output = {
    'articles': unique_articles,
    'filters': {
        'topics': topics,
        'years': years,
        'audiences': audiences
    },
    'stats': {
        'total': len(unique_articles),
        'year_range': f"{min(years)}-{max(years)}",
        'topic_count': len(topics)
    }
}

# Write JSON
with open('articles.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nGenerated articles.json with {len(unique_articles)} articles")
print(f"Year range: {min(years)}-{max(years)}")
print(f"Topics: {len(topics)}")
