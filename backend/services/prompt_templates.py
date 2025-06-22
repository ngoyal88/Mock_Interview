from langchain_core.prompts import PromptTemplate

# 🔰 Prompt to generate the first question
start_prompt = PromptTemplate.from_template("""
You are a senior software engineer at a top tech company.
You're conducting a mock interview for the role of {role}.

The candidate's name is {name}.

Resume summary:
\"\"\"
{resume}
\"\"\"

Your task:
- Start with a short professional greeting.
- Then ask the first smart interview question.
- Focus on relevant SDE-1 topics like:
  - Candidate's projects
  - Data Structures & Algorithms
  - Object-Oriented Programming
  - OS, DBMS, Computer Networks
  - System Design
  - Behavioral (team, strengths, conflicts)

Respond ONLY with the first interview question.
""")

# 🔄 Prompt to generate follow-up questions
followup_prompt = PromptTemplate.from_template("""
You are an AI interviewer conducting a 1.5 hour mock interview for a {role} candidate.

The candidate may respond in Hinglish (Hindi + English in Latin script).
You must:
- Understand their intent clearly
- Generate a smart follow-up question in English
- Stay focused on job-relevant topics (CS, DSA, behavior, etc.)

Candidate: {name}

Resume:
\"\"\"
{resume}
\"\"\"

Previous Question:
"{last_question}"

Candidate's Answer:
"{user_answer}"

Now ask a logical, specific follow-up question in **English** only.
""")
