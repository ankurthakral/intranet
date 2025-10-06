import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
import psycopg2
import os
import bcrypt
import random

# Initialize Flask app
app = Flask(__name__)

# Secure secret key
app.secret_key = "be8920e4e2e25f4e6654970f9148dbadc07b056795473592a58c92e09a67aea2"

# CSRF protection
csrf = CSRFProtect(app)


# Configure PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost:5433/intranet"

# mail Configuration
app.config["MAIL_SERVER"] = "mail.railtelindia.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_DEBUG"] = True
app.config["MAIL_USERNAME"] = "fp@railtelindia.com"
app.config["MAIL_PASSWORD"] = "Login@#@!"
mail = Mail(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler(),  # Log to console
    ],
)


# Connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Database connection established successfully.")
        return conn
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        raise


@app.route("/", methods=["GET", "POST"])
def login():
    logging.info("Login route accessed. Method: %s", request.method)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        logging.debug("Received login attempt. Email: %s", email)

        if not email or not password:
            logging.warning("Email or password not provided.")
            flash("Email and password are required.", "danger")
            return redirect(url_for("login"))

        if not email.endswith("@railtelindia.com"):
            logging.warning("Invalid email domain: %s", email)
            flash("Please use a valid RailTel India email ID.", "danger")
            return redirect(url_for("login"))

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    logging.debug("Querying the database for user: %s", email)
                    cur.execute("SELECT password FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()

                    if user:
                        logging.debug("User found in database. Verifying password...")
                        if bcrypt.checkpw(
                            password.encode("utf-8"), user[0].encode("utf-8")
                        ):
                            session["logged_in"] = True
                            session["email"] = email
                            logging.info("User logged in successfully: %s", email)
                            flash("Login successful!", "success")
                            return redirect(url_for("index"))
                        else:
                            logging.warning("Invalid password for user: %s", email)
                            flash("Invalid email or password.", "danger")
                    else:
                        logging.warning("No user found with email: %s", email)
                        flash("Invalid email or password.", "danger")
        except Exception as e:
            logging.error("An error occurred during login: %s", e)
            flash("An error occurred during login. Please try again.", "danger")

    return render_template("login.html")


# Route to serve the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("email")
        password = request.form.get("password")

        if not email.endswith("@railtelindia.com"):
            print("Please use a valid RailTel India email ID.", "danger")
            flash("Please use a valid RailTel India email ID.", "danger")
            return redirect(url_for("register"))

        # Validate password
        if (
            len(password) < 12
            or not any(c.islower() for c in password)
            or not any(c.isupper() for c in password)
            or not any(c.isdigit() for c in password)
            or not any(c in "!@#$%^&;:*()-_+=" for c in password)
        ):
            flash(
                "Password must be at least 12 characters long and include uppercase, lowercase, numbers, and special characters.",
                "danger",
            )
            print(
                "Password must be at least 12 characters long and include uppercase, lowercase, numbers, and special characters.",
                "danger",
            )

            return redirect(url_for("register"))

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Generate OTP
        otp = random.randint(100000, 999999)

        session["otp"] = otp
        session["email"] = email
        session["first_name"] = first_name
        session["last_name"] = last_name
        session["password"] = hashed_password

        # Send OTP via email
        try:
            msg = Message(
                subject="Your OTP for RailTel Registration",
                sender="fp@railtelindia.com",
                recipients=[email],
            )

            msg.body = f"Your OTP is: {otp}\nPlease use this OTP to complete your registration."

            msg.html = f"<p>Hello, <br /> Please use the OTP below to Verify Yourself</p> \n<strong>{otp}</strong> <p>--sent by RailTel</p><p>Regards, RailTel Silver Jubilee.</p>"

            try:
                mail.send(msg)
                flash("OTP sent to your email address.", "success")
                return redirect(url_for("verify_register_otp"))
            except:
                flash(f"Failed to send OTP. Error: {str(e)}", "danger")

        except Exception as e:
            flash(f"Failed to send OTP. Error: {str(e)}", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")


# Route to verify registration OTP
@app.route("/verify-register-otp", methods=["GET", "POST"])
def verify_register_otp():
    if request.method == "POST":
        user_otp = request.form.get("otp")

        if str(user_otp) == str(session.get("otp")):
            with connect_db() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(
                            "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                            (
                                session["first_name"],
                                session["last_name"],
                                session["email"],
                                session["password"],
                            ),
                        )
                        conn.commit()
                        flash("Registration successful! You can now log in.", "success")
                        session.clear()
                        return redirect(url_for("login"))
                    except Exception as e:
                        flash(f"Database error: {str(e)}", "danger")
                        return redirect(url_for("register"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            # return redirect(url_for("login"))

    return render_template("verify_register_otp.html")


# Route to handle forgot password page
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("regMail")

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("forgot_password"))

        # Check if email exists in the database
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT email FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()

                    if not user:
                        flash("No user found with this email.", "danger")
                        return redirect(url_for("forgot_password"))

                    # Generate OTP
                    otp = random.randint(100000, 999999)

                    session["reset_email"] = email
                    session["reset_otp"] = otp

                    # Send OTP via email
                    msg = Message(
                        subject="Your Password Reset OTP",
                        sender="fp@railtelindia.com",
                        recipients=[email],
                    )
                    msg.body = f"Your OTP for password reset is: {otp}"

                    msg.html = f"<p>Hello, <br /> Please use the OTP below to reset your password.</p> \n<strong>{otp}</strong> <p>--sent by RailTel</p><p>Regards, RailTel Silver Jubilee.</p>"
                    try:
                        mail.send(msg)
                        flash("OTP sent to your email address.", "success")
                        return redirect(url_for("verify_forgot_password"))
                    except Exception as e:
                        flash(f"Failed to send OTP. Error: {str(e)}", "danger")
        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")

    return render_template("forgot_password.html")


# Route to verify OTP for password reset
@app.route("/verify-forgot-password", methods=["GET", "POST"])
def verify_forgot_password():
    if request.method == "POST":
        user_otp = request.form.get("otp")

        if str(user_otp) == str(session.get("reset_otp")):
            flash("OTP verified successfully. Please reset your password.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template("verify_forgot_password.html")


# Route to reset password
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        password = request.form.get("newPass")
        confirm_password = request.form.get("confirmPass")

        if not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("reset_password"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))

        # Validate password strength
        if (
            len(password) < 12
            or not any(c.islower() for c in password)
            or not any(c.isupper() for c in password)
            or not any(c.isdigit() for c in password)
            or not any(c in "!@#$%^:;&*()-_+=" for c in password)
        ):
            flash(
                "Password must be at least 12 characters long and include uppercase, lowercase, numbers, and special characters.",
                "danger",
            )
            return redirect(url_for("reset_password"))

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Update the password in the database
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (hashed_password, session.get("reset_email")),
                    )
                    conn.commit()
                    flash("Password reset successful! You can now log in.", "success")
                    session.clear()
                    return redirect(url_for("login"))
        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")

    return render_template("reset_password.html")


@app.route("/index")
def index():
    if not session.get("logged_in"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    with connect_db() as conn:
        with conn.cursor() as cur:
            # Fetch YouTube videos
            cur.execute("SELECT title, link FROM youtube_videos")
            videos = cur.fetchall()

            # Fetch announcements
            cur.execute("SELECT announcement_text, link_or_file FROM announcements")
            announcements = cur.fetchall()

            # Fetch WebX meeting link
            cur.execute("SELECT link, description FROM meeting_link")
            meeting_link = cur.fetchone()
            meeting_link_url = meeting_link[0] if meeting_link else "#"
            meeting_link_description = meeting_link[1] if meeting_link else ""

            # Fetch Gallery Images
            cur.execute("SELECT image_path FROM gallery")
            gallery_images = [row[0] for row in cur.fetchall()]

    return render_template(
        "index.html",
        videos=videos,
        announcements=announcements,
        meeting_link=meeting_link_url,
        meeting_link_description=meeting_link_description,
        gallery_images=gallery_images,
    )


# Route to display the admin form (requires login)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        with connect_db() as conn:
            with conn.cursor() as cur:
                # Handle YouTube Video Form
                if "youtube_title" in request.form:
                    youtube_title = request.form["youtube_title"]
                    youtube_link = request.form["youtube_link"]
                    cur.execute("DELETE FROM youtube_videos")
                    cur.execute(
                        "INSERT INTO youtube_videos (title, link) VALUES (%s, %s)",
                        (youtube_title, youtube_link),
                    )
                    conn.commit()
                    flash("YouTube Video Added Successfully!", "success")

                # Handle Announcement Form
                elif "announcement_text" in request.form:
                    announcement_text = request.form.get("announcement_text")

                    announcement_link_or_file = request.form.get(
                        "announcement_link_or_file"
                    )

                    # Handle file upload
                    if "announcement_file" in request.files:
                        file = request.files.get("announcement_file")

                        if file:
                            upload_folder = "static/uploads"
                            if not os.path.exists(upload_folder):
                                os.makedirs(upload_folder)

                            file_path = os.path.join(
                                upload_folder, file.filename
                            ).replace("\\", "/")
                            file.save(file_path)

                            # Store the path relative to the static folder
                            announcement_link_or_file = f"uploads/{file.filename}"
                            print(
                                "announcement_link_or_file", announcement_link_or_file
                            )

                    cur.execute(
                        "INSERT INTO announcements (announcement_text, link_or_file) VALUES (%s, %s)",
                        (announcement_text, announcement_link_or_file),
                    )
                    conn.commit()
                    flash("Announcement Added Successfully!", "success")

                # Handle WebX Meeting Link Form
                elif "meeting_link" in request.form:
                    meeting_link = request.form["meeting_link"]
                    web_link_text = request.form["web_link_text"]

                    # Remove any existing entry and add the new one
                    cur.execute("DELETE FROM meeting_link")
                    cur.execute(
                        "INSERT INTO meeting_link (link, description) VALUES (%s, %s)",
                        (meeting_link, web_link_text),
                    )
                    conn.commit()
                    flash("WebX Meeting Link Added Successfully!", "success")

                # Handle Image Gallery Form
                elif "image_title" in request.form:
                    image_title = request.form["image_title"]

                    if "gallery_image" in request.files:
                        image_file = request.files["gallery_image"]
                        if image_file:
                            gallery_folder = "static/image/imageGallery"
                            if not os.path.exists(gallery_folder):
                                os.makedirs(gallery_folder)

                            # Save the image
                            image_path = os.path.join(
                                gallery_folder, image_file.filename
                            ).replace("\\", "/")
                            image_file.save(image_path)

                            # Store metadata in the database
                            cur.execute(
                                "INSERT INTO gallery (image_title, image_path) VALUES (%s, %s)",
                                (
                                    image_title,
                                    f"image/imageGallery/{image_file.filename}",
                                ),
                            )
                            conn.commit()
                            flash("Image Added to Gallery Successfully!", "success")
                        else:
                            flash("Failed to upload image.", "danger")

        return redirect(url_for("admin"))

    return render_template("admin.html")


# Route to log out
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)
