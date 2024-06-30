from database import mongo
from werkzeug.security import generate_password_hash
# Στο admin_functions.py

def create_doctor(username, email, password, name, speciality, surname, appointment_cost,available):
    existing_user = mongo.db.doctors.find_one({'$or': [{'username': username}, {'email': email}]})
    
    if existing_user:
        return False

    # Αφαιρούμε την κρυπτογράφηση του κωδικού πρόσβασης generate_password_hash(password)
    doctor = {
        "name": name,
        "surname": surname,
        "email": email,
        "username": username,
        "password": password,  # Εδώ προσθέστε τον κωδικό ως κείμενο
        "speciality": speciality,
        "appointment_cost": appointment_cost,
        "available":available
    }
    
    result = mongo.db.doctors.insert_one(doctor)
    return result.acknowledged

def change_doctor_password(username, new_password):
    result = mongo.db.doctors.update_one({"username": username}, {"$set": {"password": new_password}})
    return result.modified_count > 0

def delete_doctor(username):
    result = mongo.db.doctors.delete_one({"username": username})
    return result.deleted_count > 0

def delete_patient(username):
    result = mongo.db.patients.delete_one({"username": username})
    return result.deleted_count > 0
