
from src.AI.ai_main import graph_state , dinal_graph


def chat_agent(body,db,user,history):
     # print("chat controller called")
     # print("history =", history)
     # print("type =", type(history))
     result = dinal_graph.invoke({
     "qna": body.qna,
     "user_id":user["id"],
     "history":history
     })
     return result


