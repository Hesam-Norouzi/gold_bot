import psycopg2
from decouple import config

# Database connection
conn = psycopg2.connect(
    dbname=config('dbname'),
    user=config('user'),
    password=config('password'),
    host=config('host'),
    port=config('port')
)
cur = conn.cursor()