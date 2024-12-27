from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import login_required, current_user

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import re
from backend.models import *

def init_app():
    # Initialize the Flask application
    app = Flask(__name__)

    # Configure the SQLite database
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db?timeout=20'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'  # Required for using flash messages

    # Initialize the LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Specify the login view
    # login_manager.login_message_category = "info"  
    # # Customize flash message category for login-required pages


    # Define a user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.debug = True
    # Initialize the SQLAlchemy database
    #db = SQLAlchemy(app)
    db.init_app(app)

    print("Application Started!")
    return app

app = init_app()

# ROUTES FOR ALL USERS

# SIGN-UP AND LOGIN ROUTES
# Sign-up route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        # Collect form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        pincode = request.form.get("pincode")
        contact_num = request.form.get("contact_num")
        address = request.form.get("address")
        role = request.form.get("role")

        print(username, password, email, pincode, contact_num, address, role)

        # Server-side validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return redirect(url_for('signup'))

        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('signup'))

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('signup'))

        # If the role is customer
        if role == "customer":
            customer_data = User(
                name=username,
                email=email,
                password=password,  
                pincode=pincode,
                role=role,
                contact_num=contact_num,
                address=address
            )
            db.session.add(customer_data)
            db.session.commit()
            db.session.close()
            flash('Account created successfully. Please wait for Admin approval!', 'success')
            return redirect(url_for('login'))

        # If the role is professional
        elif role == "professional":
            service_type = request.form.get("service_type")
            experience = request.form.get("experience")
            #attachdoc = request.form.get("attachdoc")  
            professional_data = User(
                name=username,
                email=email,
                password=password,  
                pincode=pincode,
                role=role,
                contact_num=contact_num,
                address=address,
                service_type=service_type,
                experience=experience
            )
            db.session.add(professional_data)
            db.session.commit()
            db.session.close()
            flash('Professional account created successfully! Please wait for Admin approval.', 'success')
            return redirect(url_for('login'))

    return render_template("signup.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Add login logic here
        username = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = username).first()
        # print(user)
        if user and user.regn_status == 1:
            if user.password == password:
                if user.role == "Admin":
                    login_user(user)  # Logs in the user
                    flash("Logged in successfully as Admin" , category = "success")
                    return redirect(url_for('admin_dash'))
                if user.role == "professional":
                    if user.flag == 1 or user.block == 1:
                        flash("User is Flagged or Blocked!", category = "error")
                        return redirect(url_for('login'))
                    else:
                        login_user(user)  # Logs in the user

                        flash("Logged in successfully as Professional" , category = "success")
                        return redirect(url_for('pro_home'))
                if user.role == "customer":
                    if user.flag == 1 or user.block == 1:
                        flash("User is Flagged or Blocked!", category = "error")
                        return redirect(url_for('login'))
                    else:
                        login_user(user)  # Logs in the user
                        flash("Thank you for being our favourite customer!!" , category = "success")
                        return redirect(url_for('cus_home'))
                        # services =  Service.query.all()
                        # return render_template("cus_home.html", services = services) 
            else:
                flash("Invalid Credentials! Please try again",category = "error")
                return render_template("all_login.html",msg = "Invalid Credentials")
        else:
            flash("Invalid Credentials",category = "error")
            return render_template("all_login.html",msg = "Invalid Credentials")
        
    return render_template("all_login.html")

