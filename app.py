from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import mongo, init_app
from datetime import datetime,timedelta
from bson import ObjectId
from threading import Timer
from admin_functions import create_doctor as admin_create_doctor, \
    change_doctor_password as admin_change_doctor_password, delete_doctor as admin_delete_doctor, \
    delete_patient as admin_delete_patient

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongo:27017/hospital'
init_app(app)
app.secret_key = 'supersecretkey'
patients_collection = mongo.db.patients
doctors_collection = mongo.db.doctors
appointments_collection = mongo.db.appointments

# Welcome page
@app.route("/")
def home():
    return render_template('welcome.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if admin
        if username == 'admin' and password == '@dm1n':
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))
            
      # Check if doctor
        doctor = doctors_collection.find_one({'username': username})
        if doctor and doctor['password'] == password:
            session['user'] = 'doctor'
            session['doctor'] = username
            return redirect(url_for('doctor_dashboard'))
        
          # Check if patient
        patient = patients_collection.find_one({'username': username})
        if patient and patient['password'] == password:
            session['user'] = 'patient'
            session['username'] = username
            session['email'] = patient['email']
            return redirect(url_for('patient_dashboard'))


        
        
        flash('Invalid credentials, please try again.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('login.html')

#logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    session.pop('doctor', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))


# Σελίδα εγγραφής ασθενούς
@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        # Λαμβάνουμε τα δεδομένα από τη φόρμα
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        amka = request.form.get('amka')
        birth_date = request.form.get('birth_date')
        username = request.form.get('username')
        password = request.form.get('password')

        # Ελέγχουμε αν το email ή το username είναι ήδη καταχωρημένα
        if patients_collection.find_one({'email': email}):
            flash('Email already registered!', 'danger')
            return redirect(url_for('register_patient'))
        if patients_collection.find_one({'username': username}):
            flash('Username already taken!', 'danger')
            return redirect(url_for('register_patient'))

        # Κρυπτογράφηση του κωδικού πρόσβασης
        hashed_password = password

        # Αποθήκευση του ασθενή στη MongoDB
        patients_collection.insert_one({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'amka': amka,
            'birth_date': birth_date,
            'username': username,
            'password': hashed_password
        })

        flash('Patient registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register_patient.html')

# Admin dashboard
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if 'user' in session and session['user'] == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('login'))
#patient dashboard    
@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user' in session and session['user'] == 'patient':
        appointments = mongo.db.appointments.find({'patient_username': session['username'], 'patient_email': session['email']})
        return render_template('patient_dashboard.html', appointments=appointments)
    else:
        flash('Please log in as a patient to view this page', 'danger')
        return redirect(url_for('login'))

#add doctor
@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def create_doctor_route():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            speciality = request.form.get('speciality')
            appointment_cost = request.form.get('appointment_cost')
            available = True

            success = admin_create_doctor(username, email, password, name, speciality, surname, appointment_cost,available)
            if success:
                flash('Doctor added successfully', 'success')
            else:
                flash('Username or email already exists', 'danger')
            return redirect(url_for('create_doctor_route'))
        else:
            return render_template('add_doctor.html')
    else:
        return redirect(url_for('login'))

# Admin change doctor password
@app.route('/admin/change_doctor_password', methods=['GET', 'POST'])
def change_doctor_password_route():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            username = request.form.get('username')
            new_password = request.form.get('new_password')

            success = admin_change_doctor_password(username, new_password)
            if success:
                flash('Doctor password changed successfully', 'success')
            else:
                flash('Failed to change doctor password', 'danger')
            return redirect(url_for('change_doctor_password_route'))
        else:
            return render_template('change_doctor_password.html')
    else:
        return redirect(url_for('login'))

# Admin delete doctor
@app.route("/admin/delete_doctor", methods=['GET', 'POST'])
def delete_doctor_route():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            doctor_id = request.form.get('doctor_id')
            success = admin_delete_doctor(doctor_id)
            if success:
                flash('Doctor deleted successfully', 'success')
            else:
                flash('Failed to delete doctor', 'danger')
            return redirect(url_for('delete_doctor_route'))
        else:
            return render_template('delete_doctor.html')
    else:
        return redirect(url_for('login'))

