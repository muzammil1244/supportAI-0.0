
from langchain_linkup import LinkupSearchTool
from langchain_groq import ChatGroq
from src.AI.db_opretions import *
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_chroma import Chroma
from fastapi import HTTPException ,status
from src.redis.connection import save_message
from src.db.vector_db import vector_store
load_dotenv()


# calling groq api and create agents------------------------------------------

llm = os.getenv("SQL_GROQ_API")
agent = ChatGroq(api_key=llm,model="openai/gpt-oss-120b")
search_engine_key = os.getenv("SEARCH_KEY")


# google search agent ----------------------------------------------

tool = LinkupSearchTool(
    depth="standard",  
    output_type="sourcedAnswer",
    linkup_api_key=search_engine_key,  
    timeout=120
)


# vector db : --------------------------------------------------------




# NODES CHILDREN -----------------------------------------------------

def google_search(state):

    try:

        res = tool.invoke(state.qna)
       

        return {
        "ans": [str(res.answer)]
    }


    except Exception as e:

        print("Google Search Error:", e)

        return {
        "ans": [f"Search service unavailable Cause : {str(e)} "]
    }


def RAG_search(state):


#   print("Vector_DB",Vector_DB)
#   print("Vector_DB._collection.count()",Vector_DB._collection.count())
#   print(type(Vector_DB))

    try:

        history_text = "\n".join(
    f"{msg['role']}: {msg['content']}"
    for msg in state.history[-5:]
)
        qn = state.qna
        
        if not qn :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pleas provide the questions"
            )


        result = vector_store.similarity_search(query=qn,k=2)

    
        
        # print("ruf result of rag : ",result)

        answer = []
        for doc, score in result:
            # print("SCORE:", score)
            # print(doc.page_content[:500])
            # print("="*50)
            answer.append(doc.page_content)


        context = " ".join(answer)
        # print( "RAG ANS",context)

        result = agent.invoke(f"""
You are an AI assistant.

Previous Conversation:
{history_text}

Current Question:
{state.qna}

Context:
{context}

Instructions:
- Use the conversation history only to understand references
  like "it", "he", "that", "this", etc.
- Use the Context as the primary source of facts.
- If the answer is not in the Context, say:
  "I could not find sufficient information in the provided context."
- Do not make up facts.

Answer:
""")

        return {
                "ans": [result.content]
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error from rag system : {str(e)}"
        )


# tools for DB Operations ---------------------------------------------------

tools =[
    create_db,
    update_db,
    read_db,
    delete_db
]


# DB agent : -------------------------------------------------------------------------

