import json
from datetime import datetime
from utils.data_utils import load_data, save_data, get_next_appointment_id
from utils.config import WORKING_HOURS, APPOINTMENT_DURATION

class AppointmentAgent:
    def __init__(self, data_dir = "data/"):
        self.data_dir = data_dir
        self.filename_prefix = "appointments_"
    
    def _get_filename(self, date):
        return self.data_dir + self.filename_prefix + str(date) + ".json"

    def book_appointment(self, patient_id, physician_id, date, time, reason):
        appointments_by_date = load_data(self._get_filename(date))
        if not appointments_by_date:
            appointments_by_date = []
        
        
        if not self.is_available(physician_id, date, time):
             return {"status": "error", "message": "Time slot is not available"}
        
        appointment_id = get_next_appointment_id(appointments_by_date)
        
        appointment = {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "physician_id": physician_id,
            "date": str(date),
            "time": str(time),
            "status": "booked",
            "reason": reason,
            "priority_score": 0
        }
        appointments_by_date.append(appointment)
        save_data(appointments_by_date, self._get_filename(date))
        return {"status": "success", "appointment_id": appointment_id}

    def reschedule_appointment(self, appointment_id, new_date, new_time):
        date = datetime.strptime(appointment_id.split("-")[0], "%Y-%m-%d").date()
        appointments = load_data(self._get_filename(date))
        for appointment in appointments:
            if appointment['appointment_id'] == appointment_id:
                appointment['date'] = str(new_date)
                appointment['time'] = str(new_time)
                save_data(appointments, self._get_filename(date))
                return {"status": "success", "message": "Appointment rescheduled"}
        return {"status": "error", "message": "Appointment not found"}

    def cancel_appointment(self, appointment_id):
        date = datetime.strptime(appointment_id.split("-")[0], "%Y-%m-%d").date()
        appointments = load_data(self._get_filename(date))
        for i, appointment in enumerate(appointments):
            if appointment['appointment_id'] == appointment_id:
                 del appointments[i]
                 save_data(appointments, self._get_filename(date))
                 return {"status": "success", "message": "Appointment cancelled"}
        return {"status": "error", "message": "Appointment not found"}

    def get_available_slots(self, physician_id, date):
        start_time = datetime.combine(date, datetime.strptime(WORKING_HOURS[0], "%H:%M").time())
        end_time = datetime.combine(date, datetime.strptime(WORKING_HOURS[1], "%H:%M").time())
        
        appointments_by_date = load_data(self._get_filename(date))
        booked_slots = []
        if appointments_by_date:
          for apt in appointments_by_date:
             if apt['physician_id'] == physician_id:
                 booked_slots.append(datetime.combine(date, datetime.strptime(apt['time'], "%H:%M").time()))
        
        
        available_slots = []
        current_time = start_time
        while current_time < end_time:
            if current_time not in booked_slots:
                available_slots.append(current_time.strftime("%H:%M"))
            current_time = current_time + APPOINTMENT_DURATION
        
        return available_slots
    
    def is_available(self, physician_id, date, time):
        start_time = datetime.combine(date, datetime.strptime(WORKING_HOURS[0], "%H:%M").time())
        end_time = datetime.combine(date, datetime.strptime(WORKING_HOURS[1], "%H:%M").time())
        appointment_time = datetime.combine(date, datetime.strptime(time, "%H:%M").time())
        
        if appointment_time < start_time or appointment_time >= end_time:
            return False
        
        
        appointments_by_date = load_data(self._get_filename(date))
        if appointments_by_date:
         for apt in appointments_by_date:
             if apt['physician_id'] == physician_id and apt['time'] == time:
               return False
        return True
    
if __name__ == '__main__':
   agent = AppointmentAgent()
   print(agent.book_appointment(1, 1, "2024-08-22", "10:00", "Regular checkup"))
   print(agent.book_appointment(2, 1, "2024-08-22", "10:30", "Fever"))
   print(agent.book_appointment(2, 1, "2024-08-22", "10:30", "Fever")) # This one should fail
   print(agent.reschedule_appointment("2024-08-22-1", "2024-08-22", "13:00"))
   print(agent.cancel_appointment("2024-08-22-2"))
   print(agent.get_available_slots(1, datetime.strptime("2024-08-22", "%Y-%m-%d").date()))
   print(agent.is_available(1, datetime.strptime("2024-08-22", "%Y-%m-%d").date(), "10:00"))
   print(agent.is_available(1, datetime.strptime("2024-08-22", "%Y-%m-%d").date(), "10:30"))