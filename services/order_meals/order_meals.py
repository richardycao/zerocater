import requests
import psycopg2
import postgres
from collections import defaultdict
import datetime as dt

"""
this is a daily job.
heuristic approach:
it gets each (username,token) from the users table
for each username, 
    - produces a dict with all item scores for this user, using items from the db
        - heuristic approach
            - it gets the impressions from the last 30 days. 
            - using these impressions, it finds the user's average rating for each item. unseen items are 
            given rating=0 by default.

    - for each day and meal time in the next 2 weeks on the user's preferred floor, 
        - it uses the average ratings to score each item. 
        - it needs to take into account the max subsidy. if it's possible to order 2 items, then it first
        orders the highest rated item, then it fills in the remaining space with the next highest rated item
        that is from the same restautant and that can fit into the remaining space.
    
"""

pg = postgres.PostgresClient()

def get_users():
    return pg.execute_read("select * from users")

def get_heuristic_item_scores(username):
    today = dt.datetime.now()
    start = (today - dt.timedelta(days=30)).strftime('%Y%m%d')

    rows, err = pg.execute_read(f"select item_id, rating from impressions where date > '{start}' and username = '{username}'")
    if err: return {}, err

    item_scores = defaultdict(lambda: [])
    for item_id, rating in rows:
        item_scores[item_id].append(rating)
    for item_id in item_scores.keys():
        item_scores[item_id] = sum(item_scores[item_id]) / len(item_scores[item_id])

    return item_scores, None

def get_model_item_scores(username):
    return defaultdict(lambda: 0)

def run():
    user_token_list, err = get_users()
    if err: return

    for username, token, _, _ in user_token_list:
        item_scores, err = get_heuristic_item_scores(username)
        if err: continue

        # get meals over the next 3 weeks




if __name__ == "__main__":
    test = True

    if test:
        # run once when users are ready
        users, err = get_users()
        while err:
            time.sleep(5)
            users, err = get_users()
            
        run()
    else:
        # run once a day, checking at 10 minute intervals
        prev_date = ""
        while True:
            cur_date = dt.datetime.now().strftime('%Y%m%d')
            while cur_date == prev_date:
                time.sleep(600) # sleep 10 minutes
                cur_date = dt.datetime.now().strftime('%Y%m%d')
            prev_date = cur_date

            run()