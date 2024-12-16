from datetime import datetime
from utils.data_utils import load_data, save_data
class CheckInAgent:
    def __init__(self, data_dir = "data/"):
       self.data_dir = data_dir
       self.filename_prefix = "appointments_"

    def _get_filename(self, date):
       return self.data_dir + self.filename_prefix + str(date) + ".json"

    def check_in(self, appointment_id):
        date = datetime.strptime(appointment_id.split("-")[0], "%Y-%m-%d").date()
        appointments = load_data(self._get_filename(date))
        for appointment in appointments:
            if appointment['appointment_id'] == appointment_id:
                appointment['status'] = "checked_in"
                save_data(appointments, self._get_filename(date))
                return {"status": "success", "message": "Patient checked in"}
        return {"status": "error", "message": "Appointment not found"}

    def get_patient_status(self, patient_id, date):
        appointments = load_data(self._get_filename(date))
        if not appointments:
            return {"status": "error", "message": "No appointments for the date"}
        for appointment in appointments:
           if appointment['patient_id'] == patient_id:
                return appointment
        return {"status": "error", "message": "Appointment not found"}

if __name__ == '__main__':
   agent = CheckInAgent()
   print(agent.check_in("2024-08-22-1"))
   print(agent.get_patient_status(1, datetime.strptime("2024-08-22", "%Y-%m-%d").date()))