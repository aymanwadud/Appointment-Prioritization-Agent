import pdfplumber
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
import os
import sys

# Check if running as a script or module
if __name__ == '__main__':
    # If running as a script, add the project directory to sys.path
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_dir)

from utils.config import DATABASE_URL

Base = declarative_base()

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, Sequence('appointment_id_seq'), primary_key=True)
    patient_name = Column(String)
    age = Column(Integer, nullable = True)
    sex = Column(String)
    phone = Column(String)
    appointment_time = Column(DateTime)
    type = Column(String)
    category = Column(String)
    check_in_time = Column(DateTime, nullable=True)
    is_checked_in = Column(Boolean, default=False)
    priority_score = Column(Float, default = 0.0)
    is_completed = Column(Boolean, default = False)

class PrioritizationAgent:
    def __init__(self, database_url=DATABASE_URL):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)
        self.priority_queue = []

    def _extract_date_from_pdf(self, pdf_path):
        """Extracts appointment date from the pdf"""
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            for line in text.split("\n"):
                if line.lower().startswith("appointment date:"):
                    date_part = line.split(":", 1)[1].strip().split(",")[0].strip()
                    year = datetime.now().year # Set current year
                    return datetime.strptime(f"{date_part} {year}", "%d %B %Y").date()
        return None

    def _extract_appointments_from_pdf(self, pdf_path):
        """Extracts appointment data from a PDF."""
        appointments = []
        date = self._extract_date_from_pdf(pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    for index, row in df.iterrows():
                        sl = row.get('SL', None)
                        if not sl or not str(sl).isdigit():
                           print(f"Error skipping row with invalid SL {sl}, row: {row}")
                           continue
                        try:

                            sl = int(sl)
                            appointment_time_str = f"{date.strftime('%Y-%m-%d')} 00:00"
                            appointment_time = datetime.strptime(appointment_time_str, "%Y-%m-%d %H:%M")
                            appointment_time = appointment_time.replace(hour = sl)

                            age = row.get("Age", None)
                            if age:
                              try:
                                  age = int(age)
                              except:
                                  age = None
                            else:
                                age = None

                            if row.get("Patient Name", None) and row.get("Phone", None):
                                 appointments.append({
                                     "patient_name": row["Patient Name"],
                                     "age": age,
                                     "sex": row.get("Sex", None),
                                     "phone": row["Phone"],
                                     "type": row.get("Type", None),
                                     "category": row.get("Category", None),
                                     "appointment_time": appointment_time
                                 })

                        except Exception as e:
                            print(f"Error extracting appointment: {e}, row: {row}")


        return appointments
    def load_appointments_from_pdf(self, pdf_path):
        """Loads appointments from the pdf to the database"""
        appointments = self._extract_appointments_from_pdf(pdf_path)
        session = self.Session()
        try:
            for appt_data in appointments:
                appointment = Appointment(**appt_data)
                session.add(appointment)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting data: {e}")
        finally:
            session.close()


    def initialize_priority_queue(self):
        """Initializes the priority queue from the database."""
        session = self.Session()
        try:
           all_appointments = session.query(Appointment).filter(Appointment.is_completed == False).order_by(Appointment.appointment_time).all()
           self.priority_queue = [app for app in all_appointments]
        finally:
           session.close()


    def update_priority(self, appointment_id, check_in_time = None):
        """Updates priority of a given appointment."""
        session = self.Session()
        try:
          appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
          if appointment:
              appointment.is_checked_in = True
              appointment.check_in_time = check_in_time
              appointment.priority_score = self.calculate_priority(appointment)
              session.commit()
          else:
              print("Appointment Not Found")
        except Exception as e:
          session.rollback()
          print(f"Error updating priority score: {e}")
        finally:
           session.close()


    def calculate_priority(self, appointment):
        """Calculates priority based on wait time and other factors."""
        priority = 0.0
        if appointment.is_checked_in:
           time_diff = (datetime.now() - appointment.check_in_time).total_seconds()
           priority += time_diff * 0.1  # More wait time, higher priority
        if appointment.type == "Report": # We can update priority if report or emergency is found.
            priority += 20

        return priority

    def get_prioritized_queue(self):
        """Returns the priority queue."""
        session = self.Session()
        try:
          self.priority_queue = session.query(Appointment).filter(Appointment.is_completed == False).order_by(Appointment.priority_score.desc()).all()
        finally:
           session.close()
        return self.priority_queue

    def mark_appointment_complete(self, appointment_id):
        """Marks an appointment as completed."""
        session = self.Session()
        try:
          appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
          if appointment:
              appointment.is_completed = True
              session.commit()
          else:
              print("Appointment Not Found")
        except Exception as e:
          session.rollback()
          print(f"Error completing the appointment: {e}")
        finally:
           session.close()

if __name__ == '__main__':
   agent = PrioritizationAgent()
   agent.load_appointments_from_pdf("test_schedule.pdf")
   queue = agent.get_prioritized_queue()
   print(queue)
   if queue:
       appt_to_update = queue[0]
       print(appt_to_update)
       agent.update_priority(appt_to_update.id, check_in_time = datetime.now())
       print(agent.get_prioritized_queue())
       agent.mark_appointment_complete(appt_to_update.id)
       print(agent.get_prioritized_queue())
   else:
       print("No Appointments to Process.")