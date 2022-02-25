from flask import Flask, render_template, request, url_for, redirect, g, session
from User import User
from Email import Email
import random
from datetime import date, timedelta
import bcrypt as bcrypt

import os
import sqlite3 as sqlite
from flask_login import LoginManager, login_user, login_required, logout_user

app = Flask(__name__, template_folder="Templates", static_folder="Static")
app.debug = True

app.config['SECRET_KEY'] = os.urandom(12).hex()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

SESSION_COOKIE_HTTPONLY = True,
REMEMBER_COOKIE_HTTPONLY = True,
SESSION_COOKIE_SAMESITE = "Strict"


@login_manager.user_loader
def load_user(user_id):
    con = sqlite.connect("PatientManagement.db")
    curs = con.cursor()
    curs.execute("SELECT * FROM Login WHERE Unique_Id = ?", [user_id])
    row = curs.fetchone()
    g.user = row[1]
    g.user_type = row[3]

    try:
        if row is None:
            return None
        else:
            return User(int(row[0]), row[1], row[2], row[3])

    except TypeError:
        return redirect(url_for('index'))


@login_manager.unauthorized_handler
def unauthorised():
    print("You are not logged in. Log in to access this page")
    return render_template("index.html", msg="You are not logged in. Log in to access this page")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return render_template("index.html", msg="You have been logged out")


@app.route("/doctor-dashboard")
@login_required
def dr_dashboard():
    return render_template("dr-dashboard.html", msg="Welcome Dr. " + g.user, rows=view_upcoming_appointments(),
                           data=view_previous_appointments())


@app.route("/nurse-dashboard")
@login_required
def nurse_dashboard():
    with sqlite.connect("PatientManagement.db") as con:
        print("Database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT * FROM Scheduled_Appointments")
        rows = cur.fetchall()
        return render_template("dashboard.html", msg="Welcome Nurse. " + g.user, rows=rows)


@app.route("/newPatient")
@login_required
def patient_form():
    specialty = "GP"
    with sqlite.connect("PatientManagement.db") as con:
        print("Database opened successfully")
        cur = con.cursor()
        cur.execute(f"SELECT Name FROM Physician WHERE Specialty = ?", [specialty])
        rows = cur.fetchall()
        print(rows)

        try:
            if g.user_type == "Nurse":
                return render_template('patients-add.html', rows=rows, msg="Welcome Nurse. " + g.user)

            else:
                return render_template('patients-add.html', rows=rows, msg="Welcome Dr. " + g.user)


        except AttributeError:
            print("Something went wrong")


@app.route("/newCheckup")
@login_required
def checkup_form():
    with sqlite.connect("PatientManagement.db") as con:
        print("Database opened successfully")
        cur = con.cursor()
        cur.execute(f"SELECT Name FROM Patients")
        rows = cur.fetchall()
        print(rows)
        return render_template('patients-routine.html', rows=rows, msg="Welcome Nurse. " + g.user)


@app.route("/newAppointment")
@login_required
def appointment_form():
    if g.user_type == "Nurse":
        with sqlite.connect("PatientManagement.db") as con:
            print("Database opened successfully")
            cur = con.cursor()
            cur.execute(f"SELECT Name FROM Patients")
            rows = cur.fetchall()
            print(rows)
            return render_template('app-schedule.html', rows=rows, msg="Welcome Nurse. " + g.user)

    if g.user_type == "Doctor":
        with sqlite.connect("PatientManagement.db") as con:
            print("Database opened successfully")
            cur = con.cursor()
            cur.execute(f"SELECT Name FROM Patients WHERE Assigned_Physician=?", [g.user])
            rows = cur.fetchall()
            print(rows)
            return render_template('dr-app-schedule.html', rows=rows, msg="Welcome Dr. " + g.user)


@app.route("/AssignForm")
@login_required
def assign_form():
    physician_name = g.user
    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Name FROM Patients WHERE Assigned_Physician = ?", [physician_name])
        rows = cur.fetchall()

        cur.execute(f"SELECT Name, Specialty FROM Physician WHERE Specialty != ?", ["GP"])
        data = cur.fetchall()

        # print(data)

        return render_template("dr-patients-specialist.html", msg="Welcome Dr. " + g.user, rows=rows, data=data)


