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

    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS dob DATE")
    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS email VARCHAR(255)")
    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS profile_photo TEXT")
    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'driver'")
    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Active'")

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

    cur.execute("ALTER TABLE alerts ADD COLUMN IF NOT EXISTS severity VARCHAR(50) DEFAULT 'Drowsiness'")

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS toll_payments (
            id SERIAL PRIMARY KEY,
            month VARCHAR(50) NOT NULL,
            toll_location VARCHAR(150) NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            payment_status VARCHAR(20) DEFAULT 'Unpaid',
            payment_method VARCHAR(50),
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def register_driver(name, username, password, email, license_no, phone, address, vehicle_no, dob):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO drivers
        (name, username, password, email, license, phone, address, vehicle_no, dob, is_authorized, role, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, false, 'driver', 'Active')
        RETURNING id
    """, (
        name, username, hash_password(password), email,
        license_no, phone, address, vehicle_no, dob
    ))

    driver_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
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
        AND status = 'Active'
    """, (username, hash_password(password)))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


def check_login_with_role(username, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, email, role
        FROM drivers
        WHERE username = %s
        AND password = %s
        AND is_authorized = TRUE
        AND status = 'Active'
    """, (username, hash_password(password)))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result



def is_waiting_for_approval(username):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT is_authorized
        FROM drivers
        WHERE username = %s
    """, (username,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return result[0] is False

    return False

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
        INSERT INTO alerts (session_id, driver_id, driver_name, severity)
        VALUES (%s, %s, %s, 'Drowsiness')
    """, (session_id, driver_id, driver_name))

    conn.commit()
    cur.close()
    conn.close()


def get_total_drivers():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM drivers WHERE role = 'driver'")
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
        WHERE license = %s
        AND is_authorized = TRUE
        AND status = 'Active'
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
        WHERE driver_id = %s
        AND status = 'Active'
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
            TO_CHAR(alert_time, 'DD-MM-YYYY'),
            TO_CHAR(alert_time, 'HH12:MI AM')
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

    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS profile_photo TEXT")

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

    cur.execute("ALTER TABLE drivers ADD COLUMN IF NOT EXISTS profile_photo TEXT")

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
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM trips
        WHERE driver_id = %s
        AND EXTRACT(MONTH FROM start_time) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM start_time) = EXTRACT(YEAR FROM CURRENT_DATE)
    """, (driver_id,))
    total_trips = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE driver_id = %s
        AND EXTRACT(MONTH FROM alert_time) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM alert_time) = EXTRACT(YEAR FROM CURRENT_DATE)
    """, (driver_id,))
    total_alerts = cur.fetchone()[0]

    safety_score = max(0, 100 - (total_alerts * 5))

    cur.close()
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


# ================= ADMIN / MANAGEMENT =================

def update_driver_status(driver_id, status):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE drivers
        SET status = %s
        WHERE id = %s
    """, (status, driver_id))

    conn.commit()
    cur.close()
    conn.close()


def enable_driver_admin(driver_id):
    update_driver_status(driver_id, "Active")


def disable_driver_admin(driver_id):
    update_driver_status(driver_id, "Disabled")


def auto_disable_low_score_drivers():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE drivers d
        SET status = 'Disabled'
        WHERE d.role = 'driver'
        AND d.status = 'Active'
        AND (
            100 - (
                SELECT COUNT(*)
                FROM alerts a
                WHERE a.driver_id = d.id
            ) * 5
        ) < 30
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_admin_dashboard_stats():
    auto_disable_low_score_drivers()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM drivers WHERE role = 'driver'")
    total_drivers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM drivers WHERE status = 'Active' AND role = 'driver'")
    active_drivers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM trips WHERE status = 'Active'")
    running_trips = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts WHERE DATE(alert_time) = CURRENT_DATE")
    today_alerts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM monitoring_sessions WHERE end_time IS NULL")
    online_monitoring = cur.fetchone()[0]

    safety_score = max(0, 100 - (today_alerts * 5))

    cur.close()
    conn.close()

    return total_drivers, active_drivers, running_trips, today_alerts, safety_score, online_monitoring


