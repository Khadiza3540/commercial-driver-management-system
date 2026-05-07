import hashlib


def connect_db():
    import psycopg2

    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="951616",
        database="driver_system",
        port=5432
    )


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            license VARCHAR(100),
            phone VARCHAR(50),
            address TEXT,
            vehicle_no VARCHAR(100),
            dob DATE,
            is_authorized BOOLEAN DEFAULT FALSE
        )
    """)

    cur.execute("""
        ALTER TABLE drivers
        ADD COLUMN IF NOT EXISTS dob DATE
    """)

    cur.execute("""
        ALTER TABLE drivers
        ADD COLUMN IF NOT EXISTS email VARCHAR(255)
    """)

    cur.execute("""
        ALTER TABLE drivers
        ADD COLUMN IF NOT EXISTS profile_photo TEXT
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_sessions (
            id SERIAL PRIMARY KEY,
            driver_id INTEGER,
            driver_name VARCHAR(100),
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            session_id INTEGER,
            driver_id INTEGER,
            driver_name VARCHAR(100),
            alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id SERIAL PRIMARY KEY,
            driver_id INTEGER,
            start_location TEXT,
            destination TEXT,
            trip_date DATE DEFAULT CURRENT_DATE,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status VARCHAR(50) DEFAULT 'Active'
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def register_driver(name, username, password, email, license_no, phone, address, vehicle_no, dob):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drivers
        (name, username, password, email, license, phone, address, vehicle_no, dob, is_authorized)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, false)
        RETURNING id
    """, (
        name,
        username,
        hash_password(password),
        email,
        license_no,
        phone,
        address,
        vehicle_no,
        dob
    ))

    driver_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return driver_id


def authorize_driver(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE drivers SET is_authorized = TRUE WHERE id = %s",
        (driver_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def check_login(username, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, email
        FROM drivers
        WHERE username = %s 
        AND password = %s 
        AND is_authorized = TRUE
    """, (username, hash_password(password)))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


def start_session(driver_id, driver_name):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO monitoring_sessions (driver_id, driver_name)
        VALUES (%s, %s)
        RETURNING id
    """, (driver_id, driver_name))

    session_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return session_id


def end_session(session_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE monitoring_sessions
        SET end_time = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (session_id,))

    conn.commit()
    cur.close()
    conn.close()


def add_alert(session_id, driver_id, driver_name):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO alerts (session_id, driver_id, driver_name)
        VALUES (%s, %s, %s)
    """, (session_id, driver_id, driver_name))

    conn.commit()
    cur.close()
    conn.close()


def get_total_drivers():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM drivers")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()
    return count


def get_total_alerts():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM alerts")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()
    return count


def get_total_sessions():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM monitoring_sessions")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()
    return count


def add_driver(name, license_no, phone, address, vehicle_no, dob=None, email=None):
    return register_driver(
        name=name,
        username=phone,
        password=license_no,
        email=email,
        license_no=license_no,
        phone=phone,
        address=address,
        vehicle_no=vehicle_no,
        dob=dob
    )


def get_driver_by_license(license_no):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM drivers
        WHERE license = %s AND is_authorized = TRUE
    """, (license_no,))

    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


def reset_password_by_driver_id(driver_id, new_password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE drivers
        SET password = %s
        WHERE id = %s
    """, (hash_password(new_password), driver_id))

    conn.commit()
    cur.close()
    conn.close()


# ================= TRIPS =================

def start_trip(driver_id, start_location, destination):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trips (driver_id, start_location, destination, status)
        VALUES (%s, %s, %s, 'Active')
        RETURNING id
    """, (driver_id, start_location, destination))

    trip_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return trip_id


def end_trip(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE trips
        SET end_time = CURRENT_TIMESTAMP,
            status = 'Completed'
        WHERE driver_id = %s AND status = 'Active'
    """, (driver_id,))

    conn.commit()
    cur.close()
    conn.close()


