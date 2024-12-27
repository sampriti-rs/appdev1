from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    contact_num = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(30), nullable=False)  

    # professional_exclusive
    service_type = db.Column(db.String(64), nullable=True)  
    experience = db.Column(db.Integer, nullable=True)
    regn_status = db.Column(db.Boolean, nullable=False, default=False)
    #attachdoc = db.Column(db.LargeBinary, nullable=True, default = b'')  
    
    flag = db.Column(db.Boolean, default=False)
    block = db.Column(db.Boolean, default=False)


    # Explicitly define the foreign keys in relationships
    services = db.relationship('Service', backref='professional', cascade="all,delete", lazy=True)
    customer_requests = db.relationship('ServiceRequest', backref='customer', cascade="all,delete",
                                        lazy=True, foreign_keys='ServiceRequest.customer_id')
    professional_requests = db.relationship('ServiceRequest', backref='professional', cascade="all,delete",
                                            lazy=True, foreign_keys='ServiceRequest.professional_id')


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_requests = db.relationship('ServiceRequest', backref='service', cascade="all,delete", lazy=True)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=True)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    service_status = db.Column(db.String(10), nullable=False, 
                               default="Requested")  #"Requested" or "Assigned" or "Closed"
    messages = db.Column(db.Text, nullable=True)
    pincode = db.Column(db.Integer, nullable=False)