@app.route("/diagnosticsForm")
@login_required
def diagnosticsReport():
    physician_name = g.user
    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Name FROM Patients WHERE Assigned_Physician = ?", [physician_name])
        rows = cur.fetchall()

    return render_template("dr-patients-add.html", msg="Welcome Dr. " + g.user, rows=rows)


@app.route("/myAppointments")
@login_required
def myAppointments():
    return render_template("dr-app-calendar.html", msg="Welcome Dr. " + g.user, rows=view_upcoming_appointments())


@app.route("/registerStaff", methods=["GET"])
@login_required
def registerStaff():
    return render_template("add-staff.html", msg="Welcome Nurse. " + g.user)


@app.route("/deleteStaff")
@login_required
def deleteStaff():
    return render_template("delete-staff.html", msg="Welcome Nurse. " + g.user, data=get_staffs())


@app.route("/deletePatient")
@login_required
def deletePatient():
    return render_template("delete-Patient.html", msg="Welcome Nurse. " + g.user, rows=get_patients())


def generate_id():
    value = str(random.randint(1000, 9999))
    con = sqlite.connect("PatientManagement.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM Login WHERE Unique_Id = ?", [value])
    row = cur.fetchall()

    if row:
        generate_id()

    else:
        return value


def get_next_month():
    next_month = (date.today() + timedelta(days=30)).isoformat()
    return next_month


@app.route("/staffregisteration", methods=["POST", "GET"])
@login_required
def staff_registration():

    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    name = firstname + " " + lastname
    password = request.form["password"]
    password2 = request.form["confirmpassword"]
    date_of_employment = date.today()
    dob = request.form["date"]
    specialty = request.form["specialty"]
    staff_type = request.form["stafftype"]
    gender = request.form["gender"]
    phone_no = request.form["number"]
    email = request.form["email"]
    unique_id = generate_id()

    if password != password2 or not password or not password2:
        msg = "passwords do not match"
        return render_template("add-staff.html", warning=msg)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    with sqlite.connect("PatientManagement.db") as con:

        print("Database opened successfully")
        cur = con.cursor()

        if staff_type == "Nurse":
            cur.execute(
                "INSERT INTO Nurse(Name, DOB, Gender, Email,"
                " Phone_no, Date_of_employment) VALUES(?,?,?,?,?,?)",
                (name, dob, gender, email, phone_no, date_of_employment))

        elif staff_type == "Doctor":
            cur.execute("INSERT INTO Physician(Name, DOB, Gender, "
                        "Specialty, Date_of_employment, Phone_no, "
                        "Email) VALUES(?,?,?,?,?,?,?)",
                        (name, dob, gender, specialty,

                        date_of_employment, phone_no, email)
                        )

        cur.execute("INSERT INTO Login(Unique_Id, Name, Password, Staff_Type)"
                    " VALUES(?,?,?,?)",
                    (unique_id, name, hashed, staff_type))

        print("Staff Registered Successfully")
        data = "your Unique Id is " + unique_id + ". use it with your password to login."
        return render_template("index.html", data=data)




@app.route("/Dashboard", methods=["POST"])
def login():
    if request.method == "POST":

        unique_id = request.form["id"]
        pass_input = request.form["password"].encode("utf-8")

        with sqlite.connect("PatientManagement.db") as con:
            print("Database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT * FROM Login WHERE Unique_Id = ?", [unique_id])
            row = cur.fetchone()

        try:
            if row is None:
                msg = "user does not exist!"
                return render_template("index.html", msg=msg)

            password = row[2]

            if bcrypt.checkpw(pass_input, password):
                user = User(row[0], row[1], password, row[3])
                g.user = row[1]
                login_user(user)
                user.authenticated = True
                msg = f"Login Successful,user is a {row[3]} "
                print(msg)

                if user.staff_type == "Doctor":
                    return redirect(url_for('dr_dashboard'))

                if user.staff_type == "Nurse":
                    return redirect(url_for('nurse_dashboard'))

                msg = "Login successful"
                print(msg)

            else:
                logout_user()
                msg = "Login failed, Incorrect ID or password!"
                return render_template("index.html", msg=msg)

        except TypeError:
            msg = "Invalid details"
            print(msg)
            return redirect(url_for('index'))


