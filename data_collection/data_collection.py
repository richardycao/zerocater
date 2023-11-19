import datetime as dt
import time
import requests
import json
import psycopg2
import os

"""
This job collects impressions data for each registered user once a day.
"""

BASE_URL = 'https://gateway.zerocater.com/api/v4'
FLOOR_CODES = {
    5: '24386',
    6: '24387',
    7: '24388',
    11: '24158',
    12: '23876'
}

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

    """
    notes:
    need to determine which of username or date should be primary key
    this job updates the table by user
    with heuristic-based food recommendation, we will get all of a user's past orders in the last 30 days
        and rank them by rating. then we will pick food according to that. so it is by user, then by date.
    with model-based food recommendation, we will first train on all impressions within the last 30 days.
        then for a specific user, we will evaluate all of the candidates meals of each day and pick the
        highest-rated one. so it is by date, then user.
    """

    cur = conn.cursor()
    try:
        cur.execute("create table if not exists impressions (date text, username text, item_id integer, rating integer, PRIMARY KEY (date, username, item_id))")
        conn.commit()
        cur.execute("create table if not exists items (item_id integer PRIMARY KEY, idx integer)")
        conn.commit()
        cur.close()
    
        return conn
    except Exception as e:
        cur.close()
        conn.rollback()
        print('failed to create table.', e)
        sys.exit(1)

conn = connect_db()

def get_users_tokens():
    cur = conn.cursor()
    try:
        cur.execute(f"select * from users")
        rows = cur.fetchall()
        cur.close()
        return rows
    except:
        cur.close()
        conn.rollback()
        return None

def record_item(item_id):
    cur = conn.cursor()
    try:
        cur.execute(f"select count(*) from items")
        rows = cur.fetchall()
        num_rows = rows[0][0]

        cur.execute(f"insert into items values ({item_id},{num_rows})")
        conn.commit()
        cur.close()
    except:
        cur.close()
        conn.rollback()

def record_impression(date, username, item_id, rating):
    cur = conn.cursor()
    try:
        cur.execute(f"insert into impressions values ('{date}','{username}',{item_id},{rating}) on conflict(date, username, item_id) do update set rating = {rating}")
        conn.commit()
        cur.close()
    except Exception as e:
        cur.close()
        conn.rollback()

def http(type, endpoint, token, **kwargs):
    if type == 'GET':
        return requests.get(BASE_URL + endpoint + '?' + '&'.join([f'{k}={v}' for k,v in kwargs.items()]),
                            headers={'Authorization': f'Token {token}'})

def get_scheduled_meals(token, floor_code):
    today = dt.datetime.now()
    lower_dt = today + dt.timedelta(days=-30)
    upper_dt = today + dt.timedelta(days=0)
    start = f'{lower_dt.year}-{lower_dt.month}-{lower_dt.day}'
    end = f'{upper_dt.year}-{upper_dt.month}-{upper_dt.day}'

    try:
        res = http('GET', '/cloud_cafe/meals', token, start=start, end=end, address_id=floor_code)
        return json.loads(res.content)
    except:
        return None

def get_user_orders(token, meal_id):
    try:
        res = http('GET', f'/cloud_cafe/meals/{meal_id}/user_orders', token)
        return json.loads(res.content)
    except:
        return None

def get_user_item_feedback(token, meal_id):
    try:
        res = http('GET', f'/user_item_feedback', token, current_user=1, meal=meal_id)
        return json.loads(res.content)
    except:
        return None

# def get_user_orders(token, floor_code):
#     today = dt.datetime.now()
#     lower_dt = today + dt.timedelta(days=-30)
#     upper_dt = today + dt.timedelta(days=0)
#     start = f'{lower_dt.year}-{lower_dt.month}-{lower_dt.day}'
#     end = f'{upper_dt.year}-{upper_dt.month}-{upper_dt.day}'

#     try:
#         res = http('GET', '/cloud_cafe/user_orders', token, start=start, end=end, address_id=floor_code)
#         return json.loads(res.content)
#     except:
#         return None

# def get_user_item_feedback(token):
#         res_pos = http('GET', f'/recent_user_item_feedback', token, is_positive='true', limit=60)
#         res_neg = http('GET', f'/recent_user_item_feedback', token, is_positive='false', limit=60)
#         return json.loads(res_pos.content) + json.loads(res_neg.content)
#     except:
#         return None

def run():
    # get the most recent (username, token) pair for each username in the users table
    user_token_list = get_users_tokens()
    if not user_token_list:
        return
    
    for username, token, _, _ in user_token_list:
        for floor, floor_code in FLOOR_CODES.items():
            scheduled_meals = get_scheduled_meals(token, floor_code)
            if not scheduled_meals:
                continue
            for scheduled_meal in scheduled_meals:
                sm_dt = scheduled_meal['time']
                sm_date = f"{sm_dt[:4]}{sm_dt[5:7]}{sm_dt[8:10]}"
                if scheduled_meal['ordered_items'] > 0:
                    user_orders = get_user_orders(token, scheduled_meal['id'])
                    for menu_item in user_orders:
                        # record item
                        item_id = menu_item['item_id']
                        record_item(item_id)
                        
                        # record impression
                        user_item_feedback = get_user_item_feedback(token, scheduled_meal['id'])
                        if not user_item_feedback:
                            record_impression(sm_date, username, item_id, 0)
                            continue
                        for feedback in user_item_feedback:
                            record_impression(sm_date, username, item_id, 1 if feedback['is_positive'] else -1)

if __name__ == "__main__":
    prev_date = ""
    # while True:
    #     cur_dt = dt.datetime.now()
    #     cur_date = f"{cur_dt.year}{cur_dt.month}{cur_dt.day}"
    #     while cur_date == prev_date:
    #         time.sleep(600) # sleep 10 minutes
    #         cur_dt = dt.datetime.now()
    #         cur_date = f"{cur_dt.year}{cur_dt.month}{cur_dt.day}"
    #     prev_date = cur_date

        # run the job here
    
    # delay for testing
    uts = get_users_tokens()
    while not uts:
        time.sleep(5)
        uts = get_users_tokens()
        
    run()


