from datetime import datetime

from flask import jsonify, request, make_response
from . import api

from api.models.question import Question, Answer
from database.config import open_connection, close_connection

from api.helper_functions.decorators import requires_authentication
from api import app


@api.route("/questions", methods=["POST", "GET"])
@requires_authentication
def questions(user_id):
    conn = open_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute("SELECT * FROM questions ORDER BY question_id DESC")
        question_set = cur.fetchall()
        all_questions = []
        for question in question_set:
            result = {
                "question_id": question[0],
                "question_title": question[1],
                "answer": question[3],
                "user_id": question[2],
                "asked_by":question[4],
                "date_created": question[5]
            }

            all_questions.append(result)
        return jsonify({"questions": all_questions})

    else:
        question_title = request.get_json('title')['title']
        if not question_title or question_title == " ":
            response = {
                "message": "Title cannot be empty"
            }

            return make_response(jsonify(response)), 400

        cur.execute("SELECT * FROM questions WHERE title='{}' and user_id='{}'".format(question_title, user_id))

        question_exists = cur.fetchall()

        if question_exists:
            response = {
                "message": "Question already exists"
            }

            return make_response(jsonify(response)), 409

        else:
            time = datetime.utcnow()
            Question(question_title, time)
            cur.execute("SELECT MAX(question_id) FROM questions")
            question = cur.fetchone()

            cur.execute("UPDATE questions SET user_id='{}' WHERE question_id='{}'".format(user_id, question[0]))
            conn.commit()

            cur.execute("SELECT * FROM questions WHERE title='{}' and user_id='{}'".format(question_title, user_id))
            questions = cur.fetchall()
            cur.execute("SELECT username FROM users WHERE user_id='{}'".format(user_id))
            username = cur.fetchone()

            cur.execute("UPDATE questions SET asked_by='{}' WHERE question_id='{}'".format(username[0], question[0]))
            conn.commit()

            data = []
            display_data = {
                "question_id": questions[0][0],
                "question_title": questions[0][1],
                "answer": questions[0][3],
                "user_id": questions[0][2],
                "asked_by": questions[0][4],
                "date_created": questions[0][5]
            }

            data.append(display_data)
            cur.execute("UPDATE users SET questions = array_append(questions, '{}')".format(questions[0][1]))
            conn.commit()
            cur.close()
            close_connection(conn)

            response = {
                "message": "Question created successfully",
                "question": data
            }

            return make_response(jsonify(response)), 200


@api.route("/questions/<question_id>", methods=["GET", "DELETE"])
@requires_authentication
def manipulate_questions(user_id, question_id):
    """Perform question gets, updates and deletes using the question_id
    """

    conn = open_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions WHERE question_id='{}'".format(question_id))
    question = cur.fetchall()
    if not question:
        response = {
            "message": "Question with that id does not exist"
        }

        return make_response(jsonify(response)), 404

    if request.method == "GET":
        return jsonify({"question": question[0]})

    if request.method == "DELETE":
        if question[0][2] != user_id:
            response = {
                "message": "You cannot delete question, not owner"
            }

            return make_response(jsonify(response)), 401

        cur.execute("UPDATE users SET questions = array_remove(questions, '{}')".format(question[0][1]))

        cur.execute("DELETE FROM answers WHERE question_id='{}'".format(question_id))
        cur.execute("DELETE FROM questions WHERE question_id='{}' and user_id='{}'".format(question_id, user_id))
        conn.commit()
        cur.close()
        close_connection(conn)

        response = {
            "message": "Question deleted successfully"
        }

        return make_response(jsonify(response)), 200