@app.route("/addPatient", methods=["POST"])
@login_required
def register_patient():
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    name = firstname + " " + lastname
    dob = request.form["date"]
    gender = request.form["gender"]
    ethnicity = request.form["ethnicity"]
    email = request.form["email"]
    number = request.form["number"]
    address = request.form["address"]
    symptoms = request.form["symptoms"]
    assigned_physician = request.form["GP"]

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("INSERT INTO Patients(Name, DOB, Gender, Ethnicity, Email, Phone_no, Address, Symptoms, "
                    "Assigned_Physician) Values(?,?,?,?,?,?,?,?,?)",
                    (name, dob, gender, ethnicity, email, number, address, symptoms, assigned_physician))

        con.commit()
        print("Patient added successfully")

        email = Email(email)
        email.welcome_message(name)
        email.setup_message()
        email.sendmail()

        return redirect(url_for('nurse_dashboard'))


@app.route("/patientDelete", methods=["POST"])
@login_required
def delete_patient():
    name = request.form["patient"]

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("DELETE FROM Patients WHERE Name = ?", [name])
        print("deleted Successfully")

    return redirect(url_for('nurse_dashboard'))


@app.route("/staffDelete", methods=["POST"])
@login_required
def delete_staff():
    name = request.form["staff"]
    print(name)

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT * FROM Physician WHERE Name=?", [name])
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM Physician WHERE Name=?", [name])
            cur.execute("DELETE FROM Login WHERE Name=?", [name])
            print("deleted Doctor Successfully")
            return redirect(url_for('nurse_dashboard'))

        cur.execute("SELECT * FROM Nurse WHERE Name=?", [name])
        data = cur.fetchone()
        if data:
            cur.execute("DELETE FROM Nurse WHERE Name=?", [name])
            cur.execute("DELETE FROM Login WHERE Name=?", [name])
            print("deleted Nurse Successfully")
            return redirect(url_for('nurse_dashboard'))


@app.route("/Patients", methods=["GET", "POST"])
@login_required
def all_patients():
    if request.method == "GET":
        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT * FROM Patients")
            rows = cur.fetchall()
            return render_template("patients-all.html", rows=rows, msg="Welcome Nurse. " + g.user)

    if request.method == "POST":
        name = request.form["name"]
        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT * FROM Patients WHERE Name=?", [name])
            rows = cur.fetchall()
            return render_template("patients-all.html", rows=rows, msg="Welcome Nurse. " + g.user)


def get_staffs():
    rows = []
    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Name FROM Physician")
        data = cur.fetchall()
        for datum in data:
            for row in datum:
                rows.append(row)

        cur.execute("SELECT Name FROM Nurse")
        result = cur.fetchall()
        for datum in result:
            for row in datum:
                rows.append(row)

        return rows


def get_patients():
    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Name FROM Patients")
        rows = cur.fetchall()
        return rows


@app.route("/PatientProfile", methods=["POST"])
@login_required
def patient_profile():
    if request.method == "POST":
        name = request.form["name"]
        rows = []
        with sqlite.connect("PatientManagement.db") as con:

            print("database opened successfully")
            cur = con.cursor()
            cur.execute(
                "SELECT Name, Address, Email, Phone_no, DOB, Confirmed_diagnosis, Prescriptions FROM Patients WHERE "
                "Name = ?", [name])
            data = cur.fetchall()
            for values in data:
                for value in values:
                    rows.append(value)

            cur.execute("SELECT Blood_Pressure, Body_Temperature, Weight, Pulse FROM Checkups WHERE Patient_Name = ?",
                        [name])
            data = cur.fetchall()

            for values in data:
                for value in values:
                    rows.append(value)

            cur.execute("SELECT Date, Physician_Name FROM Appointment_data WHERE Patient_Name = ?", [name])
            data = cur.fetchall()

        try:
            # print(rows)
            # print(data)
            if g.user_type == "Nurse":
                return render_template("patients-profile.html", rows=rows, data=data, msg="Welcome Nurse. " + g.user)

            else:
                return render_template("dr-patients-profile.html", rows=rows, data=data, msg="Welcome Dr. " + g.user)

        except TypeError:
            return render_template("patients-profile.html")


def nurse_update_patient():
    name = "david Jones"
    symptoms = "headache and migraines, high temperature, coughing"

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("UPDATE Patients SET Symptoms = ? WHERE Name = ?", (symptoms, name))
        print("Symptoms added Successfully")