# Admin delete patient
@app.route("/admin/delete_patient", methods=['GET', 'POST'])
def delete_patient_route():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            username = request.form.get('username')
            success = admin_delete_patient(username)
            if success:
                flash('Patient deleted successfully', 'success')
            else:
                flash('Failed to delete patient', 'danger')
            return redirect(url_for('delete_patient_route'))
        else:
            return render_template('delete_patient.html')
    else:
        return redirect(url_for('login'))

#Admin delete patient
def admin_delete_patient(username):
    try:
        result = patients_collection.delete_one({'username': username})
        if result.deleted_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
#doctor dashboard
@app.route('/doctor/dashboard', methods=['GET'])
def doctor_dashboard():
    if 'user' in session and session['user'] == 'doctor':
        doctor_username = session['doctor']  # Fetching doctor's username from session

        # Query appointments for the specific doctor
        doctor_appointments = list(appointments_collection.find({'doctor_username': doctor_username}))

        return render_template('doctor_dashboard.html', appointments=doctor_appointments)
    else:
        return redirect(url_for('login'))
#doctor change appointment cost    
@app.route('/doctor/change_appointment_cost', methods=['POST'])
def change_appointment_cost():
    if 'user' in session and session['user'] == 'doctor':
        new_cost = request.form.get('new_cost')

        if not new_cost:
            flash('Please enter a valid cost.', 'danger')
            return redirect(url_for('doctor_dashboard'))

        try:
            new_cost = float(new_cost)
        except ValueError:
            flash('Cost must be a number.', 'danger')
            return redirect(url_for('doctor_dashboard'))

        # Fetching doctor's username from session
        doctor_username = session['doctor']

        # Update appointments cost in MongoDB appointments collection
        result_appointments = appointments_collection.update_many(
            {'doctor_username': doctor_username},
            {'$set': {'cost': new_cost}}
        )

        if result_appointments.modified_count > 0:
            flash('Appointment costs updated successfully.', 'success')
        else:
            flash('No appointments found to update.', 'danger')

        # Update doctor's appointment_cost in MongoDB doctors collection
        result_doctor = doctors_collection.update_one(
            {'username': doctor_username},
            {'$set': {'appointment_cost': new_cost}}
        )

        if result_doctor.modified_count == 1:
            flash('Doctor\'s appointment cost updated successfully.', 'success')
        else:
            flash('Failed to update doctor\'s appointment cost.', 'danger')

        return redirect(url_for('doctor_dashboard'))
    else:
        return redirect(url_for('login'))

# Doctor change password
@app.route('/doctor/change_password', methods=['GET', 'POST'])
def doctor_change_password():
    if 'user' in session and session['user'] == 'doctor':
        if request.method == 'POST':
            username = session.get('doctor')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')

            doctor = mongo.db.doctors.find_one({'username': username})
            if doctor and doctor['password'] == current_password:
                mongo.db.doctors.update_one({'username': username}, {'$set': {'password': new_password}})
                flash('Password changed successfully', 'success')
            else:
                flash('Current password is incorrect', 'danger')
            return redirect(url_for('doctor_change_password'))
        else:
            return render_template('doctor_change_password.html')
    else:
        return redirect(url_for('login'))

#Change available
def update_doctor_availability(doctor_username, delay):
    def set_available():
        doctors_collection.update_one({'username': doctor_username}, {'$set': {'available': True}})
    
    Timer(delay, set_available).start()

def set_doctor_unavailable(doctor_username, delay):
    def set_unavailable():
        doctors_collection.update_one({'username': doctor_username}, {'$set': {'available': False}})
    
    Timer(delay, set_unavailable).start()