def get_trips(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            start_location,
            destination,
            status,
            TO_CHAR(trip_date, 'DD-MM-YYYY'),
            TO_CHAR(start_time, 'HH12:MI AM'),
            COALESCE(TO_CHAR(end_time, 'HH12:MI AM'), '')
        FROM trips
        WHERE driver_id = %s
        ORDER BY id DESC
    """, (driver_id,))

    trips = cur.fetchall()

    cur.close()
    conn.close()

    return trips


# ================= ALERTS =================

def get_alerts(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            driver_name,
            TO_CHAR(alert_time, 'DD-MM-YYYY') AS alert_date,
            TO_CHAR(alert_time, 'HH12:MI AM') AS alert_time
        FROM alerts
        WHERE driver_id = %s
        ORDER BY id DESC
    """, (driver_id,))

    alerts = cur.fetchall()

    cur.close()
    conn.close()

    return alerts


# ================= PROFILE =================

def get_driver_profile(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        ALTER TABLE drivers
        ADD COLUMN IF NOT EXISTS profile_photo TEXT
    """)

    cur.execute("""
        SELECT name, license, phone, vehicle_no, address, dob, profile_photo
        FROM drivers
        WHERE id = %s
    """, (driver_id,))

    data = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return data


def update_driver_profile(driver_id, name, license_no, phone, vehicle_no, address, dob):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE drivers
        SET name = %s,
            license = %s,
            phone = %s,
            vehicle_no = %s,
            address = %s,
            dob = %s
        WHERE id = %s
    """, (name, license_no, phone, vehicle_no, address, dob, driver_id))

    conn.commit()
    cur.close()
    conn.close()


def update_driver_photo(driver_id, photo_path):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        ALTER TABLE drivers
        ADD COLUMN IF NOT EXISTS profile_photo TEXT
    """)

    cur.execute("""
        UPDATE drivers
        SET profile_photo = %s
        WHERE id = %s
    """, (photo_path, driver_id))

    conn.commit()
    cur.close()
    conn.close()


def get_monthly_profile_stats(driver_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM trips
        WHERE driver_id = %s
        AND EXTRACT(MONTH FROM start_time) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM start_time) = EXTRACT(YEAR FROM CURRENT_DATE)
    """, (driver_id,))
    total_trips = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE driver_id = %s
        AND EXTRACT(MONTH FROM alert_time) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM alert_time) = EXTRACT(YEAR FROM CURRENT_DATE)
    """, (driver_id,))
    total_alerts = cursor.fetchone()[0]

    safety_score = max(0, 100 - (total_alerts * 5))

    cursor.close()
    conn.close()

    return total_trips, total_alerts, safety_score


# ================= DASHBOARD =================

def get_dashboard_analytics(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM trips
        WHERE driver_id = %s
        AND trip_date = CURRENT_DATE
    """, (driver_id,))
    today_trips = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE driver_id = %s
        AND DATE(alert_time) = CURRENT_DATE
    """, (driver_id,))
    today_alerts = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE driver_id = %s
        AND alert_time >= CURRENT_DATE - INTERVAL '7 days'
    """, (driver_id,))
    last_7_alerts = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM trips
        WHERE driver_id = %s
        AND EXTRACT(MONTH FROM start_time) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM start_time) = EXTRACT(YEAR FROM CURRENT_DATE)
    """, (driver_id,))
    monthly_trips = cur.fetchone()[0]

    cur.execute("""
        SELECT start_location, destination, COUNT(*)
        FROM trips
        WHERE driver_id = %s
        GROUP BY start_location, destination
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """, (driver_id,))
    route = cur.fetchone()

    if route and route[0] and route[1]:
        top_route = f"{route[0]} → {route[1]}"
    else:
        top_route = "No route yet"

    safety_score = max(0, 100 - (today_alerts * 5))

    cur.close()
    conn.close()

    return today_trips, today_alerts, last_7_alerts, monthly_trips, top_route, safety_score


create_tables()