# Forgot Password 
@app.route("/forgot_password", methods = ["GET","POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("username")
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")
        user = User.query.filter_by(email = email).first()
        if user and new_password == confirm_password:
            user.password = new_password
            db.session.commit()
            db.session.close()
            flash("Password Updated Successfully! You may Login now.", category = "success")
            return redirect(url_for('login'))
        else:
            flash("Email not found", category = "error")
            return redirect(url_for('forgot_password'))
    else:
        return render_template("forgot_password.html")


# HOME and LOGOUT 
# Home route
@app.route("/")
def all_home():
    return render_template("all_home.html")

# Logout route
@app.route("/logout", methods = ["GET","POST"])
@login_required
def logout():
    return render_template("all_login.html")


# ROUTES FOR ADMIN

# admin_dash route
@app.route("/admin_dash", methods = ["GET","POST"])
@login_required
def admin_dash():
    users = User.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    return render_template("admin_dash.html", name = current_user.name,
                           users=users, services=services, 
                           service_requests=service_requests)

# Admin search route
@app.route("/ad_search", methods = ["GET","POST"])
@login_required
def ad_search():
    if request.method == "POST":
        search_query = request.form.get("search-text")
        # filter = request.form.get("search-by") # dropdown
        if search_query:
            users = User.query.filter(User.name.ilike(f"%{search_query}%")).all()
            return render_template("ad_search.html",users=users)
        else:
            flash("Please enter a search query.", "error")
            return render_template("ad_search.html")
    else:
        return render_template("ad_search.html")

# Admin summary route
@app.route("/ad_summary", methods = ["GET","POST"])
@login_required
def ad_summary():
    return render_template("ad_summary.html")

# Admin review route
@app.route("/ad_review", methods = ["GET","POST"])
@login_required
def ad_review():
    return render_template("ad_review.html")

# ad_create_service route
@app.route("/add_service", methods = ["GET","POST"])
def add_service():
    if request.method == "POST":
        service_name = request.form.get("service_name")
        description = request.form.get("description")
        base_price = request.form.get("base_price")
        pincode = request.form.get("pincode")
        service_data = Service(service_name=service_name, 
                               description=description, budget=base_price, 
                               professional_id=0, pincode=pincode)
        db.session.add(service_data)
        db.session.commit()
        db.session.close()
        flash("Service added successfully!", category="success")
        return redirect(url_for('admin_dash'))

    return render_template("add_service.html")


# Utility function to validate email
def validate_email(email):
    # Basic email validation using regex
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)


# FLAG and UNFLAG, BLOCK and UNBLOCK ROUTES
# Flag route
@app.route("/flag/<int:user_id>", methods=["GET", "POST"])
def flag(user_id):
    print(user_id)
    try:
        user = User.query.filter_by(id=user_id).first()
        if user:
            if user.flag == 0:
                user.flag = 1
            db.session.commit()  # Commit changes
            db.session.close()
            flash("User has been FLAGGED", category="success")
        else:
            flash("User not found!", category="error")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash("Database error: " + str(e), category="error")
    finally:
        db.session.close()  # Ensure session is closed
        
    return redirect(url_for('admin_dash'))  # Redirect after the operation
    
    flash("Something is wrong!!", category="error")
    return redirect(url_for('admin_dash'))

# Unflag route
@app.route("/unflag/<int:user_id>", methods=["GET", "POST"])
def unflag(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        if user.flag == 1:
            user.flag = 0
        db.session.commit()
        db.session.close()
        flash("Unflagged Successfully",category="success")
        return redirect (url_for('admin_dash'))
    else:
        flash("Something went wrong!",category="error")
        return redirect (url_for('admin_dash'))

# Block user route
@app.route("/block/<int:user_id>", methods=["GET", "POST"])
def block(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if user and user.block == 0:
            user.block = 1  # Directly set block status
            db.session.commit()  # Commit changes
            db.session.close()
            flash("User has been BLOCKED", category="success")
        else:
            flash("User not found!", category="error")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash("Database error: " + str(e), category="error")
    finally:
        db.session.close()  # Ensure session is closed

    return redirect(url_for('admin_dash'))  # Redirect after the operation

# Unblock route
@app.route("/unblock/<int:user_id>", methods=["GET", "POST"])
def unblock(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if user and user.block == 1:
            user.block = 0  # Directly set block status
            db.session.commit()
            db.session.close()
            flash("User has been UNBLOCKED", category="success")
        else:
            flash("User not found!", category="error")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash("Database error: " + str(e), category="error")
    finally:
        db.session.close()  # Ensure session is closed

    return redirect(url_for('admin_dash'))


# EDIT AND DELETE SERVICE ROUTES

#Edit service route
@app.route("/edit_service/<int:service_id>", methods=["GET","POST"])
def edit_service(service_id):
    if request.method == "POST":
        service_name = request.form.get("service_name")
        description = request.form.get("description")
        base_price = request.form.get("base_price")
        pincode = request.form.get("pincode")
        service = Service.query.filter_by(id=service_id).first()
        if service:
            if service_name:
                service.service_name = service_name
            if description:
                service.description = description
            if pincode:
                service.pincode = pincode
            if base_price:
                service.budget = base_price
            db.session.commit()
            db.session.close()
            flash("Service updated successfully!", category="success")
            return redirect(url_for('admin_dash'))
        else:
            flash("Service not found!", category="error")
            return render_template('admin_dash.html', service_id = service_id)
    else:    
        service = Service.query.filter_by(id=service_id).first()
        service_name = service.service_name
        description = service.description
        budget = service.budget
        pincode = service.pincode
        return render_template("ad_edit_service.html", service_id = service_id,
                               service_name = service_name, description = description, 
                               pincode=pincode, budget = budget) 


#Delete service route
@app.route("/delete_service/<int:service_id>", methods=["GET","POST"])
def delete_service(service_id):
    if request.method == "POST":
        print ("Service id: ", service_id)
        service = Service.query.filter_by(id = service_id).first()
        print ("Service: ", service)
        if service:
            db.session.delete(service)
            db.session.commit()
            db.session.close()
            flash("Service deleted successfully!", category="success")
            return redirect(url_for('admin_dash'))
        else:
            flash("Service not found!", category="error")
            return redirect(url_for('admin_dash', service_id = service_id))
    else:
        
        return redirect(url_for('admin_dash'))
    

# ROUTES FOR PROFESSIONALS
# pro_home route
@app.route("/pro_home", methods = ["GET","POST"])
@login_required
def pro_home():
    services =  ServiceRequest.query.all()
    # service_requests = ServiceRequest.query.filter_by(professional_id = current_user.id).all()
    return render_template("pro_home.html", services = services, 
                           name = current_user.name)


# pro_accept_service route
@app.route("/pro_accept_service/<int:service_id>", methods=["GET","POST"])
@login_required
def pro_accept_service(service_id):
    print("User ID:", current_user.id)
    service_request = ServiceRequest.query.get(service_id)
    print("Service Request Status:", service_request.service_status)
    if service_request and service_request.service_status == "Requested":
        service_request.service_status = "Accepted"  # Assuming 'status' field tracks request status
        service_request.professional_id = current_user.id
        db.session.commit()
        db.session.close()
        flash("Service request accepted successfully.", category="success")
        return redirect(url_for('pro_home'))
    else:
        flash("Service request not found.", category="error")
        return redirect(url_for('pro_home'))

# pro_reject_service route
@app.route("/pro_reject_service/<int:service_id>", methods=["GET","POST"])
@login_required
def pro_reject_service(service_id):
    service_request = ServiceRequest.query.get(service_id)
    if service_request:
        service_request.service_status = "Rejected"
        db.session.commit()
        db.session.close()
        flash("Service request rejected.", category="info")
        return redirect(url_for('pro_home'))
    else:
        flash("Service request not found.", category="error")
        return redirect(url_for('pro_home'))


# pro_search route
@app.route("/pro_search", methods = ["GET","POST"])
def pro_search():
    if request.method == "POST":
        query = request.form.get("searchText")
        filter = request.form.get("searchBy")
        if filter == "service-name":
            services = Service.query.filter(Service.service_name.ilike(f"%{query}%")).all()
            print(services)
            if services:
                return render_template("pro_search.html", services=services)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        elif filter == "pincode":
            service_requests = ServiceRequest.query.filter(ServiceRequest.pincode.like(f"%{query}%")).all()
            print(service_requests)
            if service_requests:
                return render_template("pro_search.html", service_requests=service_requests)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        elif filter == "status":
            service_requests = ServiceRequest.query.filter(ServiceRequest.service_status.like(f"%{query}%")).all()
            # print(service_requests)
            if service_requests:
                return render_template("pro_search.html", service_requests=service_requests)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        else:
            services = ServiceRequest.query.all()
            return render_template("pro_search.html", services=services)
    else:
        return render_template("pro_search.html")

# pro_summary route
@app.route("/pro_summary", methods = ["GET","POST"])
def pro_summary():
    return render_template("pro_summary.html")

# pro_approve route
@app.route("/pro_approve/<int:user_id>", methods = ["GET","POST"])
def pro_approve(user_id):
    user = User.query.get(user_id)
    if user :
        user.regn_status = 1
        db.session.commit()
        db.session.close()
        flash("User Approved Successfully",category = "success")
        return redirect(url_for('admin_dash'))      
    else:
        flash("User not found",category = "error")
        return redirect(url_for('admin_dash'))

#pro_reject route
@app.route("/pro_reject/<int:user_id>", methods = ["GET","POST"])
def pro_reject(user_id):
    user = User.query.get(user_id)
    if user :
        user.regn_status = 0
        db.session.commit()
        db.session.close()
        flash("Oops! User Rejected!!",category = "success")
        return redirect(url_for('admin_dash'))      
    else:
        flash("User not found",category = "error")
        return redirect(url_for('admin_dash'))
    
# pro_complete route
@app.route("/pro_complete/<int:service_id>", methods=["GET", "POST"])
@login_required
def pro_complete(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        if request.method == "POST":
            if service.service_status == "Requested" or service.service_status == "Accepted":
                service.service_status = "Closed"
                db.session.commit()
                db.session.close()
                flash("Service marked as completed!", category="success")
                return redirect(url_for('pro_home'))
        else:
            return render_template("pro_complete.html", service=service, service_id=service_id)
    else:
        flash("Service not found", category="error")
        return redirect(url_for('pro_home'))
    
# pro_serv_review route
@app.route("/pro_serv_review", methods = ["GET","POST"])
def pro_serv_review():
    return render_template("pro_serv_review.html")


# ROUTES FOR CUSTOMERS

# cus_home route
@app.route("/cus_home", methods = ["GET","POST"])
@login_required
def cus_home():
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    # print(current_user.id)
    return render_template("cus_home.html",services = services, name = current_user.name,
                           service_requests = service_requests)

# cus_search route
@app.route("/cus_search", methods = ["GET","POST"])
def cus_search():
    if request.method == "POST":
        query = request.form.get("searchText")
        filter = request.form.get("searchBy")
        if filter == "service-name":
            services = Service.query.filter(Service.service_name.ilike(f"%{query}%")).all()
            print(services)
            if services:
                return render_template("cus_search.html", services=services)
            else:
                flash("No services found with this spectification.", category="error")
                return render_template("cus_search.html")
        elif filter == "pincode":
            services = Service.query.filter(Service.pincode.like(f"%{query}%")).all()
            # flash("No services found for this pincode.", category="error")
            return render_template("cus_search.html", services=services)
        elif filter == "status":
            service_requests = ServiceRequest.query.filter(ServiceRequest.service_status.like(f"%{query}%")).all()
            # flash("No service requests found with this spectification.", category="error")
            return render_template("cus_search.html", service_requests=service_requests)
        else:
            services = Service.query.all()
            flash("No services found with this spectification.", category="error")
            return render_template("cus_search.html", services=services)
    else:
        return render_template("cus_search.html")

# cus_summary route
@app.route("/cus_summary", methods = ["GET","POST"])
def cus_summary():
    return render_template("cus_summary.html")

# cus_serv_review route
@app.route("/cus_serv_review", methods = ["GET","POST"])
def cus_serv_review():
    return render_template("cus_serv_review.html")

# payments route
@app.route("/payments", methods = ["GET","POST"])
def payments():
    return render_template("payments.html")

from flask import Flask, render_template, redirect, url_for, flash


@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Process payment logic here, if any
    flash("Payment Completed! Please visit the Home Page to check your booked services.")
    return redirect(url_for('payment_cnf'))

@app.route('/payment_cnf', methods=['GET'])
def payment_cnf():
    return render_template('payment_cnf.html')

# cus_book_service route
@app.route("/cus_book_service/<int:service_id>", methods=["GET", "POST"])
@login_required  
def cus_book_service(service_id):
    if request.method == "POST":
        if current_user.role == "customer":
            # Retrieve current user's ID
            user_id = current_user.id
            print("User ID:", user_id)
            print("Pincode:", current_user.pincode)
            
            # Collect form data
            description = request.form.get("description")
            pincode = request.form.get("pincode")
            base_price = request.form.get("payment_amount")
            date_of_request = request.form.get("date_of_request")
            date_of_completion = request.form.get("date_of_completion")
            remarks = request.form.get("remarks")
            date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d')
            date_of_completion = datetime.strptime(date_of_completion, '%Y-%m-%d')
            # Assuming you have a ServiceRequest model to store the booking information
            service_request = ServiceRequest(
                customer_id=user_id,  service_id=service_id, date_of_request=date_of_request,
                date_of_completion=date_of_completion, requirements=description,
                messages=remarks, payment_amount=base_price, professional_id=0, pincode = current_user.pincode)
        
            # Save the booking in the database
            db.session.add(service_request)
            db.session.commit()
            db.session.close()
            flash("Service booked successfully!", category="success")
            return redirect(url_for('payments'))
    else:
        service = Service.query.get(service_id)
        return render_template("cus_book_service.html", service_id=service_id, service=service)

    
# cus_edit_service route
@app.route("/cus_edit_service/<int:service_id>", methods=["GET", "POST"])
@login_required
def cus_edit_service(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        if request.method == "POST":
            service_id = request.form.get("service_id")
            date_of_request = request.form.get("date_of_request")
            date_of_completion = request.form.get("date_of_completion")
            remarks = request.form.get("remarks")

            if service_id:
                service.service_id = service_id
            if date_of_request:
                date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d')
                service.date_of_request = date_of_request
            if date_of_completion:
                date_of_completion = datetime.strptime(date_of_completion, '%Y-%m-%d')
                service.date_of_completion = date_of_completion
            if remarks:
                service.messages = remarks
            db.session.commit()
            db.session.close()
            flash("Service updated successfully!", category="success")
            return redirect(url_for('cus_home'))
        else:
            service = ServiceRequest.query.get(service_id)
            return render_template("cus_edit_service.html", request=service, service_id=service_id)
            
@app.route("/cus_serv_change_status/<int:service_id>", methods=["GET", "POST"])
@login_required
def cus_serv_change_status(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        if request.method == "POST":
            if service.service_status == "Rejected":
                service.service_status = "Requested"
                db.session.commit()
                db.session.close()
                flash("Service status updated successfully!", category="success")
                return redirect(url_for('cus_home'))
            else:
                flash("Service status cannot be changed!", category="error")
                return redirect(url_for('cus_home'))
        else:
            return render_template("cus_home.html", service=service, service_id=service_id)
    else:
        flash("Service status cannot be changed!", category="error")
        return redirect(url_for('cus_home'))

# mark_as_complete route
@app.route("/mark_as_complete/<int:service_id>", methods=["GET", "POST"])
@login_required
def mark_as_complete(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        if request.method == "POST":
            if service.service_status == "Requested" or service.service_status == "Assigned":
                service.service_status = "Closed"
                db.session.commit()
                db.session.close()
                flash("Service marked as completed!", category="success")
                return redirect(url_for('cus_home'))
        else:
            return render_template("mark_as_complete.html", service=service, service_id=service_id)
    else:
        flash("Service not found", category="error")
        return redirect(url_for('cus_home'))

# cus_approve route
@app.route("/cus_approve/<int:user_id>", methods = ["GET","POST"])
def cus_approve(user_id):
    user = User.query.get(user_id)
    if user :
        user.regn_status = 1
        db.session.commit()
        db.session.close()
        flash("User Approved Successfully",category = "success")
        return redirect(url_for('admin_dash'))      
    else:
        flash("User not found",category = "error")
        return redirect(url_for('admin_dash'))
    

#cus_reject route
@app.route("/cus_reject/<int:user_id>", methods = ["GET","POST"])
def cus_reject(user_id):
    user = User.query.get(user_id)
    if user :
        user.regn_status = 0
        db.session.commit()
        db.session.close()
        flash("Oops! User Rejected!!",category = "success")
        return redirect(url_for('admin_dash'))      
    else:
        flash("User not found",category = "error")
        return redirect(url_for('admin_dash'))


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates database tables
    app.run(debug = True)
