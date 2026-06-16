from src.model.user import User
from pwdlib import PasswordHash
from fastapi import HTTPException  , status
import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from src.celery.email_send import send_email
# auth register controller

load_dotenv()
sec_key = os.getenv("SECRETE_KY")
token_exp  = int(os.getenv("TOKEN_EXP"))
hash_password = PasswordHash.recommended()


def register(body,db):

   try:
            new_user = User(

                name = body.name,
                email = body.email,
                password = hash_password.hash(body.password)
            )

            db.add(new_user)
            db.commit()
            return {
                  "message":"user created successfuly"
            }
   except Exception as e:

    print(e)

    return {
        "message": "user register error"
    }
    





  


# auth login controller
def login(body,db):
    is_user = db.query(User).filter(User.email == body.email).first()
    if not is_user:
        raise HTTPException(detail="email is not registered" , status_code=status.HTTP_401_UNAUTHORIZED)
   
    
    is_correct_pass = hash_password.verify(body.password  ,is_user.password)

    if not is_correct_pass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong password"
        )
    send_email(to=is_user.email)
    expire = datetime.utcnow() + timedelta(minutes=token_exp)
    
    payload = {
        "id": is_user.id,
        "role":is_user.email,
        # "exp" : int(expire.timestamp())
     

    }


    token = jwt.encode(payload=payload,key=sec_key,algorithm="HS256",)



   
   
   
    return {
        "message":"user login",
        "token":token
    }

