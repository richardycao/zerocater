from flask import Flask, request, jsonify
import os
import psycopg2
import datetime as dt
import sys

"""
This is the api for registering users.
"""

app = Flask(__name__)

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=5432,
            database='zerocater',
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
        )
    except Exception as e:
        print('failed to connect to postgres.', e)
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("create table if not exists users (username text PRIMARY KEY, token text, idx integer, preferred_floor integer)")
        conn.commit()
        cur.close()

        return conn
    except Exception as e:
        cur.close()
        conn.rollback()
        print('failed to create table.', e)
        sys.exit(1)

conn = connect_db()

# health
@app.route("/", methods=['GET'])
def health():
    return jsonify({"message": "healthy"})

# get user
@app.route("/user", methods=['GET'])
def get_user():
    data = request.get_json()
    username = data.get('username')

    cur = conn.cursor()
    try:
        cur.execute(f"select * from users where username like '{username}'")
        rows = cur.fetchall()
        cur.close()
        return jsonify({"message": str(rows)})
    except:
        cur.close()
        conn.rollback()
        return jsonify({"error": "failed to get user"})

# create user
@app.route("/user", methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    token = data.get('token')
    preferred_floor = data.get('preferred_floor')

    if username and token:
        cur = conn.cursor()
        try:
            cur.execute(f"select count(*) from users")
            rows = cur.fetchall()
            num_rows = rows[0][0]

            cur.execute(f"insert into users values ('{username}','{token}','{num_rows}','{preferred_floor}') on conflict(username) do update set token = '{token}', preferred_floor = {preferred_floor}")
            conn.commit()
            cur.close()
            return jsonify({"message": "registered successfully"})
        except:
            cur.close()
            conn.rollback()
            return jsonify({"error": "failed to register user"})
    else:
        return jsonify({"error": "invalid request"})

# get impressions by user (testing)
@app.route("/impressions", methods=['GET'])
def get_impressions_by_user():
    data = request.get_json()
    username = data.get('username')

    cur = conn.cursor()
    try:
        cur.execute(f"select * from impressions where username = '{username}'")
        rows = cur.fetchall()
        cur.close()
        return jsonify({"message": str(rows)})
    except:
        cur.close()
        conn.rollback()
        return jsonify({"error": "failed to get impressions"})

# get all items (testing)
@app.route("/items", methods=['GET'])
def get_items():
    cur = conn.cursor()
    try:
        cur.execute(f"select * from items")
        rows = cur.fetchall()
        cur.close()
        return jsonify({"message": str(rows)})
    except:
        cur.close()
        conn.rollback()
        return jsonify({"error": "failed to get items"})
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)
