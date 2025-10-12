from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change in production

# ---------------- DB Config ----------------
db_config = {}
with open("database.db", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        db_config[key] = value

# MySQL configuration
app.config['MYSQL_HOST'] = db_config['host']
app.config['MYSQL_USER'] = db_config['user']
app.config['MYSQL_PASSWORD'] = db_config['password']
app.config['MYSQL_DB'] = db_config['database']

mysql = MySQL(app)

# ---------------- Admin Credentials ----------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# ---------------- Visitor Pages ----------------

@app.route('/')
def index():
    # later fetch from properties table, for now static
    properties = [
        {'image': '/static/images/property1.jpg', 'title': 'Luxury Villa'},
        {'image': '/static/images/property2.jpg', 'title': 'City Apartment'},
        {'image': '/static/images/property3.jpg', 'title': 'Beach House'},
        {'image': '/static/images/property4.jpg', 'title': 'Mountain Cabin'}
    ]
    return render_template('index.html', properties=properties, is_admin_page=False)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO messages (name, email, phone, message, created_at)
        VALUES (%s, %s, %s, %s, %s)
    ''', (name, email, phone, message, created_at))
    mysql.connection.commit()
    cur.close()

    return render_template('thankyou.html', name=name, is_admin_page=False)

# ---------------- Admin Panel ----------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('admin_login.html', is_admin_page=True)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, phone, message, created_at,remarks 
        FROM messages ORDER BY created_at DESC
    """)
    messages = cur.fetchall()
    cur.close()

    return render_template('admin_dashboard.html', messages=messages, is_admin_page=True)

@app.route('/admin/delete/<int:message_id>')
def admin_delete(message_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/remark/<int:message_id>', methods=['POST'])
def admin_remark(message_id):
    """Add/update admin remarks for a visitor message"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    remark = request.form.get("remark")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE messages SET remarks = %s WHERE id = %s", (remark, message_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    properties = [
        {
            'title': 'Luxury Villa',
            'images': [
                '/static/images/category/villa1.jpg',
                '/static/images/category/villa2.jpg',
                '/static/images/category/villa3.jpg',
                '/static/images/category/villa4.jpg'
            ],
            'description': 'A luxury villa with 4 bedrooms, swimming pool, and sea view. Spacious living and modern design.'
        },
        {
            'title': 'City Apartment',
            'images': [
                '/static/images/category/apartment1.jpg',
                '/static/images/category/apartment2.jpg',
                '/static/images/category/apartment3.jpg',
                '/static/images/category/apartment4.jpg'
            ],
            'description': 'Modern city apartment with 3 bedrooms, close to schools and shopping centers.'
        },
        {
            'title': 'Beach House',
            'images': [
                '/static/images/category/beach1.jpg',
                '/static/images/category/beach2.jpg',
                '/static/images/category/beach3.jpg',
                '/static/images/category/beach4.jpg'
            ],
            'description': 'Beautiful beach house perfect for weekend getaways. Enjoy sea breeze and sunrise views.'
        },
        {
            'title': 'Mountain Cabin',
            'images': [
                '/static/static/images/category/cabin1.jpg',
                '/static/static/images/category/cabin2.jpg',
                '/static/static/images/category/cabin3.jpg',
                '/static/static/images/category/cabin4.jpg'
            ],
            'description': 'Cozy mountain cabin surrounded by nature. Ideal for relaxation and hiking lovers.'
        }
    ]

    if 0 <= property_id < len(properties):
        return render_template('property_detail.html', property=properties[property_id], is_admin_page=False)
    else:
        return redirect(url_for('index'))



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True)