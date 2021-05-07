from datetime import datetime
from hms import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
#hospital-admin, doctors-self, patients-self
    id = db.Column(db.Integer,primary_key=True)
    role = db.Column(db.String(80))
    name = db.Column(db.String(80))
    email = db.Column(db.String(256),unique=True)
    password = db.Column(db.String(200))
    contact_no = db.Column(db.String(20))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(200))
    test_result = db.Column(db.String(20), nullable=True)
    book_test_time = db.Column(db.String(120), nullable=True)
    book_vaccine_time = db.Column(db.String(120), nullable=True)
    doctor_email = db.Column(db.String(256), nullable=True)#doctor to take care-allocated doctor email


    def __init__(self, role, name, email, password, contact_no, address, pincode, test_result, book_test_time, book_vaccine_time, doctor_email):
            self.role = role
            self.name = name
            self.email = email
            self.password = password
            self.contact_no = contact_no
            self.address = address
            self.pincode = pincode
            self.test_result = test_result
            self.book_test_time = book_test_time
            self.book_vaccine_time = book_vaccine_time
            self.doctor_email = doctor_email

    def get_role(self):
            return self.role

    def __repr__(self):
        return f"User('{self.role}', '{self.name}', '{self.email}', '{self.contact_no}', '{self.address}', '{self.pincode}', '{self.test_result}', \
        '{self.book_test_time}', '{self.book_vaccine_time}', '{self.doctor_email}',)"


class Chat(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    from_email = db.Column(db.String(256), nullable=False)
    to_email = db.Column(db.String(256), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    time = db.Column(db.String(120), nullable=False)#print(datetime.utcfromtimestamp(a[1]).strftime('%Y-%m-%d %H:%M:%S'))

    def __repr__(self):
        return f"Chat('{self.from_email}', '{self.to_email}', '{self.message}', '{self.time}')"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20))
    password = db.Column(db.String(120))