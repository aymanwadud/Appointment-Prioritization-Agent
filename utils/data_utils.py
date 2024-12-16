import json
import os
from datetime import datetime

def load_data(filename):
    if os.path.exists(filename):
       with open(filename, 'r') as file:
          try:
             return json.load(file)
          except json.JSONDecodeError:
            return []
    return []

def save_data(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok = True)
    with open(filename, 'w') as file:
        json.dump(data, file, indent = 4)

def get_next_appointment_id(appointments):
    today = datetime.today().strftime("%Y-%m-%d")
    if not appointments:
        return today + "-1"
    max_id = 0
    for appointment in appointments:
        appointment_id = appointment.get("appointment_id", None)
        if appointment_id:
           parts = appointment_id.split("-")
           if parts[0] == today:
               try:
                    max_id = max(max_id, int(parts[1]))
               except:
                  continue
    
    return f"{today}-{max_id+1}"