# Warbler
A twitter clone with a Flask back end

## Features
- User registration/authentication/profile deletion
- Posting, liking, and deleting messages
- Following/unfollowing users
- Chronological feed of followed-users' messages
- 92% test coverage

## Setting it up
1. Create a virtual environment and install requirements:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
2. Set up the database (PostgreSQL):
```
$ psql
=# CREATE DATABASE
(ctrl+D)
$ python3 seed.py
```
3. Run the server:
```
$ flask run -p 5001
```
4. View at `localhost:5001`

## // TODO
- Fix background image formatting
- Shift to responsive, SPA front-end framework
- Write more tests