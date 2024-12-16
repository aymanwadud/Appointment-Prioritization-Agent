import streamlit as st
from datetime import date
from agents.appointment_agent import AppointmentAgent
from agents.checkin_agent import CheckInAgent
from agents.prioritization_agent import PrioritizationAgent

# Initialize Agents
appointment_agent = AppointmentAgent()
checkin_agent = CheckInAgent()
prioritization_agent = PrioritizationAgent()

def book_appointment_form():
    st.header("Book Appointment")
    with st.form("book_appointment"):
        patient_id = st.number_input("Patient ID", value=1)
        physician_id = st.number_input("Physician ID", value=1)
        appointment_date = st.date_input("Appointment Date", value=date.today())
        appointment_time = st.text_input("Appointment Time", placeholder="HH:MM", value="10:00")
        reason = st.text_input("Reason for appointment", placeholder="Regular checkup")
        submit = st.form_submit_button("Book Appointment")
        if submit:
            result = appointment_agent.book_appointment(patient_id, physician_id, appointment_date, appointment_time, reason)
            if result["status"] == "success":
                st.success(f"Appointment booked with ID: {result['appointment_id']}")
            else:
                st.error(result["message"])


def reschedule_appointment_form():
    st.header("Reschedule Appointment")
    with st.form("reschedule_appointment"):
        appointment_id = st.text_input("Appointment ID", placeholder = "YYYY-MM-DD-id")
        new_date = st.date_input("New Date", value=date.today())
        new_time = st.text_input("New Time", placeholder = "HH:MM")
        submit = st.form_submit_button("Reschedule Appointment")
        if submit:
           result = appointment_agent.reschedule_appointment(appointment_id, new_date, new_time)
           if result["status"] == "success":
                st.success(result['message'])
           else:
                 st.error(result["message"])


def cancel_appointment_form():
   st.header("Cancel Appointment")
   with st.form("cancel_appointment"):
      appointment_id = st.text_input("Appointment ID", placeholder = "YYYY-MM-DD-id")
      submit = st.form_submit_button("Cancel Appointment")
      if submit:
         result = appointment_agent.cancel_appointment(appointment_id)
         if result["status"] == "success":
                st.success(result["message"])
         else:
            st.error(result["message"])

def check_in_form():
   st.header("Check In")
   with st.form("check_in"):
       appointment_id = st.text_input("Appointment ID", placeholder = "YYYY-MM-DD-id")
       submit = st.form_submit_button("Check In")
       if submit:
           result = checkin_agent.check_in(appointment_id)
           if result["status"] == "success":
              st.success(result["message"])
           else:
               st.error(result["message"])


def patient_status_form():
    st.header("Patient Status")
    with st.form("patient_status"):
        patient_id = st.number_input("Patient ID", value = 1)
        appointment_date = st.date_input("Appointment Date", value = date.today())
        submit = st.form_submit_button("Get Status")
        if submit:
          result = checkin_agent.get_patient_status(patient_id, appointment_date)
          if result["status"] == "success":
               st.write(f"Appointment: {result}")
          else:
              st.error(result['message'])

def show_priority_queue():
     st.header("Prioritized Queue")
     appointment_date = st.date_input("Appointment Date", value = date.today())
     prioritized_queue = prioritization_agent.get_prioritized_queue(appointment_date)
     st.write(prioritized_queue)


def update_priority_factors():
    st.header("Update Priority Factors")
    with st.form("update_priority_factors"):
        st.write("Current Priority Factors:")
        st.write(prioritization_agent.PRIORITY_FACTORS)
        factors = st.text_input("Priority Factors (seperated by commas)", placeholder = "fever=10, headache=5")
        submit = st.form_submit_button("Update Priority Factors")
        if submit:
            config = {}
            for factor in factors.split(','):
               factor_key, factor_value = factor.split("=")
               config[factor_key.strip()] = int(factor_value)
            prioritization_agent.update_priority_factor(config)
            st.success("Priority Factors updated")

def main():
    st.title("Physician Chamber AI System")
    menu = ["Book Appointment", "Reschedule Appointment", "Cancel Appointment", "Check In", "Patient Status", "Show Prioritized Queue", "Update Priority Factors"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Book Appointment":
        book_appointment_form()
    elif choice == "Reschedule Appointment":
        reschedule_appointment_form()
    elif choice == "Cancel Appointment":
        cancel_appointment_form()
    elif choice == "Check In":
        check_in_form()
    elif choice == "Patient Status":
         patient_status_form()
    elif choice == "Show Prioritized Queue":
        show_priority_queue()
    elif choice == "Update Priority Factors":
        update_priority_factors()


if __name__ == "__main__":
    main()