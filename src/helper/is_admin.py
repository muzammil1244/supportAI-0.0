from fastapi import Request , HTTPException,status
import jwt
from dotenv import load_dotenv
import os
# auth register controller

load_dotenv()
sec_key = os.getenv("SECRETE_KY")





def is_admin(request: Request):
    data = request.headers.get("authorization")
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = data.split(" ")[-1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found"
        )

    try:
        decoded = jwt.decode(token, key=sec_key, algorithms=["HS256"])

        if decoded.get("role") == "admin1244@gmail.com":
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only admin allowed"
            )

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

