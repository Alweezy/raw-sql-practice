from database.config import open_connection, close_connection


class Question(object):
    """Defines the question model
    """

    def __init__(self, title, time):
        self.title = title
        conn = open_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO questions (title, date_created) VALUES ('{}', '{}')".format(self.title, time))
        close_connection(conn)


class Answer(object):
    """Defines the answer model
    """
    def __init__(self, answer_body, time):
        self.answer_body = answer_body
        conn = open_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO answers "
                    "(answer_body, date_answered) VALUES ('{}', '{}')".format(self.answer_body, time))
        close_connection(conn)