def get_all_drivers_admin():
    auto_disable_low_score_drivers()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            d.id,
            d.name,
            d.username,
            d.email,
            d.license,
            d.phone,
            d.vehicle_no,
            d.status,
            d.is_authorized,
            COALESCE(COUNT(DISTINCT t.id), 0) AS total_trips,
            COALESCE(COUNT(DISTINCT a.id), 0) AS total_alerts
        FROM drivers d
        LEFT JOIN trips t ON d.id = t.driver_id
        LEFT JOIN alerts a ON d.id = a.driver_id
        WHERE d.role = 'driver'
        GROUP BY d.id
        ORDER BY d.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_driver_report_by_name(driver_name):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            d.id,
            d.name,
            d.username,
            d.email,
            d.license,
            d.phone,
            d.vehicle_no,
            d.status,
            d.is_authorized,
            COALESCE(COUNT(DISTINCT t.id), 0) AS total_trips,
            COALESCE(COUNT(DISTINCT a.id), 0) AS total_alerts
        FROM drivers d
        LEFT JOIN trips t ON d.id = t.driver_id
        LEFT JOIN alerts a ON d.id = a.driver_id
        WHERE d.role = 'driver'
        AND d.name = %s
        GROUP BY d.id
        LIMIT 1
    """, (driver_name,))

    data = cur.fetchone()

    cur.close()
    conn.close()

    return data


def search_drivers_admin(keyword):
    conn = connect_db()
    cur = conn.cursor()

    search_text = f"%{keyword}%"

    cur.execute("""
        SELECT 
            id, name, username, email, license, phone, vehicle_no, status, is_authorized
        FROM drivers
        WHERE role = 'driver'
        AND (
            name ILIKE %s OR
            username ILIKE %s OR
            email ILIKE %s OR
            license ILIKE %s OR
            phone ILIKE %s OR
            vehicle_no ILIKE %s
        )
        ORDER BY id DESC
    """, (
        search_text, search_text, search_text,
        search_text, search_text, search_text
    ))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def delete_driver_admin(driver_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM alerts WHERE driver_id = %s", (driver_id,))
    cur.execute("DELETE FROM trips WHERE driver_id = %s", (driver_id,))
    cur.execute("DELETE FROM monitoring_sessions WHERE driver_id = %s", (driver_id,))
    cur.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))

    conn.commit()
    cur.close()
    conn.close()


def get_all_trips_admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            t.id,
            COALESCE(d.name, 'Unknown Driver'),
            t.start_location,
            t.destination,
            TO_CHAR(t.trip_date, 'DD-MM-YYYY'),
            TO_CHAR(t.start_time, 'HH12:MI AM'),
            COALESCE(TO_CHAR(t.end_time, 'HH12:MI AM'), ''),
            t.status
        FROM trips t
        LEFT JOIN drivers d ON t.driver_id = d.id
        ORDER BY t.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_all_alerts_admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            a.id,
            a.driver_name,
            COALESCE(a.severity, 'Drowsiness'),
            TO_CHAR(a.alert_time, 'DD-MM-YYYY'),
            TO_CHAR(a.alert_time, 'HH12:MI AM'),
            a.session_id
        FROM alerts a
        ORDER BY a.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_monitoring_sessions_admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            id,
            driver_name,
            TO_CHAR(start_time, 'DD-MM-YYYY'),
            TO_CHAR(start_time, 'HH12:MI AM'),
            COALESCE(TO_CHAR(end_time, 'HH12:MI AM'), 'Running'),
            CASE 
                WHEN end_time IS NULL THEN 'Online'
                ELSE 'Offline'
            END AS status
        FROM monitoring_sessions
        ORDER BY id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_high_risk_drivers_admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            d.id,
            d.name,
            d.license,
            d.phone,
            COUNT(a.id) AS total_alerts
        FROM drivers d
        LEFT JOIN alerts a ON d.id = a.driver_id
        WHERE d.role = 'driver'
        GROUP BY d.id
        HAVING COUNT(a.id) >= 3
        ORDER BY total_alerts DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_admin_report_summary():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM trips")
    total_trips = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM trips WHERE status = 'Completed'")
    completed_trips = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM trips WHERE status = 'Active'")
    active_trips = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts WHERE DATE(alert_time) = CURRENT_DATE")
    today_alerts = cur.fetchone()[0]

    safety_score = max(0, 100 - (today_alerts * 5))

    cur.close()
    conn.close()

    return total_trips, completed_trips, active_trips, total_alerts, today_alerts, safety_score


# ================= TOLL PAYMENTS =================

def seed_demo_toll_payments():
    conn = connect_db()
    cur = conn.cursor()

    demo_records = [
        ("January", "Padma Bridge Toll Plaza", 50000, "Paid", "Card Payment"),
        ("February", "Meghna Bridge Toll Plaza", 35000, "Unpaid", None),
        ("March", "Jamuna Bridge Toll Plaza", 42000, "Paid", "Bkash"),
        ("April", "Dhaka Expressway Toll", 50000, "Unpaid", None),
    ]

    for month, location, amount, status, method in demo_records:
        cur.execute("""
            INSERT INTO toll_payments
            (month, toll_location, amount, payment_status, payment_method)
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM toll_payments
                WHERE month = %s AND toll_location = %s
            )
        """, (month, location, amount, status, method, month, location))

    conn.commit()
    cur.close()
    conn.close()


def get_all_toll_payments_admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            month,
            toll_location,
            amount,
            payment_status,
            COALESCE(payment_method, '')
        FROM toll_payments
        ORDER BY id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def mark_toll_payment_paid(payment_id, payment_method):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE toll_payments
        SET payment_status = 'Paid',
            payment_method = %s,
            paid_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (payment_method, payment_id))

    conn.commit()
    cur.close()
    conn.close()


def create_admin_user():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO drivers
        (name, username, password, email, license, phone, address, vehicle_no, dob, is_authorized, role, status)
        VALUES 
        ('System Admin', 'admin', %s, 'admin@cdms.com', 'ADMIN-001', '0000000000', 'CDMS Office', 'ADMIN', NULL, TRUE, 'admin', 'Active')
        ON CONFLICT (username) DO NOTHING
    """, (hash_password("admin123"),))

    conn.commit()
    cur.close()
    conn.close()


create_tables()
create_admin_user()
