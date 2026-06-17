from fastapi import APIRouter,status,UploadFile , File
from src.AI.Rag import upload_controller
from fastapi import Depends
from src.db.DataBase import get_db
from sqlalchemy.orm import Session
from src.controller.admin import read_appointments_controller,delete_appointment_controller
from src.helper.is_admin import is_admin



admin_route = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@admin_route.post("/upload",status_code=status.HTTP_201_CREATED)
async def upload_document_route(file_data:UploadFile = File(),user = Depends(is_admin)):
    return await  upload_controller(file_data)
        # return {"filenames": [f.filename for f in file_data]}

@admin_route.get("/read/appointments")
def read_appointment_routs(db :Session =Depends(get_db) , user = Depends(is_admin)):
    return read_appointments_controller(db)

@admin_route.delete("/delete/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db=Depends(get_db),user = Depends(is_admin)):
    return delete_appointment_controller(db, appointment_id)
