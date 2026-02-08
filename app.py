#
#
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# import sqlite3
# from datetime import datetime
# import random
# import string
#
#
# class Flask(Flask):
#     pass
#
#
# app = Flask(__name__)
# app.secret_key = "super_secret_key_change_me_2025"  # change this in production
#
# def get_db():
#     conn = sqlite3.connect("tips.db")
#     conn.row_factory = sqlite3.Row
#     return conn
#
# def init_db():
#     with get_db() as conn:
#         conn.execute('''
#         CREATE TABLE IF NOT EXISTS tips (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             tip_code TEXT UNIQUE NOT NULL,
#             access_code TEXT NOT NULL,
#             message TEXT NOT NULL,
#             category TEXT,
#             location TEXT,
#             created_at TEXT NOT NULL,
#             status TEXT DEFAULT 'New'
#         )
#         ''')
#         conn.execute('''
#         CREATE TABLE IF NOT EXISTS suspicious_places (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             description TEXT,
#             location TEXT,
#             added_at TEXT NOT NULL,
#             is_active INTEGER DEFAULT 1
#         )
#         ''')
#         conn.commit()
#
# @app.before_request
# def setup_db():
#     init_db()
#
# def generate_code(length=8):
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
#
# # ────────────────────────────────────────────────
# # Routes (only /add-place is changed)
# # ────────────────────────────────────────────────
#
# @app.route('/')
# def home():
#     return render_template('login.html')
#
# @app.route('/login', methods=['POST'])
# def police_login():
#     password = request.form.get('password')
#     if password == '123':
#         session['police'] = True
#         flash('Login successful', 'success')
#         return redirect(url_for('admin'))
#     flash('Wrong password', 'error')
#     return redirect(url_for('home'))
#
# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out', 'info')
#     return redirect(url_for('home'))
#
# @app.route('/anonymous', methods=['GET', 'POST'])
# def anonymous_tip():
#     if request.method == 'POST':
#         message = request.form.get('message', '').strip()
#         category = request.form.get('category')
#         location = request.form.get('location', 'Not shared')
#
#         if not message:
#             flash('Please enter a message', 'error')
#             return redirect(url_for('anonymous_tip'))
#
#         tip_code = 'T' + generate_code(7)
#         access_code = generate_code(10)
#
#         try:
#             with get_db() as conn:
#                 conn.execute('''
#                     INSERT INTO tips
#                     (tip_code, access_code, message, category, location, created_at)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 ''', (
#                     tip_code,
#                     access_code,
#                     message,
#                     category,
#                     location,
#                     datetime.now().strftime("%Y-%m-%d %H:%M")
#                 ))
#                 conn.commit()
#
#             flash('Tip submitted successfully!', 'success')
#             flash('Your Tip Code: {tip_code}', 'info')          # ← fixed formatting
#             flash('Your Access Code: {access_code} (save this!)', 'warning')
#
#         except Exception as e:
#             flash('Error saving tip: {str(e)}', 'error')
#
#         return redirect(url_for('anonymous_tip'))
#
#     return render_template('index.html')
#
# @app.route('/view-tips')
# def view_tips():
#     with get_db() as conn:
#         tips = conn.execute('''
#             SELECT * FROM tips
#             ORDER BY created_at DESC
#         ''').fetchall()
#     return render_template('view_tips.html', tips=tips)
#
# @app.route('/suspicious-places')
# def suspicious_places():
#     with get_db() as conn:
#         places = conn.execute('''
#             SELECT * FROM suspicious_places
#             WHERE is_active = 1
#             ORDER BY added_at DESC
#         ''').fetchall()
#     return render_template('suspicious_places.html', places=places)
#
# # ─── ONLY THIS ROUTE WAS EDITED ───────────────────────────────────────────────
#
# @app.route('/add-place', methods=['GET', 'POST'])
# def add_place():
#     if 'police' not in session:
#         flash('Please login as police first', 'error')
#         return redirect(url_for('home'))
#
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         description = request.form.get('description', '').strip()
#         location = request.form.get('location', '').strip()
#
#         if not name:
#             flash('Name is required', 'error')
#             return redirect(url_for('add_place'))
#
#         if len(name) > 200:
#             flash('Name is too long (max 200 characters)', 'error')
#             return redirect(url_for('add_place'))
#
#         added_at = datetime.now().strftime("%Y-%m-%d %H:%M")
#
#         try:
#             with get_db() as conn:
#                 conn.execute('''
#                     INSERT INTO suspicious_places
#                     (name, description, location, added_at)
#                     VALUES (?, ?, ?, ?)
#                 ''', (name, description, location, added_at))
#                 conn.commit()
#
#             flash('Suspicious place added successfully', 'success')
#             return redirect(url_for('suspicious_places'))   # ← changed: go to list instead of form
#
#         except Exception as e:
#             flash('Error adding place: {str(e)}', 'error')
#             return redirect(url_for('add_place'))
#
#     return render_template('policehome.html')
#
# # ───────────────────────────────────────────────────────────────────────────────
#
# @app.route('/admin')
# def admin():
#     if 'police' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('home'))
#
#     with get_db() as conn:
#         tips = conn.execute('''
#             SELECT * FROM tips
#             ORDER BY created_at DESC
#         ''').fetchall()
#
#     return render_template('admin.html', tips=tips)
#
# @app.route('/status', methods=['GET', 'POST'])
# def status():
#     tip = None
#     if request.method == 'POST':
#         tip_code = request.form.get('tip_code', '').strip()
#         access_code = request.form.get('access_code', '').strip()
#
#         with get_db() as conn:
#             tip = conn.execute('''
#                 SELECT * FROM tips
#                 WHERE tip_code = ? AND access_code = ?
#             ''', (tip_code, access_code)).fetchone()
#
#         if not tip:
#             flash('Invalid Tip Code or Access Code', 'error')
#
#     return render_template('status.html', tip=tip)
#
# @app.route("/help", methods=["GET", "POST"])
# def help():
#     if request.method == "POST":
#         message = request.form.get("message", "").strip()
#         location = request.form.get("location", "Not provided").strip()
#
#         if not message:
#             flash("Please describe what is happening", "error")
#             return redirect(url_for("help"))
#
#         help_code = "HELP-" + generate_code(6)
#         access_code = generate_code(10)
#
#         with get_db() as conn:
#             conn.execute("""
#                 INSERT INTO tips
#                 (tip_code, access_code, message, location, category, created_at, status)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 help_code,
#                 access_code,
#                 message,
#                 location,
#                 "HELP_REQUEST",
#                 datetime.now().strftime("%Y-%m-%d %H:%M"),
#                 "Urgent"
#             ))
#             conn.commit()
#
#         flash("Help request sent successfully!", "success")
#         flash("Help Code: {help_code}", "info")                     # ← fixed formatting
#         flash("Access Code: {access_code} – save these to check status", "warning")
#
#         return redirect(url_for("help"))
#
#     return render_template("help.html")
#
# @app.route("/anohome")
# def anohome():
#     return render_template("anohome.html")
#
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me_2025"  # change in production

