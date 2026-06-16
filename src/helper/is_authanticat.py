from fastapi import Request , HTTPException,status
import jwt
from dotenv import load_dotenv
import os
# auth register controller

load_dotenv()
sec_key = os.getenv("SECRETE_KY")






def is_authenticated(body:Request,):

    data = body.headers["authorization"]

    token = data.split(" ")[-1]
    if not token:
     
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=" token is not founded"
        )
    
   
    try:

        is_authenticated = jwt.decode(
            token,
            key=sec_key,
            algorithms=["HS256"]
        )

        print(is_authenticated)
        return is_authenticated

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    


    

