from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_mail import Mail, Message
from models import db, UserProfile, EducationDetail, LanguageSkill, User
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
app.config['MAIL_USERNAME'] = 'info.goldwingsaviation@gmail.com'
app.config['MAIL_PASSWORD'] = 'bclh ncrq aawi rmeg'
mail = Mail(app)

# Init DB
db.init_app(app)

@app.route('/')
def home():
    return render_template("home.html", page="Home")

@app.route('/about')
def about():
    return render_template("about.html", page="About")

@app.route('/services')
def services():
    return render_template("service.html", page="Services")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        msg = Message(subject="New Contact Query",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['info.goldwingsaviation@gmail.com'])
        msg.body = f"You have received a new contact message:\n\nName: {name}\nEmail: {email}\n\nMessage:\n{message}"
        mail.send(msg)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template("contact.html", page="Contact")

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
def apply():
    if request.method == 'POST':
        form = request.form

        # Check if user already exists
        existing_user = User.query.filter_by(email=form['primary_email']).first()

        if existing_user:
            user = existing_user
        else:
            user = User(
                email=form['primary_email'],
                password_hash='temporary',
                role='User'
            )
            db.session.add(user)
            db.session.commit()

        # Delete previous related data (if any) to avoid UNIQUE constraint errors
        UserProfile.query.filter_by(user_id=user.id).delete()
        EducationDetail.query.filter_by(user_id=user.id).delete()
        LanguageSkill.query.filter_by(user_id=user.id).delete()

        # Create and link UserProfile
        profile = UserProfile(
            user_id=user.id,
            first_name=form['first_name'],
            middle_name=form.get('middle_name'),
            last_name=form['last_name'],
            date_of_birth=datetime.strptime(form['dob'], '%Y-%m-%d').date(),
            gender=form['gender'],
            primary_email=form['primary_email'],
            mobile_number=form['mobile_number'],
            emergency_name=form['emergency_name'],
            emergency_relationship=form['emergency_relationship'],
            emergency_phone=form['emergency_phone'],
            nationality=form['nationality'],
            country_of_birth=form['country_of_birth'],
            citizenship_status=form['citizenship_status']
        )
        db.session.add(profile)

        # Create and link EducationDetail
        education = EducationDetail(
            user_id=user.id,
            secondary_education_level=form['secondary_education_level'],
            highest_completed_level=form['highest_completed_level'],
            still_enrolled=bool(form.get('still_enrolled')),
            previous_qualification=form.get('previous_qualification') or None
        )
        db.session.add(education)

        # Create and link LanguageSkill
        language = LanguageSkill(
            user_id=user.id,
            english_proficiency=form['english_proficiency'],
            other_languages=form.get('other_languages')
        )
        db.session.add(language)

        # Commit all
        db.session.commit()

        # Generate PDF
        html = render_template("pdf_template.html", form=form)
        pdf = BytesIO()
        pisa.CreatePDF(html, dest=pdf)
        pdf.seek(0)

        # Send to recruiter
        recruiter_msg = Message("New Application Submission",
                                sender=app.config['MAIL_USERNAME'],
                                recipients=["info.goldwingsaviation@gmail.com"],
                                reply_to=form['primary_email'],
                                body="A new application has been submitted.")
        recruiter_msg.attach("application.pdf", "application/pdf", pdf.read())
        mail.send(recruiter_msg)

        # Send confirmation to applicant
        user_msg = Message("Application Received",
                           sender=app.config['MAIL_USERNAME'],
                           recipients=[form['primary_email']],
                           body="Thank you for submitting your application. We have received it.")
        mail.send(user_msg)

        flash("Application submitted successfully. Confirmation email sent.", "success")
        return redirect(url_for('end'))

    # Choices for the form
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
def end():
    return render_template('end.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')

    if email:
        msg = Message("New Email Subscription",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=["info.goldwingsaviation@gmail.com"])
        msg.body = f"New subscriber: {email}"
        mail.send(msg)
        flash("Thank you for subscribing!", "success")
    else:
        flash("Please enter a valid email.", "danger")

    return redirect(request.referrer or url_for('home'))

@app.route('/mission')
def mission():
    return render_template('mission.html', page="Our Mission")

@app.route('/values')
def values():
    return render_template('values.html', page="Our Values")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
