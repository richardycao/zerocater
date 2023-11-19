from flask import Flask, request, jsonify
import os
import psycopg2
import datetime as dt
import sys
import postgres

"""
This is the api for registering users.
"""

app = Flask(__name__)
pg = postgres.PostgresClient()

# get user
@app.route("/user", methods=['GET'])
def get_user():
    data = request.get_json()
    username = data.get('username')

    rows, err = pg.execute_read(f"select * from users where username like '{username}'")
    if err:
        return jsonify({"error": "failed to get user"})
    
    return jsonify({"message": str(rows)})

# create user
@app.route("/user", methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    token = data.get('token')
    preferred_floor = data.get('preferred_floor')

    if username and token:
        rows, err = pg.execute_read("select count(*) from users")
        if err:
            return jsonify({"error": "failed to register user 1"})
        
        if len(rows) > 0 and len(rows[0]) > 0:
            num_rows = rows[0][0]
        else:
            return jsonify({"error": "failed to register user 2"})
        
        err = pg.execute_writes([f"insert into users values ('{username}','{token}','{num_rows}','{preferred_floor}') on conflict(username) do update set token = '{token}', preferred_floor = {preferred_floor}"])
        if err:
            return jsonify({"error": "failed to register user 3"})
        
        return jsonify({"message": "registered successfully"})
    else:
        return jsonify({"error": "invalid request"})

# get impressions by user (testing)
@app.route("/impressions", methods=['GET'])
def get_impressions_by_user():
    data = request.get_json()
    username = data.get('username')

    rows, err = pg.execute_read(f"select * from impressions where username = '{username}'")
    if err:
        return jsonify({"error": "failed to get impressions"})
    
    return jsonify({"message": str(rows)})

# get all items (testing)
@app.route("/items", methods=['GET'])
def get_items():
    rows, err = pg.execute_read("select * from items")
    if err:
        return jsonify({"error": "failed to get items"})
    
    return jsonify({"message": str(rows)})
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)
