import streamlit as st
import random

class PrioritizationAgent:
    def calculate_priority(self, patient_data):
        base_score = 0
        
        # Age weighting
        if patient_data['age'] > 65:
            base_score += 20
        elif patient_data['age'] < 18:
            base_score += 15
        
        # Condition severity mapping
        severity_map = {
            "critical": 30,
            "serious": 20,
            "moderate": 10,
            "mild": 5
        }
        base_score += severity_map.get(patient_data['medical_condition'].lower(), 0)
        
        # Chronic illness bonus
        if patient_data['chronic_illness']:
            base_score += 15
        
        return {
            "priority_score": min(base_score, 100),
            "rationale": f"Prioritized based on patient characteristics"
        }

def main():
    st.title("Physician's Chamber Prioritization Agent")
    st.write("Demonstrate patient prioritization mechanism")

    # Input fields
    age = st.number_input("Patient Age", min_value=0, max_value=120, value=30)
    
    medical_conditions = [
        "Mild", "Moderate", "Serious", "Critical"
    ]
    medical_condition = st.selectbox(
        "Medical Condition Severity", 
        medical_conditions
    )
    
    chronic_illness = st.checkbox("Chronic Illness Present")
    
    # Prioritization button
    if st.button("Calculate Priority"):
        agent = PrioritizationAgent()
        patient_data = {
            'age': age,
            'medical_condition': medical_condition,
            'chronic_illness': chronic_illness
        }
        
        result = agent.calculate_priority(patient_data)
        
        # Display results
        st.subheader("Prioritization Results")
        st.metric("Priority Score", result['priority_score'])
        st.info(result['rationale'])
        
        # Visual representation
        st.progress(result['priority_score'] / 100)
        
        # Recommendation based on score
        if result['priority_score'] > 70:
            st.warning("HIGH PRIORITY: Immediate medical attention recommended")
        elif result['priority_score'] > 50:
            st.warning("MODERATE PRIORITY: Prompt assessment needed")
        else:
            st.info("LOW PRIORITY: Standard queue processing")

if __name__ == "__main__":
    main()
