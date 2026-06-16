
from src.redis.connection import get_messages
from fastapi import HTTPException , status
def get_history(user_id):

    try:
        user_id_key = user_id['id']

        messages =get_messages(user_id=user_id_key)
        return messages
    except Exception as e :
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error from chat history detail : {str(e)}"
        )
        



      
