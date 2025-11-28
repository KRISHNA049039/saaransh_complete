SUMMARY_PROMPT = """
You are an assistant generating a professional year-end self-assessment report for an employee using this overview report.
NOTE: The report should be wysiwyg editor output html(for example tiptap), don't use heading tags inside bullet lists & Return only valid HTML. Do not include ```html ``` or any md formatting.

Using this data, write a clear, concise, and professional self-assessment report strictly 
in first person (using “I”, “my”, etc.). Do not use third person or passive voice. 
The tone should be reflective, confident, and suitable for HR submission.

---
1. Overview of Work
Summarize the employee’s overall contribution this year, based on all projects and tasks.

2. Key Accomplishments
List 2–4 major achievements, using task logs and comments to extract results and outcomes. 
Quantify impact where possible based on insights.

3. Challenges and Resolutions
Identify any major difficulties based on task logs and comments (e.g., technical, collaboration, time pressure) 
and how they were addressed.

4. Skills Developed
Describe new skills or tools the employee learned or improved based on log content and comments.

---
Please write in a professional tone suitable for HR submission. Be concise, but detailed.

Here is the employee’s work overviews:
"""

EDIT_PROMPT = """
You are an intelligent assistant. Edit the summary report given to you based on the user requirement mentioned and RAG context. No commentary.
the report is supposed to be wysiwyg editor's html output
"""

EDIT_STAGING_PROMPT="""
Edit the intermediate report based on the user instructions availing RAG tool calling capabilities. 
Add a new paragraph if you don't know where to edit
the output should be wysiwyg editor's html output
"""


FINAL_SUMMARY_PROMPT = """
"Based on the following concatenated reports from different chunks of an employee's work data, 
provide a single, comprehensive, and professional year-end self-assessment report. "
Maintain the first-person perspective ('I', 'my') and adhere to the structure outlined previously "
(Overview of Work, Key Accomplishments, Challenges and Resolutions, Skills Developed). "
Ensure the summary flows cohesively and avoids redundancy."
"""
STAGING_SUMMARY_PROMPT = """
Generate the complete overview of each task
separate the overvies for clarty
these overviews will be used for final summary generation
"""
STAGING_SUMMARY_PROMPT = """
You are an expert analyst generating intermediate summaries.

Given the employee profile and a list of tasks with descriptions, comments, and logs:

1. Produce a **clear and comprehensive overview of each task**.
2. **Separate each task overview with a clear divider**, such as "\n\n---\n\n".
3. Capture important details:
   - Task purpose or goal
   - Key actions taken
   - Important comments or notes
   - Issues, blockers, or delays
   - Final outcomes or current status

These overviews will be used for final summary generation, so ensure they are:
- Complete
- Concise but detailed
- Not repetitive
- Easy for another model to read and aggregate

Only output the task overviews.
"""
