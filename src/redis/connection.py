import redis
import os
from dotenv import load_dotenv
import json
load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
    username=os.getenv("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)






def save_message(user_id, role, content):

    key = f"chat:{user_id}"

    message = {
        "role": role,
        "content": content
    }

    redis_client.rpush(
        key,
        json.dumps(message),
        
    )
    redis_client.expire(key,86400)


def get_messages(user_id):

    key = f"chat:{user_id}"

    messages = redis_client.lrange(
        key,
        0,
        -1
    )

    return [json.loads(msg) for msg in messages]


def clear_chat(user_id):

    redis_client.delete(
        f"chat:{user_id}"
    )