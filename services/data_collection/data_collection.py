import datetime as dt
import time
import requests
import json
import psycopg2
import postgres

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

pg = postgres.PostgresClient()

def get_users():
    rows, err = pg.execute_read("select * from users")
    return rows if not err else None

def record_item(item_id):
    rows, err = pg.execute_read("select count(*) from items")
    if err: return
    if len(rows) > 0 and len(rows[0]) > 0:
        num_rows = rows[0][0]
    else: return

    err = pg.execute_writes([f"insert into items values ({item_id},{num_rows})"])

def record_impression(date, username, item_id, rating):
    err = pg.execute_writes([f"insert into impressions values ('{date}','{username}',{item_id},{rating}) on conflict(date, username, item_id) do update set rating = {rating}"])

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
    user_token_list = get_users()
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
    test = True

    if test:
        # run once when users are ready
        uts = get_users()
        while not uts:
            time.sleep(5)
            uts = get_users()
            
        run()
    else:
        # run once a day, checking at 10 minute intervals
        prev_date = ""
        while True:
            cur_dt = dt.datetime.now()
            cur_date = f"{cur_dt.year}{cur_dt.month}{cur_dt.day}"
            while cur_date == prev_date:
                time.sleep(600) # sleep 10 minutes
                cur_dt = dt.datetime.now()
                cur_date = f"{cur_dt.year}{cur_dt.month}{cur_dt.day}"
            prev_date = cur_date

            run()
