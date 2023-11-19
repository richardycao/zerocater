from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

def connect_db():
    print(os.getenv('POSTGRES_USER'), os.getenv('POSTGRES_PASSWORD'))
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database='zerocater',
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
    )

    cur = conn.cursor()
    cur.execute("create table if not exists users (username text PRIMARY KEY, token text)")
    conn.commit()

    return conn, cur

conn, cur = connect_db()

@app.route("/", methods=['GET'])
def health():
    return jsonify({"message": "healthy"})

@app.route("/user", methods=['GET'])
def get_user():
    data = request.get_json()
    username = data.get('username')
    try:
        cur.execute(f"select * from users where username like '{username}'")
        rows = cur.fetchall()
        return jsonify({"message": str(rows)})
    except:
        return jsonify({"error": "failed to get user"})

@app.route("/user", methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    token = data.get('token')

    if username and token:
        try:
            cur.execute(f"insert into users values ('{username}','{token}')")
            conn.commit()
            return jsonify({"message": "registered successfully"})
        except:
            return jsonify({"error": "failed to register user"})
    else:
        return jsonify({"error": "invalid request"})
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)
