from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph ,START,END
from src.schemas.graph_schema import Query , Q_res
from src.AI.agents import google_search,RAG_search,final_node_ans,DB_search,LLM_search
from fastapi import HTTPException , status
from src.redis.connection import get_messages





load_dotenv()


# graph and agent build with calling groq api

llm = os.getenv("GROQ_API")
agent = ChatGroq(api_key=llm,model="openai/gpt-oss-120b")
graph_state = StateGraph(Query)



# get history ----------------------------------


# verify_node help to take question from user and analyse that and return the type of node which they gonna call

def verify_node(state: Query):

    try:
       
        structured_llm = agent.with_structured_output(Q_res,method="json_mode")
        print("Q_res.model_json_schema()", Q_res.model_json_schema())


        history_text = "\n".join(
    f"{msg['role']}: {msg['content']}"
    for msg in state.history[-10:]
)

        res = structured_llm.invoke(
[
   {
    "role": "system",
    "content": f"""
You are an intelligent routing agent for a hospital assistant system.

Your ONLY job is to analyze the user's question and route it to the correct node.
You must be smart enough to understand INTENT — not just keywords.

---

Conversation History:
{history_text}

Current User Question:
{state.qna}

---

## CONTEXT UNDERSTANDING RULES

Use conversation history to resolve pronouns and references like:
- "it", "this", "that", "same", "previous", "again", "those"

Example:
- History: "What are your hospital timings?"
- Current: "What about on Sundays?"
- → This is still about hospital info → RAG_search

---

## NODE DEFINITIONS & SMART ROUTING

### 1. `DB_operations` — HIGHEST PRIORITY
Use when user wants to manage appointments (CRUD).
Trigger on any intent related to booking, scheduling, viewing, updating, or canceling appointments.

Smart triggers (even without exact keywords):
- "I want to see a doctor tomorrow" → book appointment
- "Can I come at 3pm?" → book appointment
- "Change my slot" → update appointment
- "I don't want the appointment anymore" → delete appointment
- "When is my next visit?" → view appointment
- "Is Dr. Sharma free on Friday?" → check/book appointment

Keywords: book, appointment, schedule, slot, visit, reschedule, cancel, check-in, availability

---

### 2. `RAG_search` — HOSPITAL KNOWLEDGE BASE
Use when the user is asking about THIS hospital, its services, staff, policies, or internal information.

The key signal is: "the answer lives in this hospital's private knowledge base."

Smart triggers (user does NOT need to say "search RAG"):
- Anything about the hospital's doctors, departments, specializations
- Hospital address, location, contact, timings, working hours
- Hospital fees, packages, procedures, facilities
- Hospital policies, insurance, rules
- Anything prefixed with "your", "you", "this hospital", "do you", "does this hospital"

Examples:
- "Do you have a cardiologist?" → RAG_search
- "What are your OPD hours?" → RAG_search
- "How much does an X-ray cost here?" → RAG_search
- "Is there parking available?" → RAG_search
- "Which doctors are available today?" → RAG_search
- "Tell me about your hospital" → RAG_search
- "Do you accept insurance?" → RAG_search

Do NOT use RAG_search for general medical knowledge (e.g., "What is diabetes?")

---

### 3. `google_search` — REAL-TIME / INTERNET INFO
Use when the answer requires current, live, or recent information from the internet.

Smart triggers:
- Latest news, today's updates, live data
- Current weather, stock prices, sports scores
- Events happening now or recently
- Anything that changes frequently and needs internet

Examples:
- "What's the weather today?" → google_search
- "Latest COVID guidelines?" → google_search
- "Current price of medicine X?" → google_search

---

### 4. `LLM_node` — GENERAL KNOWLEDGE
Use for universal knowledge, explanations, definitions, and educational queries.

Smart triggers:
- Medical knowledge (symptoms, diseases, treatments — in general, not specific to this hospital)
- Technology, science, history, coding questions
- "What is...", "How does...", "Explain..."

Examples:
- "What are symptoms of diabetes?" → LLM_node
- "How does an MRI work?" → LLM_node
- "What is blood pressure?" → LLM_node
- "Explain Python" → LLM_node

---

## PRIORITY ORDER (when in doubt)

1. DB_operations — if any appointment/scheduling intent exists
2. RAG_search — if question is about THIS hospital specifically
3. google_search — if real-time/internet data needed
4. LLM_node — everything else (general knowledge)

---

## OUTPUT RULES

- Return ONLY valid JSON — no explanation, no extra text.
- Choose EXACTLY one node.

Valid outputs:
{{"qna_type": ["DB_operations"]}}
{{"qna_type": ["RAG_search"]}}
{{"qna_type": ["google_search"]}}
{{"qna_type": ["LLM_node"]}}
"""
},
    {
        "role": "user",
        "content": state.qna
    }
]
)
        # print("response", res.model_dump())

        return {
            "qna_type": res.qna_type
        }
    
    except Exception as e :
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                           detail=f"error to verify question just try to ask in different way : {str(e)}" )


# condition node its hell to call node and it s return array
# for example
#  ["Rag_search","db_search"]

def condition_nod(state:Query):

    return state.qna_type


# NODES --------------------------------------------------------

def google_search_node(state:Query):
    return google_search(state)

def RAG_search_node(state:Query):
    return RAG_search(state)

def DB_operations_node(state:Query):
    return DB_search(state)

def LLM__node(state:Query):
    return LLM_search(state)

def final_node(state:Query):
    return final_node_ans(state)


# ADD NODES ---------------------------------------------------------

graph_state.add_node("verify_Q",verify_node)
graph_state.add_node("google_search",google_search_node)
graph_state.add_node("RAG_search",RAG_search_node)
graph_state.add_node("DB_operations",DB_operations_node)
graph_state.add_node("final_node",final_node)
graph_state.add_node("LLM_node",LLM__node)


# ADD NODES WITH EDGES -----------------------------------------------

graph_state.add_edge(START,"verify_Q")
# conditional node-------------------------
graph_state.add_conditional_edges("verify_Q",condition_nod)
# ------------------------------------------------------------------------
graph_state.add_edge("google_search" , "final_node")
graph_state.add_edge("RAG_search" , "final_node")
graph_state.add_edge("DB_operations" , 'final_node')
graph_state.add_edge("LLM_node" , 'final_node')
graph_state.add_edge("final_node" , END)


# Compiling GRAPH ----------------------------------------------------------------------
dinal_graph = graph_state.compile()












    




