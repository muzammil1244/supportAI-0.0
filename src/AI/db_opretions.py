from langchain.tools import tool
from src.schemas.db_schema import *

from typing import Optional
from langchain.tools import tool
from pydantic import BaseModel
from src.model.ai_operation import ai_Database
from sqlalchemy.orm import Session
from fastapi import Depends
from src.db.DataBase import get_db
from src.db.DataBase import sessionlocal
from sqlalchemy import func
from typing import Optional
from langchain.tools import tool
from datetime import date as dt_date   # safe
from datetime import datetime
from src.celery.email_send_by_date import send_email_by_date
from src.model.user import User
from fastapi import HTTPException , status
#  db = connection  --------------------------------------------------------------

db = sessionlocal()

# create and save appointment

@tool(args_schema=create_db_schema)
def create_db(
    name: str = None,
    description: str = None,
    appointment_date: str = None,   # renamed to avoid conflict: str = None,
    doctor: str = None,
    number: str = None,
    user_id : int = None
):
    """
    CREATE AND SAVE NEW APPOINTMENT
    """

    try:
        print("create operation")

        dt = datetime.strptime(appointment_date, "%Y-%m-%d")
        crunt_date = dt_date.today()



        missing_fields = []

        if not name:
            missing_fields.append("name")

        if not description:
            missing_fields.append("description")

        if not appointment_date :
            missing_fields.append("date")

        if not doctor:
            missing_fields.append("doctor")

        if not number:
            missing_fields.append("number")
        
        

        if missing_fields:
            return {
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
        if crunt_date>dt.date() :
            return {
                "message" :f"pleas provide date greater then today date"
            }

        print("create operation activate")
    

        new_appointment = ai_Database(
            name=name,
            description=description,
            date=appointment_date,
            doctor=doctor,
            number = number,
            create_by = user_id,
            create_date=dt_date.today()
        )

        # finding user data by user_id
        print(name , description, appointment_date,doctor,number,user_id,dt_date.today())
        
        user_data = db.query(User).filter( User.id == int(user_id) ).first()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user data not found by user id "
            )

        db.add(new_appointment)
        db.commit()
        seconds_diff = int((dt - datetime.now()).total_seconds())
        send_email_by_date.apply_async(
        args=[user_data.email, user_data.name, name, description, doctor, appointment_date],
        countdown=seconds_diff
)        
    

        return {
            "status": "success",
            "message": "Appointment created successfully",
            "data": {
                "name": name,
                "description": description,
                "date": appointment_date,
                "doctor": doctor,
                "number":number,
                "create at":dt_date.today()
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }


# tool fo update the appointment 

@tool(args_schema=update_db_schema)
def update_db(
    id: int,
    name: str,
    date: str,
    doctor:str,
    description:str,
    number:str,
    user_id:int
):
    """
    Update and save appointment

    Args:
    id: appointment id
    name: updated name
    date: updated date YYYY-MM-DD
    number : string 
    user_id : integer
    """

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        crunt_date = dt_date.today()
        print("update operation")

        missing_fields = []

        if not name:
            missing_fields.append("name")

        if not description:
            missing_fields.append("description")

        if not date :
            missing_fields.append("date")

        if not doctor:
            missing_fields.append("doctor")

        if not number:
            missing_fields.append("number")
        
        

        if missing_fields:
            return {
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }

        appointment = db.query(ai_Database).filter(
            ai_Database.id == id
        ).first()

        if crunt_date>dt.date() :
            return {
                "message" :f"pleas provide date greater then today date"
            }

        if not appointment:
            return f"No appointment found with id {id}"

        appointment.name = name
        appointment.date = date
        appointment.description = description
        appointment.doctor = doctor
        appointment.number = number
        db.commit()
        db.refresh(appointment)

        user_data = db.query(User).filter( User.id == int(user_id) ).first()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user data not found by user id "
            )
        seconds_diff = int((dt - datetime.now()).total_seconds())
        send_email_by_date.apply_async(
        args=[user_data.email, user_data.name, name, description, doctor, appointment_date],
        countdown=seconds_diff
)        

        return (
            f"Appointment updated successfully "
            f"id:{id}, name:{name}, date:{date}, description:{description} , doctor:{doctor},number:{number}"
        )

    except Exception as e:
        db.rollback()
        return f"Update failed: {str(e)}"


#  tool for read appointment

@tool()
def read_db(id: Optional[int] = None):

    """
    Read appointment data.

    Args:
        id: appointment id.
            If id is not provided, return all appointments.
    """

    try:
        print("read operation")


        # Return all records
        if id is None:

            appointments = db.query(ai_Database).all()

            if not appointments:
                return "No appointments found"

            result = []

            for appointment in appointments:
                result.append(
                    {
                        "id": appointment.id,
                        "name": appointment.name,
                        "description": appointment.description,
                        "date": str(appointment.date),
                        "doctor": appointment.doctor
                    }
                )

            return result

        # Return specific record
        appointment = db.query(ai_Database).filter(
            ai_Database.id == id
        ).first()

        if not appointment:
            return f"No appointment found with id {id}"

        return {
            "id": appointment.id,
            "name": appointment.name,
            "description": appointment.description,
            "date": str(appointment.date),
            "doctor": appointment.doctor
        }

    except Exception as e:
        return f"Read failed: {str(e)}"  


#  tool for delete appointment

@tool()
def delete_db(
    id: int
):
    """
    Delete appointment

    Args:
    id: appointment id

    if question has no id so just return none or nothing
    """

    try:
        print("create operation")


        appointment = db.query(ai_Database).filter(
            ai_Database.id == id
        ).first()

        if not appointment:
            return f"No appointment found with id {id}"

        db.delete(appointment)
        db.commit()

        return f"Appointment deleted successfully. id:{id}"

    except Exception as e:
        db.rollback()
        return f"Delete failed: {str(e)}"