@app.route("/updateReport", methods=["POST"])
@login_required
def physician_update_patient():
    name = request.form["patient"]
    diagnosis = request.form["diagnosis"]
    prescription = request.form["prescriptions"]

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Email FROM Patients WHERE Name = ?", [name])
        row = cur.fetchone()
        email = str(row[0]).strip("(), '' , , ")

        cur.execute("UPDATE Patients SET Confirmed_diagnosis = ?, Prescriptions = ? WHERE Name = ?", (diagnosis,
                                                                                                      prescription,
                                                                                                      name))
        print("Diagnosis and Prescription added Successfully")

        send = Email(email)
        send.prescription_sent(name)
        send.setup_message()
        send.sendmail()

        return redirect(url_for('dr_dashboard'))


def nurse_assign_patient():
    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Name FROM Physician WHERE Specialty = ?", ["GP"])
        rows = cur.fetchall()

        patient_name = "Oladimeji Atikko"
        physician_name = str(rows[3]).strip("(), '' , , ")

        cur.execute("UPDATE Patients SET Assigned_Physician = ? WHERE Name = ?", (physician_name, patient_name))

        print("Physician assigned Successfully")

        cur.execute("SELECT * FROM Patients WHERE Assigned_Physician = ? ", [physician_name])

        rows = cur.fetchall()

        no_of_assigned_patients = str(len(rows))

        cur.execute("UPDATE Physician SET No_of_assigned_patients = ? WHERE Name = ?", (no_of_assigned_patients,
                                                                                        physician_name))

        print("Number of assigned patients updated successfully")


@app.route("/routineCheckup", methods=["POST"])
@login_required
def record_checkup_data():
    if request.method == "POST":
        name = request.form["name"]
        temp = request.form["temperature"]
        blood_pressure = request.form["bloodpressure"]
        pulse = request.form["pulse"]
        weight = request.form["weight"]

        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT Assigned_Physician FROM Patients WHERE Name = ?", [name])
            rows = cur.fetchone()

            physician_name = str(rows[0]).strip("(), '' , , ")

            cur.execute("SELECT * FROM Checkups WHERE Patient_Name = ?", [name])
            data = cur.fetchone()

            if data:
                cur.execute(
                    f"UPDATE Checkups SET  Assigned_Physician = ?, Date = ?, Body_Temperature = ?, "
                    "Blood_Pressure = ?, "
                    f"Pulse = ?, Weight = ? WHERE Patient_Name ='{name}'",
                    (physician_name, date.today(), temp, blood_pressure, pulse, weight))
                print("record updated successfully")

            if not data:
                cur.execute(
                    "INSERT INTO Checkups(Patient_Name, Assigned_Physician, Date, Body_Temperature, Blood_Pressure, "
                    "Pulse, Weight) VALUES(?,?,?,?,?,?,?)",
                    (name, physician_name, date.today(), temp, blood_pressure, pulse, weight))
                print("record inserted successfully")

        return redirect(url_for('nurse_dashboard'))


@app.route("/assignedPatients", methods=["GET", "POST"])
@login_required
def view_assigned_patients():
    physician_name = g.user
    if request.method == "GET":
        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT * FROM Patients WHERE Assigned_Physician = ?", [physician_name])
            rows = cur.fetchall()
            return render_template("dr-patients-all.html", rows=rows, msg="Welcome Dr." + g.user)

    if request.method == "POST":
        name = request.form["name"]
        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT * FROM Patients WHERE Name=? AND Assigned_Physician=?", (name, physician_name))
            rows = cur.fetchall()

            if not name:
                cur.execute("SELECT * FROM Patients WHERE Assigned_Physician = ?", [physician_name])
                row = cur.fetchall()
                rows = row

        return render_template("dr-patients-all.html", rows=rows, msg="Welcome Dr." + g.user)


@app.route("/createAppointment", methods=["POST"])
@login_required
def create_appointment():
    if request.method == "POST":
        name = request.form["name"]
        appointment_date = request.form["date"]
        time = request.form["time"]

        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT Assigned_Physician, Email FROM Patients WHERE Name = ?", [name])
            rows = cur.fetchone()
            print(rows)
            physician_name = str(rows[0]).strip("(), '' , , ")
            email = str(rows[1]).strip("(), '' , , ")

            cur.execute("INSERT INTO Scheduled_Appointments(Patient_Name,Physician_Name, Date, Time) VALUES(?,?,?,?)",
                        (name, physician_name, appointment_date, time))

            email = Email(email)
            email.appointment_reminder(name, appointment_date, time)
            email.setup_message()
            email.sendmail()

            print("Appointment created successfully")

    if g.user_type == "Nurse":
        return redirect(url_for('nurse_dashboard'))

    if g.user_type == "Doctor":
        return redirect(url_for('dr_dashboard'))


