from .config import open_connection, close_connection

QUERY_SET = [
    """
     
     CREATE TABLE IF NOT EXISTS users (
         user_id SERIAL PRIMARY KEY NOT NULL,
         username VARCHAR NOT NULL,
         email VARCHAR NOT NULL,
         password VARCHAR NOT NULL,
         questions VARCHAR[] NOT NULL default '{}',
         answers VARCHAR[] NOT NULL default '{}',
         date_created TIMESTAMP
     )
    """,
    """
    CREATE TABLE IF NOT EXISTS questions (
    question_id SERIAL PRIMARY KEY NOT NULL,
    title VARCHAR NOT NULL,
    user_id INT REFERENCES users(user_id),
    answers VARCHAR[] NOT NULL default '{}',
    asked_by VARCHAR,
    date_created TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS answers (
    answer_id SERIAL PRIMARY KEY NOT NULL,
    answer_body VARCHAR NOT NULL,
    user_id INT REFERENCES users(user_id),
    question_id INT REFERENCES questions(question_id),
    answered_by VARCHAR,
    answered_at TIMESTAMP
    )
    """

]


def create_tables():
    """create tables
    """
    conn = open_connection()
    cur = conn.cursor()

    for query in QUERY_SET:
        cur.execute(query)

    close_connection(conn)


def drop_tables():
    """Drop tables
    """
    query_set = [
        'DROP TABLE users CASCADE',
        'DROP TABLE questions CASCADE',
        'DROP TABLE answers CASCADE'
    ]

    conn = open_connection()
    cur = conn.cursor

    for query in query_set:
        cur.execute(query)

    close_connection(conn)

