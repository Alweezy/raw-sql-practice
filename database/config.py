import psycopg2
import os


def db_connect():
    """Establish a database connection
    """
    url = os.getenv('DATABASE_URI')

    try:
        return psycopg2.connect(url)

    except Exception as e:
        print(str(e))


def open_connection():
    """Open connection to execute queries """
    conn = db_connect()
    return conn


def close_connection(conn):
    """Close db connection"""
    conn.commit()
    conn.close()
