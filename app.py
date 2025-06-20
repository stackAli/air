from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_mail import Mail, Message
from models import db, User, UserProfile, EducationDetail, LanguageSkill
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aftabdawood36@gmail.com'
app.config['MAIL_PASSWORD'] = 'strx ybzm ekuo weux'
mail = Mail(app)

# Init DB and Login Manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("home.html", page="Home")

@app.route('/about')
def about():
    return render_template("about.html", page="about")

@app.route('/services')
def services():
    return render_template("service.html", page="Services")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Email to admin
        msg = Message(subject="New Contact Query",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['aftabdawood36@gmail.com'])  # Admin Email
        msg.body = f"You have received a new contact message:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
        mail.send(msg)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template("contact.html", page="Contact")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('apply'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('login'))

    return render_template("login.html", page="Login")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'User')

        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful. You can now log in.")
        return redirect(url_for('login'))

    return render_template("signup.html", page="Signup")

@app.route('/rpl')
def rpl():
    return render_template("rpl.html", page="RPL")

@app.route('/tif')
def cpl():
    return render_template("tif.html", page="TIF")
@app.route('/ppl')
def ppl():
    return render_template("ppl.html", page="PPL")

@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if request.method == 'POST':
        form = request.form

        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.session.add(profile)

        profile.title = form['title'].title()
        profile.first_name = form['first_name']
        profile.middle_name = form.get('middle_name')
        profile.last_name = form['last_name']
        profile.date_of_birth = datetime.strptime(form['dob'], '%Y-%m-%d').date()
        profile.gender = form['gender']
        profile.primary_email = form['primary_email']
        profile.alternative_email = form.get('alternative_email')
        profile.mobile_number = form['mobile_number']
        profile.home_phone = form.get('home_phone')
        profile.emergency_name = form['emergency_name']
        profile.emergency_relationship = form['emergency_relationship']
        profile.emergency_phone = form['emergency_phone']
        profile.nationality = form['nationality']
        profile.country_of_birth = form['country_of_birth']
        profile.citizenship_status = form['citizenship_status']

        education = EducationDetail.query.filter_by(user_id=current_user.id).first()
        if not education:
            education = EducationDetail(user_id=current_user.id)
            db.session.add(education)

        education.secondary_education_level = form['secondary_education_level']
        education.highest_completed_level = form['highest_completed_level']
        education.still_enrolled = bool(form.get('still_enrolled'))
        education.previous_qualification = form.get('previous_qualification')

        language = LanguageSkill.query.filter_by(user_id=current_user.id).first()
        if not language:
            language = LanguageSkill(user_id=current_user.id)
            db.session.add(language)

        language.english_proficiency = form['english_proficiency']
        language.other_languages = form.get('other_languages')

        db.session.commit()

        # Generate PDF
        html = render_template("pdf_template.html", form=form)
        pdf = BytesIO()
        pisa.CreatePDF(html, dest=pdf)
        pdf.seek(0)

        # Email to recruiter
        recruiter_msg = Message("New Application Submission",
                                sender=app.config['MAIL_USERNAME'],
                                recipients=["recruiter@example.com"],
                                body="A new application has been submitted.")
        recruiter_msg.attach("application.pdf", "application/pdf", pdf.read())
        mail.send(recruiter_msg)

        # Email to user
        user_msg = Message("Application Received",
                           sender=app.config['MAIL_USERNAME'],
                           recipients=[form['primary_email']],
                           body="Thank you for submitting your application. We have received it.")
        mail.send(user_msg)

        flash("Application submitted successfully. Confirmation email sent.", "success")
        return redirect(url_for('end'))

    title_choices = ['Mr', 'Mrs', 'Miss', 'Ms', 'Dr']
    gender_choices = ['Male', 'Female', 'Other']
    citizenship_choices = ['Citizen', 'Permanent Resident', 'International']
    qualification_choices = ['None', "Bachelor's", "Master's", 'Diploma']
    english_proficiency_choices = ['Fluent', 'Intermediate', 'Basic']

    return render_template("apply.html",
                           page="Apply",
                           title_choices=title_choices,
                           gender_choices=gender_choices,
                           citizenship_choices=citizenship_choices,
                           qualification_choices=qualification_choices,
                           english_proficiency_choices=english_proficiency_choices)

@app.route('/end')
@login_required
def end():
    return render_template('end.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


from flask import request, redirect, url_for, flash
from flask_mail import Message

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')

    if email:
        msg = Message("New Email Subscription",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=["aftabdawood36@gmail.com"])
        msg.body = f"New subscriber: {email}"
        mail.send(msg)

        flash("Thank you for subscribing!", "success")
    else:
        flash("Please enter a valid email.", "danger")

    return redirect(request.referrer or url_for('home'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)