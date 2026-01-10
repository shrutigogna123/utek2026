import time
def calculate_priority(patient):
    """
    calculates priority score based on CTAS, urgency, and wait time.
    Lower score = Higher Priority.
    """
    # base priority from CTAS (most important)
    # CTAS 1 = 100, CTAS 5 = 500
    priority_score = patient["ctas"] * 100

   
    waiting_time = (time.time() - patient["arrival_time"]) / 60
    priority_score += waiting_time

    # Urgency adjustment (Higher urgency = Lower score = Better priority)
    priority_score -= patient["urgency"] * 5

    return priority_score

def prioritize_patients(patient_list):
    """
    Sorts the patient list using the custom Insertion Sort logic.
    """
    sorted_patients = []

    for patient in patient_list:
        # CTAS 1 always goes to the front
        if patient["ctas"] == 1:
            sorted_patients.insert(0, patient)
            continue

        patient_priority = calculate_priority(patient)
        inserted = False

        # insertion sort
        for i in range(len(sorted_patients)):
            # cannot displace CTAS 1 patients
            if sorted_patients[i]["ctas"] == 1:
                continue
            
            # compare scores
            if patient_priority < calculate_priority(sorted_patients[i]):
                sorted_patients.insert(i, patient)
                inserted = True
                break
    
        if not inserted:
            sorted_patients.append(patient)

    return sorted_patients