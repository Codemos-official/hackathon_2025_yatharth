from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)
bcrypt = Bcrypt(app)
Session(app)

# ---------------- LANDING ----------------
@app.route('/')
def landing():
    return render_template('landing.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(
            request.form['password']
        ).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (name,email,password)
        )
        mysql.connection.commit()
        return redirect('/login')
    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id,password FROM users WHERE email=%s",(email,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect('/movies')

    return render_template('login.html')

# ---------------- MOVIES ROUTE ----------------
@app.route('/movies')
def movies():
    # 1. Get Selected Date from URL (default to Today)
    selected_date_str = request.args.get('date')
    if not selected_date_str:
        selected_date = datetime.now().date()
        selected_date_str = selected_date.strftime('%Y-%m-%d')
    else:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    # 2. Generate Next 4 Days for the Tabs
    date_tabs = []
    today = datetime.now().date()
    for i in range(4):
        date_obj = today + timedelta(days=i)
        date_tabs.append({
            'display': date_obj.strftime('%a, %d %b'), 
            'value': date_obj.strftime('%Y-%m-%d'),    
            'active': (date_obj == selected_date)      
        })

    # 3. Fetch Movies
    cur = mysql.connection.cursor()
    # Note: 'movies.genre' hata diya hai safety ke liye
    cur.execute("""
        SELECT shows.id, movies.title, movies.poster, shows.price, shows.show_time
        FROM shows
        JOIN movies ON shows.movie_id = movies.id
        WHERE DATE(shows.show_time) = %s
        ORDER BY shows.show_time ASC
    """, (selected_date_str,))
    
    raw_data = cur.fetchall()
    
    # 4. Process Data
    movies_data = []
    for m in raw_data:
        dt_obj = m[4] 
        if isinstance(dt_obj, str): 
            dt_obj = datetime.strptime(dt_obj, '%Y-%m-%d %H:%M:%S')
            
        formatted_time = dt_obj.strftime("%I:%M %p") 

        movies_data.append({
            'show_id': m[0],
            'title': m[1],
            'poster': m[2],
            'genre': 'Blockbuster', 
            'price': m[3],
            'time': formatted_time
        })

    return render_template('movies.html', movies=movies_data, date_tabs=date_tabs)

# ---------------- SEATS & LOCKING (UPDATED WITH SMART LOGIC) ----------------
@app.route('/lock_seats', methods=['POST'])
def lock_seats():
    data = request.json
    show_id = data['show_id']
    seats = data['seats']

    cur = mysql.connection.cursor()

    for seat in seats:
        cur.execute("""
            UPDATE seats
            SET status='locked', lock_time=NOW()
            WHERE show_id=%s AND seat_number=%s AND status='available'
        """, (show_id, seat))

        if cur.rowcount == 0:
            return jsonify({"status":"failed"})

    mysql.connection.commit()
    session['locked_seats'] = seats
    session['show_id'] = show_id

    return jsonify({"status":"ok"})

# 🔥 THIS IS THE UPDATED SMART ROUTE 🔥
@app.route('/seats/<int:show_id>')
def seats(show_id):
    cur = mysql.connection.cursor()

    # 1. PEHLE CHECK KARO: Kya is show ke liye seats hain?
    cur.execute("SELECT count(*) FROM seats WHERE show_id=%s", (show_id,))
    count = cur.fetchone()[0]

    # 2. AGAR SEATS NAHI HAIN, TOH ABHI BANA DO (Auto-Generate)
    if count == 0:
        rows = ['A', 'B', 'C', 'D', 'E'] # A-B VIP, C-E Gold
        seats_per_row = 8
        
        for r in rows:
            for n in range(1, seats_per_row + 1):
                seat_num = f"{r}{n}"
                seat_type = 'VIP' if r in ['A', 'B'] else 'Standard'
                price = 500 if seat_type == 'VIP' else 250
                
                cur.execute("""
                    INSERT INTO seats (show_id, seat_number, status, seat_type, price)
                    VALUES (%s, %s, 'available', %s, %s)
                """, (show_id, seat_num, seat_type, price))
        
        mysql.connection.commit()
        print(f"✅ Seats auto-generated for Show ID: {show_id}")

    # 3. AB SEATS FETCH KARO
    cur.execute(
        "SELECT seat_number, status FROM seats WHERE show_id=%s",
        (show_id,)
    )
    seats = cur.fetchall()
    return render_template('seats.html', seats=seats, show_id=show_id)

# ---------------- OTP & CONFIRMATION ----------------
@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if 'locked_seats' not in session or 'show_id' not in session:
        return redirect('/movies')

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if entered_otp == str(session.get('otp')):
            return redirect('/confirm')
        else:
            pass 

    show_id = session['show_id']
    seats = session['locked_seats']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT movies.title, shows.show_time, shows.price
        FROM shows
        JOIN movies ON shows.movie_id = movies.id
        WHERE shows.id = %s
    """, (show_id,))
    
    data = cur.fetchone()
    
    if data:
        movie_title = data[0]
        show_time = data[1]
        price_per_seat = data[2]
        total_price = len(seats) * price_per_seat
    else:
        movie_title = "Unknown Movie"
        show_time = ""
        total_price = 0

    if request.method == 'GET' or 'otp' not in session:
        new_otp = str(random.randint(100000, 999999))
        session['otp'] = new_otp
        print(f"OTP: {new_otp}")

    return render_template('otp.html', 
                           movie_title=movie_title,
                           show_time=show_time,
                           seat_count=len(seats),
                           seats_str=", ".join(seats),
                           total_price=total_price,
                           error="Invalid OTP" if request.method == 'POST' else None)

@app.route('/confirm')
def confirm():
    seats = ",".join(session['locked_seats'])
    show_id = session['show_id']
    user_id = session['user_id']
    total = len(session['locked_seats']) * 200 

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO bookings (user_id, show_id, seats, total_price)
        VALUES (%s,%s,%s,%s)
    """, (user_id, show_id, seats, total))

    cur.execute("""
        UPDATE seats
        SET status='booked'
        WHERE show_id=%s AND seat_number IN %s
    """, (show_id, tuple(session['locked_seats'])))

    mysql.connection.commit()
    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    
    # Updated Query for accuracy
    cur.execute("""
        SELECT movies.title, bookings.created_at, movies.title, shows.show_time, bookings.seats
        FROM bookings
        JOIN shows ON bookings.show_id = shows.id
        JOIN movies ON shows.movie_id = movies.id
        WHERE bookings.user_id = %s
        ORDER BY bookings.created_at DESC
    """, (session['user_id'],))

    bookings = cur.fetchall()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/release-seats', methods=['POST'])
def release_seats():
    show_id = session.get('show_id')
    seats = session.get('locked_seats')

    if show_id and seats:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE seats
            SET status='available'
            WHERE show_id=%s AND seat_number IN %s
        """, (show_id, tuple(seats)))
        mysql.connection.commit()

    session.pop('locked_seats', None)
    session.pop('show_id', None)
    session.pop('otp', None)

    return jsonify({"status": "released"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')




@app.route('/fix-db')
def fix_db():
    cur = mysql.connection.cursor()
    try:
        cur.execute("ALTER TABLE seats ADD COLUMN seat_type VARCHAR(20) DEFAULT 'Standard'")
        cur.execute("ALTER TABLE seats ADD COLUMN price INT DEFAULT 250")
        mysql.connection.commit()
        return "Database Fixed! Columns added successfully."
    except Exception as e:
        return f"Error: {e}"

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)