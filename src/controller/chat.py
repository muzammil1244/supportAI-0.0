
from src.AI.ai_main import graph_state , dinal_graph
from fastapi import HTTPException , status
from src.model.user import User
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


def user_profile(user,db):
     id = user["id"]
     print(id , " use id " , type(id))
     try :

       user_data = db.query(User).filter(User.id == id).first()
       print(
            {
    "id": user_data.id,
    "name": user_data.name,
    "email": user_data.email
}
       )

       return {
           "id": user_data.id,
    "name": user_data.name,
    "email": user_data.email
       }


       
       
     
     except :
          raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="use data not found "
          )