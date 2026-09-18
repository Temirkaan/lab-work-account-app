from flask import Flask, render_template, request, redirect, url_for, jsonify
import database as db

app = Flask(__name__)


@app.route("/")
def index():
    status = request.args.get("status") or None
    group = request.args.get("group") or None

    students = db.get_students()
    labs = db.get_labs()
    submissions = db.get_submissions(status=status, group=group)

    stats = {
        "students": db.count_students(),
        "labs": db.count_labs(),
        "submitted": db.count_by_status("submitted"),
        "checked": db.count_by_status("checked"),
    }

    return render_template(
        "index.html",
        students=students,
        labs=labs,
        submissions=submissions,
        stats=stats,
    )


@app.route("/students", methods=["POST"])
def add_student():
    full_name = request.form.get("full_name", "").strip()
    group_name = request.form.get("group_name", "").strip()
    if full_name and group_name:
        db.add_student(full_name, group_name)
    return redirect(url_for("index"))


@app.route("/labs", methods=["POST"])
def add_lab():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    max_score = request.form.get("max_score", "10")
    deadline = request.form.get("deadline", "").strip()
    if title and subject:
        try:
            max_score = int(max_score)
        except ValueError:
            max_score = 10
        db.add_lab(title, subject, max_score, deadline)
    return redirect(url_for("index"))


@app.route("/submissions", methods=["POST"])
def add_submission():
    student_id = request.form.get("student_id")
    lab_work_id = request.form.get("lab_work_id")
    comment = request.form.get("comment", "").strip()
    if student_id and lab_work_id:
        db.add_submission(student_id, lab_work_id, comment)
    return redirect(url_for("index"))


@app.route("/submissions/<int:submission_id>/check", methods=["POST"])
def check_submission(submission_id):
    score = request.form.get("score")
    comment = request.form.get("comment", "").strip()
    if score and score.isdigit():
        db.check_submission(submission_id, score, comment)
    return redirect(url_for("index"))


@app.route("/submissions/<int:submission_id>/revision", methods=["POST"])
def revision_submission(submission_id):
    comment = request.form.get("comment", "").strip()
    db.send_to_revision(submission_id, comment)
    return redirect(url_for("index"))


@app.route("/api/submissions")
def api_submissions():
    status = request.args.get("status") or None
    group = request.args.get("group") or None
    rows = db.get_submissions(status=status, group=group)
    items = [dict(r) for r in rows]
    return jsonify({"count": len(items), "items": items})


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)