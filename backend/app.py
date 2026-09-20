from flask import Flask, jsonify
import os
import mysql.connector

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'changeme')
DB_NAME = os.getenv('DB_NAME', 'appdb')


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api')
def index():
    """Read data from MySQL."""

    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cur = conn.cursor()

    # Read the current MySQL server time
    cur.execute("SELECT NOW()")
    server_time = cur.fetchone()[0]

    # Read the current page view count
    cur.execute("SELECT count FROM page_views WHERE id = 1")
    page_views = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify(
        message="Hello from MySQL via Flask! v1.0.2 ",
        server_time=str(server_time),
        page_views=page_views
    )


@app.post('/api/visit')
def visit():
    """Write data to MySQL by increasing the page view counter."""

    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cur = conn.cursor()

    # Increase the counter in MySQL
    cur.execute(
        "UPDATE page_views SET count = count + 1 WHERE id = 1"
    )

    conn.commit()

    # Read the new value
    cur.execute("SELECT count FROM page_views WHERE id = 1")
    page_views = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify(page_views=page_views)


if __name__ == '__main__':
    # Dev-only fallback
    app.run(host='0.0.0.0', port=8000, debug=True)