db_agent = create_agent(agent
                        ,tools=tools,
#                         system_prompt=f"""

# You are an Appointment Database Agent.

# Your job is to perform CRUD operations using the provided tools only.

# Rules:

# * Always use tools for CRUD operations.
# * Never answer from your own knowledge.
# * Never generate SQL queries.
# * Never explain database operations.
# *if i say in question like create add and save word for appointment so just call create_db tool
# *if i say in question like read show and give appointment so just call read_db tool
# *if i say update in question so just call update_db tool
# *if i say delete in question so just call delete_db tool
# * Return tool results directly.
# *if user wanna update appointment and he give only on or tow argument value so just return args from history 

# Data Formatting only for create_db tool and update_db tool:

# if you calling read_db and update_db tool so follow this formate
# * Convert all names to UPPERCASE before passing them to tools.
# * if doctor name comes with different spell or similar spell so just return Nearest doctor name 
# * Convert all dates to YYYY-MM-DD format before passing them to tools.
# * Remove extra spaces from inputs.

# Doctor Names:

# * Valid doctors:

#   * DR.RAMESH
#   * DR.SURESH
#   * DR.MISHRA

# Missing Data Rules:

# * If required information is missing, ask only for the missing fields.
# * Never guess values.
# * Never create fake names, dates, doctors, or descriptions.

# Tool Usage:

# * create_db → create appointment
# * read_db → read/search appointment
# * update_db → update appointment
# * delete_db → delete appointment

# Arguments:

# *create_db : for this tool you have to send (name,description,number,appointment_date,doctor,doctor and user_id only in integer)
# *read_db   : for this tool you have to send (id) in integer
# *update_db    : for this tool you have to send (name,description,appointment_date,doctor,number)
# *delete_db   : for this tool you have to send (id) in integer

# Important:

# * If a tool returns data, return that data exactly.
# * Do not summarize tool output.
# * Do not modify tool output.
# * Do not add explanations.
# * Do not generate code examples.
# * if date exist return it in table format rows ans columns
# * If no record exists, return "No matching record found."
# *never send name description date and doctor name argument to read_db and delete_db tools



# major points :
# You MUST use tool output.

# Never say record not found if tool returned data.

# If tool returns JSON,
# convert it into a human readable response.

# """
  system_prompt="""
You are a smart Appointment Database Agent for a hospital.

Your job is to extract appointment data from natural, informal, broken, or casual language
and perform CRUD operations using the provided tools ONLY.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — UNDERSTAND INTENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Detect what the user wants from their natural language:

| Intent Keywords / Patterns                              | Tool to Call  |
|---------------------------------------------------------|---------------|
| book, add, create, save, i want, i need, i have come,   |               |
| please fix, set, register, i want to visit, schedule    | create_db     |
| show, give, read, find, check my appointment, tell me   | read_db       |
| update, change, reschedule, modify, shift               | update_db     |
| cancel, delete, remove                                  | delete_db     |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — EXTRACT FIELDS FROM NATURAL LANGUAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Even if the user writes casually or in broken English/Hindi, extract these fields:

┌─────────────────┬────────────────────────────────────────────────────────────────────┐
│ Field           │ How to Extract                                                     │
├─────────────────┼────────────────────────────────────────────────────────────────────┤
│ name            │ Look for "my name is", "I am", "mera naam", or standalone names    │
│ number          │ Any 10-digit phone number in the text                               │
│ doctor          │ "to dr", "doctor", "dr.", match to nearest valid doctor name        │
│ appointment_date│ "on", "at", "day X month Y", "X/Y/Z", "5 day 8 month 2026"         │
│ description     │ Reason for visit: "check", "pain", "fever", "mouth", "teeth",      │
│                 │ "chek my mout", "eye", "back pain", "follow up" etc.               │
│                 │ If user says "chek my mout" → description = "Mouth/Dental Checkup" │
│                 │ If not mentioned, set description = "General Checkup"              │
│ user_id         │ Always taken from the provided user_id in the message              │
└─────────────────┴────────────────────────────────────────────────────────────────────┘

DESCRIPTION EXTRACTION EXAMPLES (most important):
- "chek my mout"          → "Mouth/Dental Checkup"
- "check my eyes"         → "Eye Checkup"
- "fever and cold"        → "Fever and Cold"
- "back pain"             → "Back Pain"
- "routine checkup"       → "General Checkup"
- "follow up"             → "Follow-up Visit"
- "sugar check"           → "Diabetes/Sugar Checkup"
- "pet dard"              → "Stomach Pain"
- "sir dard"              → "Headache"
- nothing mentioned       → "General Checkup"

DATE EXTRACTION EXAMPLES:
- "5 day 8 month 2026"    → 2026-08-05
- "5/8/2026"              → 2026-08-05
- "August 5"              → 2026-08-05
- "kal"                   → tomorrow's date
- "aaj"                   → today's date

DOCTOR NAME MATCHING (fuzzy match to nearest valid name):
Valid doctors:
  - DR.RAMESH
  - DR.SURESH
  - DR.MISHRA

Examples:
- "dr ramesh", "Dr Ramesh", "ramesh doctor"  → DR.RAMESH
- "dr suresh", "surash", "suresh sir"        → DR.SURESH
- "mishra", "dr mishra", "dr. mishra"        → DR.MISHRA

NAME FORMATTING:
- Convert all patient names to UPPERCASE
- Example: "muzammil" → "MUZAMMIL"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — TOOL ARGUMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

create_db  → name (str, UPPERCASE), description (str), number (str),
             appointment_date (YYYY-MM-DD), doctor (str), user_id (int)

read_db    → id (int only)
             ⚠ NEVER send name, date, doctor, description to read_db

update_db  → name, description, appointment_date, doctor, number
             (only send fields that are changing; get rest from history)

delete_db  → id (int only)
             ⚠ NEVER send name, date, doctor, description to delete_db

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — MISSING FIELDS RULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before calling create_db, confirm you have:
  ✅ name
  ✅ number
  ✅ doctor
  ✅ appointment_date
  ✅ description (if missing → use "General Checkup")
  ✅ user_id (from message)

If name, number, doctor, OR date is missing → ask ONLY for that missing field.
NEVER guess. NEVER fake. NEVER assume a name or date.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — OUTPUT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Return tool results directly — do not summarize or modify.
- If tool returns JSON → convert to clean human-readable format.
- If data has dates → show in a table (rows and columns).
- If no record found → return "No matching record found."
- Do NOT generate SQL.
- Do NOT explain operations.
- Do NOT add code examples.
"""
)

def DB_search(state):
    try:

        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in state.history[-5:]
        )

        res = db_agent.invoke(
            {
                
               "messages": [
            {
                "role": "user",
                "content": f"""
Previous Conversation:
{history_text}

Current Question:
{state.qna}

user_id: {state.user_id}
"""
            }
        ]
            }
        )

        result = res["messages"][-1].content

        return {
            "ans": [str(result)]
        }

    except Exception as e:
         return {
        "ans":f" issue: {str(e)}"
    }


def LLM_search(state):
    try:
        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in state.history
        )

        res = agent.invoke(f"""
        You are a helpful AI assistant.

        Previous Conversation:

        {history_text}

        Current User Question:

        {state.qna}

        Rules:
        - Use previous conversation when relevant.
        - If the current question refers to previous messages,
        use the conversation history.
        - Answer clearly and briefly.
        """)


        # print("result from llm search",res.content)
        return{
            "ans":[res.content]
        }
    except Exception as e :
        raise HTTPException(
            statuc_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error from llm search detail : {str(e)}"
        )
       
    

# final node where the all answer combination execute and become perfect answer 
# or right answer 

def final_node_ans(state):
    
    try:

        q =  state.qna
        save_message(

           user_id= state.user_id,
           role= " user",
           content=q

            
            )

        an = "\n".join(state.ans)

        response = agent.invoke(
        f"""
    Question: {q}

    Answers:
    {an}

    Your are final answer generate that generate answer as per given question and there answer
    """
    )
        
        save_message(
            user_id=state.user_id,
            role="assistance",
            content=response.content
        )
        return {
            "final_answer": response.content
        }
    
    except Exception as e :
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"error from final answer generater node detail : {str(e)}"
        )