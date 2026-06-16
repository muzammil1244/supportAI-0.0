from pydantic import BaseModel, Field
from typing import Literal , List , Annotated 
from operator import add
class Query(BaseModel):

    qna: str = Field(default="hi")

    user_id : int = 0

    ans: Annotated[list[str], add]  = Field(default_factory=list)

    qna_type: List[str] = Field(
        default_factory=lambda: ["google_search"]
    )   
    final_answer: str = ""

    history: List = Field(default_factory=list)


class Q_res(BaseModel):

    qna_type: List[
        Literal[
            "google_search",
            "RAG_search",
            "DB_operations",
            "LLM_node"
            
        
        ]
    ] = Field(
        default_factory=lambda: ["google_search"]
    )