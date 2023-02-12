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
=# CREATE DATABASE warbler;
(ctrl+D)
$ python3 seed.py
```
3. Add a .env file with:
```
SECRET_KEY=(any secret key you want)
DATABASE_URL=postgresql:///warbler
```
4. Run the server:
```
$ flask run -p 5001
```
5. View at `localhost:5001`

## // TODO
- Fix background image formatting
- Shift to responsive, SPA front-end framework
- Write more tests