#Create appointment
def create_appointment(patient_username, patient_email, doctor_username, appointment_date, appointment_time, reason):
    try:
        doctor = doctors_collection.find_one({'username': doctor_username})
        if not doctor:
            raise ValueError("Doctor not found")

        # Ελέγχουμε αν ο γιατρός είναι διαθέσιμος και έχει την επιθυμητή ειδικότητα
        if not doctor['available']:
            raise ValueError("Doctor is not available")

        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")

        # Ελέγχουμε αν υπάρχει ήδη ραντεβού για τον γιατρό τη δεδομένη ώρα
        existing_appointment = appointments_collection.find_one({
            'doctor_username': doctor_username,
            'appointment_datetime': appointment_datetime
        })
        if existing_appointment:
            raise ValueError("Doctor already has an appointment at this time")

        appointments_collection.insert_one({
            'patient_username': patient_username,
            'patient_email': patient_email,
            'doctor_username': doctor_username,
            'appointment_datetime': appointment_datetime,
            'reason': reason,
            'doctor_name': doctor['name'],
            'doctor_surname': doctor['surname'],
            'doctor_speciality': doctor['speciality'],
            'cost': doctor['appointment_cost']  # Παράδειγμα κόστους ραντεβού
        })

        # Υπολογισμός χρόνου μέχρι την έναρξη του ραντεβού
        now = datetime.now()
        start_delay = (appointment_datetime - now).total_seconds()

        # Ενημέρωση διαθεσιμότητας γιατρού σε false κατά την ώρα έναρξης του ραντεβού
        set_doctor_unavailable(doctor_username, start_delay)
        
        # Ενημέρωση διαθεσιμότητας γιατρού σε true μετά τη λήξη του ραντεβού (διάρκεια 1 ώρα)
        appointment_duration = 60 * 60  # 1 ώρα σε δευτερόλεπτα
        update_doctor_availability(doctor_username, start_delay + appointment_duration)

        return True
    except Exception as e:
        print(f"Error creating appointment: {str(e)}")
        return False

#Search appointment
@app.route('/patient/search_appointment', methods=['GET', 'POST'])
def search_appointment():
    if 'user' in session and session['user'] == 'patient':
        if request.method == 'POST':
            doctor_specialty = request.form.get('speciality')
            appointment_date = request.form.get('date')
            reason = request.form.get('reason')
            appointment_time = request.form.get('time')
            patient_username = session['username']
            patient_email = session['email']

            # Εύρεση διαθέσιμου γιατρού με την ειδικότητα
            doctor = doctors_collection.find_one({
                'speciality': doctor_specialty,
                'available': True
            })

            if doctor:
                # Δημιουργία ραντεβού
                success = create_appointment(patient_username, patient_email, doctor['username'], appointment_date, appointment_time, reason)
                if success:
                    flash('Το ραντεβού καταχωρήθηκε επιτυχώς!', 'success')
                else:
                    flash('Η δημιουργία του ραντεβού απέτυχε.', 'danger')
            else:
                flash('Δεν βρέθηκε διαθέσιμος γιατρός για την επιλεγμένη ειδικότητα.', 'danger')

            return redirect(url_for('search_appointment'))
        else:
            return render_template('search_and_book_appointment.html')
    else:
        return redirect(url_for('login'))

#my appointments
@app.route('/patient/my_appointments', methods=['GET'])
def my_appointments():
    if 'user' in session and session['user'] == 'patient':
        appointments = mongo.db.appointments.find({
            'patient_username': session['username']
        })
        return render_template('my_appointments.html', appointments=appointments)
    else:
        return redirect(url_for('login'))   
#single appointment   
@app.route('/patient/appointment/<appointment_id>', methods=['GET'])
def view_appointment(appointment_id):
    if 'user' in session and session['user'] == 'patient':
        appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
        if appointment:
            return render_template('view_appointment.html', appointment=appointment)
        else:
            flash('Το ραντεβού δεν βρέθηκε.', 'danger')
            return redirect(url_for('patient_dashboard'))
    else:
        return redirect(url_for('login'))
#delete appointment
@app.route('/patient/delete_appointment/<appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    if 'user' in session and session['user'] == 'patient':
        appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
        if appointment:
            # Διαγραφή ραντεβού
            appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
            
            # Ενημέρωση διαθεσιμότητας γιατρού
            doctor_username = appointment['doctor_username']
            doctors_collection.update_one({'username': doctor_username}, {'$set': {'available': True}})
            
            flash('Το ραντεβού ακυρώθηκε επιτυχώς.', 'success')
        else:
            flash('Το ραντεβού δεν βρέθηκε.', 'danger')
        return redirect(url_for('patient_dashboard'))
    else:
        return redirect(url_for('login'))


# Test MongoDB connection
@app.route('/test_mongo')
def test_mongo():
    try:
        mongo.db.command("ping")
        return jsonify({'message': 'MongoDB connection successful!'})
    except Exception as e:
        return jsonify({'message': 'MongoDB connection failed!', 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
