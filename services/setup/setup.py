from flask import Flask, request, jsonify
import psycopg2
import sys
import postgres
import logging

"""
This job creates postgres tables.
"""

app = Flask(__name__)
app.logger.setLevel(logging.WARNING)
pg = postgres.PostgresClient()

def create_users_table():
    err = pg.execute_writes(["create table if not exists users (username text PRIMARY KEY, token text, idx integer, preferred_floor integer)"])
    if err:
        print('failed to create users table.', err)
        sys.exit(1)

def create_items_table():
    err = pg.execute_writes(["create table if not exists items (item_id integer PRIMARY KEY, idx integer)"])
    if err:
        print('failed to create items table.', err)
        sys.exit(1)

def create_impressions_table():
    err = pg.execute_writes(["create table if not exists impressions (date text, username text, item_id integer, rating integer, PRIMARY KEY (date, username, item_id))"])
    if err:
        print('failed to create impressions table.', err)
        sys.exit(1)



# health
@app.route("/", methods=['GET'])
def health():
    return jsonify({"message": "healthy"})

if __name__ == "__main__":
    create_users_table()
    create_items_table()
    create_impressions_table()

    app.run(host='0.0.0.0', port=3000, debug=False)
