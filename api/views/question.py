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


@api.route("questions/<question_id>/answers", methods=["GET", "POST"])
@requires_authentication
def answers(user_id, question_id):
    """Post, retrieve a question's answers using the question id
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
    if request.method == "POST":
        answer_body = request.get_json('answer_body')['answer_body']
        if not answer_body or answer_body == " ":
            response = {
                "message": "Answer cannot be blank"
            }

            return make_response(jsonify(response)), 400

        cur.execute("SELECT answer_body FROM questions INNER JOIN answers ON "
                    "answers.question_id = questions.question_id WHERE"
                    "(answers.answer_body = '{}' AND answers.user_id = '{}' AND answers.question_id = '{}')"
                    .format(answer_body, user_id, question_id))

        answer_exists = cur.fetchall()

        if answer_exists:
            response = {
                "message": "You have already given that answer"
            }

            return make_response(jsonify(response)), 409

        time = datetime.utcnow()
        Answer(answer_body, time)
        cur.execute("SELECT MAX(answer_id) from answers")
        answer = cur.fetchone()

        cur.execute("UPDATE answers SET user_id='{}' where answer_id='{}'".format(user_id, answer[0]))

        cur.execute("SELECT username FROM users WHERE user_id='{}'".format(user_id))
        user = cur.fetchone()

        cur.execute("UPDATE answers SET answered_by='{}' WHERE answer_id='{}'".format(user[0], answer[0]))
        conn.commit()

        cur.execute("UPDATE answers SET question_id = {} where answer_id ='{}'"
                    .format(question_id, answer[0]))
        conn.commit()

        cur.execute("SELECT questions.user_id FROM questions INNER JOIN answers"
                    " ON answers.question_id=questions.question_id WHERE questions.question_id='{}'".format(question_id))

        question_owner = cur.fetchone()
        cur.execute("UPDATE answers SET question_owner='{}' WHERE  answer_id='{}'".format(question_owner[0], answer[0]))
        conn.commit()

        cur.execute("SELECT * FROM answers WHERE answer_body='{}' AND user_id='{}'".format(answer_body, user_id))
        answer_data = cur.fetchone()

        cur.execute("UPDATE questions SET answers = array_append(answers, '{}') WHERE question_id='{}'".
                    format(answer_data[1], question_id))
        conn.commit()

        cur.execute("UPDATE  users SET answers = array_append(answers, '{}')".format(answer_data[1]))
        cur.close()

        response = {
            "answer_id": answer_data[0],
            "answer": answer_data[1],
            "question_id": answer_data[2],
            "user_id": answer_data[3],
            "answered_by": answer_data[4],
            "question_owner": answer_data[5],
            "answered_at": answer_data[6]
        }

        return make_response(jsonify(response)), 201
    else:
        response = {
            "message": "Method currently after development"
        }

        return make_response(jsonify(response)), 200







