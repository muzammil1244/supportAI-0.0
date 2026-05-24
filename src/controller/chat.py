

from src.AI.agents import agent


def chat_user(body,db):


     Q = body.question

     res =  agent.invoke(Q)
     print(res.content)
     return {
          "question":body.question,
          "answer":res.content
     }
