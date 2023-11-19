import requests
import psycopg2
from collections import defaultdict

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

def get_heuristic_item_scores(username):
    return defaultdict(lambda: 0)

def get_model_item_scores(username):
    return defaultdict(lambda: 0)

if __name__ == "__main__":
    test = True

    if test:
        # run once when users are ready
        uts = get_users_tokens()
        while not uts:
            time.sleep(5)
            uts = get_users_tokens()
            
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