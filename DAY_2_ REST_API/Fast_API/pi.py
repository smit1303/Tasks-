from pydantic import BaseModel

class Patient(BaseModel):

    name : str
    age : int

def insert_patient_data(Patient: Patient):

    print(Patient.name)
    print(Patient.age)
    print("Patient data inserted successfully")


Patient_info = {"name":"smit","age" : 20}

Patient_1 = Patient(**Patient_info)

insert_patient_data(Patient_1)