# ────────────────────────────────────────────────
# Database Setup
# ────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("tips.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tip_code TEXT UNIQUE NOT NULL,
            access_code TEXT NOT NULL,
            message TEXT NOT NULL,
            category TEXT,
            location TEXT,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'New'
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS suspicious_places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            added_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
        ''')
        conn.commit()

@app.before_request
def setup_db():
    init_db()

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────

# Home / Police Login
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def police_login():
    password = request.form.get('password')
    if password == '123':
        session['police'] = True
        flash('Login successful', 'success')
        return redirect(url_for('admin'))
    flash('Wrong password', 'error')
    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# Anonymous tip submission
@app.route('/anonymous', methods=['GET', 'POST'])
def anonymous_tip():
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        category = request.form.get('category')
        location = request.form.get("location", "Not provided").strip()

        if not message:
            flash('Please enter a message', 'error')
            return redirect(url_for('anonymous_tip'))

        tip_code = 'T' + generate_code(7)
        access_code = generate_code(10)

        try:
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO tips 
                    (tip_code, access_code, message, category, location, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    tip_code,
                    access_code,
                    message,
                    category,
                    location,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ))
                conn.commit()

            flash('Tip submitted successfully!', 'success')
            flash('Your Tip Code: {tip_code}', 'info')
            flash('Your Access Code: {access_code} (save this!)', 'warning')
            return redirect(url_for('anohome'))

        except Exception as e:
            flash('Error saving tip: {str(e)}', 'error')
            return redirect(url_for('anonymous_tip'))

    return render_template('index.html')

# Anonymous Home Dashboard
@app.route("/anohome")
def anohome():
    return render_template("anohome.html")

# View tips
@app.route('/view-tips')
def view_tips():
    with get_db() as conn:
        tips = conn.execute('''
            SELECT * FROM tips 
            ORDER BY created_at DESC
        ''').fetchall()
    return render_template('view_tips.html', tips=tips)

# Suspicious Places
@app.route('/suspicious-places')
def suspicious_places():
    with get_db() as conn:
        places = conn.execute('''
            SELECT * FROM suspicious_places 
            WHERE is_active = 1 
            ORDER BY added_at DESC
        ''').fetchall()
    return render_template('suspicious_places.html', places=places)

# Add Suspicious Place (Police Only)
@app.route('/add-place', methods=['GET', 'POST'])
def add_place():
    if 'police' not in session:
        flash('Please login as police first', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()

        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('add_place'))

        if len(name) > 200:
            flash('Name is too long (max 200 characters)', 'error')
            return redirect(url_for('add_place'))

        added_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO suspicious_places 
                    (name, description, location, added_at)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, location, added_at))
                conn.commit()

            flash('Suspicious place added successfully', 'success')
            return redirect(url_for('suspicious_places'))

        except Exception as e:
            flash('Error adding place: {str(e)}', 'error')
            return redirect(url_for('add_place'))

    return render_template('policehome.html')

# Admin panel
@app.route('/admin')
def admin():
    if 'police' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('home'))

    with get_db() as conn:
        tips = conn.execute('''
            SELECT * FROM tips 
            ORDER BY created_at DESC
        ''').fetchall()

    return render_template('admin.html', tips=tips)

# Tip status check
@app.route('/status', methods=['GET', 'POST'])
def status():
    tip = None
    if request.method == 'POST':
        tip_code = request.form.get('tip_code', '').strip()
        access_code = request.form.get('access_code', '').strip()

        with get_db() as conn:
            tip = conn.execute('''
                SELECT * FROM tips 
                WHERE tip_code = ? AND access_code = ?
            ''', (tip_code, access_code)).fetchone()

        if not tip:
            flash('Invalid Tip Code or Access Code', 'error')

    return render_template('status.html', tip=tip)

# Emergency Help
@app.route("/help", methods=["GET", "POST"])
def help():
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        location = request.form.get("location", "Not provided").strip()

        if not message:
            flash("Please describe what is happening", "error")
            return redirect(url_for("help"))

        help_code = "HELP-" + generate_code(6)
        access_code = generate_code(10)

        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO tips 
                    (tip_code, access_code, message, location, category, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    help_code,
                    access_code,
                    message,
                    location,
                    "HELP_REQUEST",
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Urgent"
                ))
                conn.commit()

            flash("Help request sent successfully!", "success")
            flash("Help Code: {help_code}", "info")
            flash("Access Code: {access_code} – save these to check status", "warning")

        except Exception as e:
            flash("Error saving help request: {str(e)}", "error")

        return redirect(url_for("help"))

    return render_template("help.html")

@app.route('/help_view')
def help_view():
    with get_db() as conn:
        tips = conn.execute('''
            SELECT * FROM tips 
            ORDER BY created_at DESC
        ''').fetchall()
    return render_template('help_view.html', tips=tips)

# Run App
if __name__ == '__main__':
    app.run(debug=True)
