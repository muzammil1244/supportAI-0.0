from src.model.ai_operation import ai_Database
from fastapi import HTTPException , status

def read_appointments_controller(db):

    try:

        data = db.query(ai_Database).all()

        users = [
    {
         "id" : user.id,
    "name" :user.name,
    "description" : user.description,
    "date" : user.date,
    "doctor" :user.doctor,
    "number" : user.number,
    "create_at":user.create_date

    }
    for user in data
    
        ]

        return users
    
    except Exception as e :

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error from the read appointment detail : {str(e)}"
        )



def delete_appointment_controller(db, appointment_id: int):
    try:
        # Finde the oppointment by ID
        appointment = db.query(ai_Database).filter(ai_Database.id == appointment_id).first()

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appointment with id {appointment_id} not found"
            )

        # Dlete the appointment
        print(appointment)
        db.delete(appointment)
        db.commit()

        return {"message": f"Appointment with id {appointment_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting appointment: {str(e)}"
        )
