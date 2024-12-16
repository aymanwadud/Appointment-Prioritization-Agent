from datetime import datetime
from utils.data_utils import load_data, save_data
from utils.config import PRIORITY_FACTORS
class PrioritizationAgent:
    def __init__(self, data_dir = "data/"):
        self.data_dir = data_dir
        self.filename_prefix = "appointments_"

    def _get_filename(self, date):
       return self.data_dir + self.filename_prefix + str(date) + ".json"
    def calculate_priority(self, appointment):
        priority_score = 0
        if "reason" in appointment:
            reason = appointment["reason"].lower()
            for key in PRIORITY_FACTORS:
                if key in reason:
                   priority_score += PRIORITY_FACTORS[key]
        
        return priority_score

    def get_prioritized_queue(self, date):
       appointments = load_data(self._get_filename(date))
       if not appointments:
           return []
       for appointment in appointments:
           appointment["priority_score"] = self.calculate_priority(appointment)
       return sorted(appointments, key=lambda x: x["priority_score"], reverse = True)

    def update_priority_factor(self, config):
        global PRIORITY_FACTORS
        PRIORITY_FACTORS = config
        
if __name__ == '__main__':
    agent = PrioritizationAgent()
    print(agent.get_prioritized_queue(datetime.strptime("2024-08-22", "%Y-%m-%d").date()))