from datetime import timedelta

WORKING_HOURS = ["09:00", "17:00"]
APPOINTMENT_DURATION = timedelta(minutes=30)
PRIORITY_FACTORS = {"fever": 10, "emergency": 20, "headache": 5}