@app.route("/assigntospecialist", methods=["POST"])
@login_required
def assign_to_specialist():
    patient = request.form["patient"]
    new_physician = request.form["specialist"]
    # specialty = request.form["specialty"]
    current_physician = g.user

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()

        cur.execute("UPDATE Patients SET Assigned_Physician = ? WHERE Name = ?", (new_physician, patient))

        print("Physician assigned Successfully")

        cur.execute("SELECT * FROM Patients WHERE Assigned_Physician = ? ", [current_physician])

        rows = cur.fetchall()

        no_of_assigned_patients = str(len(rows))

        cur.execute("UPDATE Physician SET No_of_assigned_patients = ? WHERE Name = ?", (no_of_assigned_patients,
                                                                                        current_physician))

        cur.execute("SELECT * FROM Patients WHERE Assigned_Physician = ? ", [new_physician])

        rows = cur.fetchall()

        no_of_assigned_patients = str(len(rows))

        cur.execute("UPDATE Physician SET No_of_assigned_patients = ? WHERE Name = ?", (no_of_assigned_patients,
                                                                                        new_physician))

        print("Number of assigned patients updated successfully")

        return redirect(url_for('dr_dashboard'))


def view_previous_appointments():
    physician = g.user

    with sqlite.connect("PatientManagement.db") as con:
        print("database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Patient_Name, Patients.Email, Date, Physician_Notes FROM Appointment_data INNER JOIN "
                    "Patients "
                    "ON Appointment_data.Patient_Name=Patients.Name WHERE Physician_Name = ? ",
                    [physician])

        data = cur.fetchall()

        return data


def view_upcoming_appointments():
    physician = g.user
    with sqlite.connect("PatientManagement.db") as con:
        print("Database opened successfully")
        cur = con.cursor()
        cur.execute("SELECT Patient_Name, Patients.Email, Date, Time FROM Scheduled_Appointments INNER JOIN Patients "
                    "ON Scheduled_Appointments.Patient_Name=Patients.Name WHERE Physician_Name = ? ",
                    [physician])
        rows = cur.fetchall()
        return rows


@app.route("/createSummary", methods=["POST", "GET"])
@login_required
def record_appointment():
    if request.method == "GET":
        name = request.args.get('name')
        session['patient_name'] = name
        return render_template("dr-app-summary.html", msg="Welcome Dr. " + g.user)

    if request.method == "POST":
        patient_name = session.get('patient_name', None)
        next_appointment = request.form["date"]
        physician_notes = request.form["notes"]
        prescription_update = request.form["prescription"]
        appointment_date = date.today()
        time = "10:00"

        with sqlite.connect("PatientManagement.db") as con:
            print("database opened successfully")
            cur = con.cursor()
            cur.execute("SELECT Assigned_Physician, Email FROM Patients WHERE Name = ?", [patient_name])
            rows = cur.fetchone()
            physician = str(rows[0]).strip("(), '' , , ")
            email = str(rows[1]).strip("(), '' , , ")

            cur.execute("INSERT INTO Appointment_data(Patient_Name, Physician_Name, Date, Physician_Notes,"
                        " Next_appointment, Prescription_update) "
                        "VALUES(?,?,?,?,?,?)",
                        (patient_name, physician, appointment_date, physician_notes, next_appointment
                         , prescription_update))

            cur.execute("INSERT INTO Scheduled_Appointments(Patient_Name,Physician_Name, Date, Time) VALUES(?,?,?,?)",
                        (patient_name, physician, next_appointment, time))

            email_obj = Email(email)
            email_obj.appointment_reminder(patient_name, next_appointment, time)
            email_obj.setup_message()
            email_obj.sendmail()

            cur.execute("DELETE FROM Scheduled_Appointments WHERE Patient_Name = ? AND Date = ? ",
                        (patient_name, date.today()))

            print("Appointments Updated")

            return redirect(url_for('myAppointments'))


if __name__ == "__main__":
    app.run()
