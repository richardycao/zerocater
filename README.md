# zerocater

## how to use

#### setup

`cd zerocater`
`docker-compose up -d`

#### register/update a user

`curl -X POST http://localhost:3001/user -d '{"username": "xxx", "token": "xxx", "preferred_floor": 0}'`

#### shut down and delete database and storage

`./reset_docker.sh`

## services

server
- the api server, with access only exposed to the local instance. used to register/update users or debug.

data_collection
- daily job that collects the latest impressions for all registered users.

train_model 
- daily job that trains the model on recent impressions and store it in object storage.

order_meals 
- heuristic: retrieves the users historical impressions and ranks them by average rating. then evaluates food options based on that ranking.
- model_based: retrieves the model from object storage and uses it to evaluate food options on each meal of each day. 

## todo

1. set up order_meals
1. set up minio object storage
1. set up train_model
1. adjust order_meals to use it