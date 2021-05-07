from flask import render_template, url_for, flash, redirect, request
from hms import app, db, bcrypt
from hms.forms import RegistrationForm, BookingForm, ChatForm, LoginForm, RegistrationAdminForm
from hms.models import User, Chat, Admin
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os, shutil
import datetime, time
from collections import Counter
import random
import smtplib
from functools import wraps
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename

Admin_Login = False

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
               return app.login_manager.unauthorized()
            urole = current_user.role
            if ( (urole != role) and (role != "ANY")):
                return app.login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route("/admin", methods=['GET', 'POST'])
def admin():

    form = LoginForm()
    if form.validate_on_submit():
        print("####")
        print(Admin.query.all())
        admin_user = Admin.query.filter_by(email=form.email.data).first()
        if form.email.data == admin_user.email and form.password.data == admin_user.password:
            print("Admin Login Success", admin_user)
            global Admin_Login
            Admin_Login = True
            return redirect(url_for('admin_operation'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('admin.html', title='Admin Login', form=form)

@app.route("/admin_operation", methods=['GET', 'POST'])
def admin_operation():
    global Admin_Login
    if(Admin_Login):
        form = RegistrationAdminForm()
        try:
            patient_info_postive = User.query.filter_by(test_result='postive').all()
            patient_info_negative = User.query.filter_by(test_result='negative').all()
            patient_booked_vaccine = User.query.filter(User.book_vaccine_time != None).all()
            patient_booked_test = User.query.filter(User.book_test_time != None).all()
            print(len(patient_info_postive), len(patient_info_negative), len(patient_booked_vaccine), len(patient_booked_test))

            patient_info_postive = len(patient_info_postive)
            patient_info_negative = len(patient_info_negative)
            patient_booked_vaccine = len(patient_booked_vaccine)
            patient_booked_test = len(patient_booked_test)


        except Exception as e:
            print('e', e)
            patient_info_postive = 0
            patient_info_negative = 0
            patient_booked_vaccine = 0
            patient_booked_test = 0


        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(role=form.role.data, name=form.name.data, email=form.email.data, password=hashed_password,
                contact_no=form.contact_no.data, address=form.address.data, pincode=form.pincode.data, test_result=None, book_test_time=None, 
                book_vaccine_time=None, doctor_email=None)
            db.session.add(user)
            db.session.commit()
            print(user)
            flash(form.role.data+' account is created', 'success')
            return redirect(url_for('admin_operation'))

        return render_template('admin_operation.html', title='Admin Login', form=form, admin_login=1, patient_info_postive=patient_info_postive, 
            patient_info_negative=patient_info_negative,
            patient_booked_vaccine=patient_booked_vaccine, patient_booked_test=patient_booked_test,)
    else:
        return redirect(url_for('admin'))


@app.route("/admin_logout", methods=['GET', 'POST'])
def admin_logout():
    global Admin_Login
    Admin_Login = False
    return redirect(url_for('admin'))

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


#  role, name, email, password, contact_no, address, pincode, test_result, book_test_time, book_vaccine_time, doctor_email
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(role='Patient', name=form.name.data, email=form.email.data, password=hashed_password,
                contact_no=form.contact_no.data, address=form.address.data, pincode=form.pincode.data, test_result=None, book_test_time=None, 
                book_vaccine_time=None, doctor_email=None)
            db.session.add(user)
            db.session.commit()
            print(user)
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("current_user", current_user, type(current_user), current_user.email)
        if current_user.role == 'Hospital':
            return redirect(url_for('hospital_operation'))
        elif current_user.role == 'Doctor':
            return redirect(url_for('doctor_operation'))
        else:
            return redirect(url_for('patient_operation'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print("Login Success", user)
            next_page = request.args.get('next')
            if current_user.role == 'Hospital':
                return redirect(next_page) if next_page else redirect(url_for('hospital_operation'))
            elif current_user.role == 'Doctor':
                return redirect(next_page) if next_page else redirect(url_for('doctor_operation'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('patient_operation'))
            #return redirect(url_for('user_operation'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#  role, name, email, password, contact_no, address, pincode, test_result, book_test_time, book_vaccine_time, doctor_email
@app.route("/patient_operation", methods=['GET', 'POST'])
@login_required(role="Patient")
def patient_operation():
    form = BookingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        dates = datetime.datetime.now() + datetime.timedelta(days=1)
        if(form.booking.data == 'Take Covid-19 Test'):
            user.book_test_time = str(dates)
        if(form.booking.data == 'Take Covid-19 Vaccine'):
            user.book_vaccine_time = str(dates)
        pincode_all = User.query.filter_by(role='Hospital').all()
        pincode = []
        for i in pincode_all:
            pincode.append(int(i.pincode))
        print(type(pincode), pincode)
        hospital_pincode = min(pincode, key=lambda x:abs(x-int(current_user.pincode)))
        print('hospital_pincode',hospital_pincode)
        hospital_info = User.query.filter_by(role='Hospital', pincode=str(hospital_pincode)).first()
        db.session.commit()
        print(user, hospital_info)
        flash('You booking is successful!', 'success')
        message = 'Your ' + form.booking.data.replace('Take ', '') + ' is allocated on ' + hospital_info.name + '''
        Address: ''' + hospital_info.address + '''
        Contact: ''' + hospital_info.contact_no + '''
        Date: ''' + str(dates.date()) + '''
        Time: ''' +  str(dates.time())


        return render_template('patient_operation.html', title='Patient', form=form, message=message)
        
    return render_template('patient_operation.html', title='Patient', form=form)

@app.route("/patient_chat", methods=['GET', 'POST'])
@login_required(role="Patient")
def patient_chat():
    form = ChatForm()
    print('cu', current_user.doctor_email)
    if form.validate_on_submit():
            print('enter')
            try:
                user = Chat(from_email=current_user.email, to_email=current_user.doctor_email, message=form.message.data, time=str(time.time()))
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                print('ex', e)
            print(user)
            flash('You message is sent!', 'success')
            return redirect(url_for('patient_chat'))

    if(current_user.doctor_email != None):
        form = ChatForm()
        print('chat')
        patient_chat = Chat.query.filter_by(from_email=current_user.email).all()
        doctor_chat = Chat.query.filter_by(from_email=current_user.doctor_email).all()
        chat = []
        for i in patient_chat:
            chat.append(i)
        for i in doctor_chat:
            chat.append(i)
        time_sort = []
        for i in chat:
            time_sort.append(float(i.time))
        time_index = [i[0] for i in sorted(enumerate(time_sort), key=lambda x:x[1], reverse=True)]
        sorted_chat = []
        for i in time_index:
            idd = chat[i].id
            print('idd', idd)
            idd = Chat.query.filter_by(id=idd).first().from_email
            sorted_chat.append([idd, chat[i].message])
        return render_template('patient_chat.html', title='Patient', form=form, sorted_chat=sorted_chat)


    else:
        flash('You have to wait for your test results, if you take Covid-19 test...', 'danger')
        return redirect(url_for('patient_operation'))


@app.route("/doctor_operation", methods=['GET', 'POST'])
@login_required(role="Doctor")
def doctor_operation():
    patient_info = User.query.filter_by(doctor_email=current_user.email).all()        
    return render_template('doctor_operation.html', title='Doctor', patient_info=patient_info)

@app.route("/doctor_chat/<patient_email>", methods=['GET', 'POST'])
@login_required(role="Doctor")
def doctor_chat(patient_email):
    form = ChatForm()
    print(patient_email)
    patient_chat = Chat.query.filter_by(from_email=patient_email).all()
    doctor_chat = Chat.query.filter_by(from_email=current_user.email, to_email=patient_email).all()
    chat = []
    for i in patient_chat:
        chat.append(i)
    for i in doctor_chat:
        chat.append(i)
    time_sort = []
    for i in chat:
        time_sort.append(float(i.time))
    time_index = [i[0] for i in sorted(enumerate(time_sort), key=lambda x:x[1], reverse=True)]
    sorted_chat = []
    for i in time_index:
        idd = chat[i].id
        print('idd', idd)
        idd = Chat.query.filter_by(id=idd).first().from_email
        sorted_chat.append([idd, chat[i].message])

    if form.validate_on_submit():
        print(current_user.email, patient_email)
        user = Chat(from_email=current_user.email, to_email=patient_email, message=form.message.data, time=str(time.time()))
        db.session.add(user)
        db.session.commit()

        print(user)
        flash('You message is sent!', 'success')
        return redirect(url_for('doctor_operation'))
        
    return render_template('doctor_chat.html', title='Doctor', form=form, sorted_chat=sorted_chat)



@app.route("/hospital_operation", methods=['GET', 'POST'])
@login_required(role="Hospital")
def hospital_operation():
    patient_info = User.query.filter(User.book_test_time != None, User.role=='Patient', User.test_result==None).all()
    print(patient_info)
    doctor_emails = User.query.filter_by(role='Doctor')
    print(doctor_emails)
    patients = []
    doctors = []
    for i in doctor_emails:
        doc_name = User.query.filter_by(email=i.email).first()
        print(doc_name)
        doctors.append(doc_name.name)
        user = User.query.filter_by(doctor_email=i.email)
        temp_names = []
        for u in user:
            temp_names.append(u.name)
        patients.append(temp_names)
    print('doc', doctors)
    print('patients', patients)
    names = []
    for i, j in zip(doctors, patients):
        names.append([i, j])
    return render_template('hospital_operation.html', title='Hospital',patient_info=patient_info, doctors=doctors,
                           patients=patients, names=names)


@app.route("/test_result/<patient_email>/<result>", methods=['GET', 'POST'])
@login_required(role="Hospital")
def test_result(patient_email, result):
    patient_info = User.query.filter_by(email=patient_email).first()
    print(patient_info)  
    doctor_info = User.query.filter_by(role='Doctor').all() 
    print('doctor_info', len(doctor_info))
    selected_doctor = random.choice(doctor_info)
    print('sd', selected_doctor)
    patient_info.doctor_email = selected_doctor.email
    patient_info.test_result = result
    db.session.commit()
    flash('Test Result is Updated and a Doctor is Allocated', 'success')
    return redirect(url_for('hospital_operation'))

 
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

