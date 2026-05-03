import os
import boto3
from flask import Flask, jsonify, request

app = Flask(__name__)

REGION = os.environ.get("AWS_REGION", "ap-south-2")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
courses_table = dynamodb.Table("course-jagan")


# ---------------- HEALTH ----------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "course-service"}), 200


# ---------------- CREATE COURSE (POST) ----------------
@app.route("/courses", methods=["POST"])
def create_course():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    code = data.get("code")
    title = data.get("title")

    if not code or not title:
        return jsonify({"error": "code and title are required"}), 400

    try:
        courses_table.put_item(
            Item={
                "code": code,
                "title": title
            }
        )

        return jsonify({
            "message": "Course created successfully",
            "course": {
                "code": code,
                "title": title
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET ONE ----------------
@app.route("/courses/<course_code>", methods=["GET"])
def get_course(course_code):
    resp = courses_table.get_item(Key={"code": course_code})
    item = resp.get("Item")

    if not item:
        return jsonify({"error": "Course not found"}), 404

    return jsonify(item), 200


# ---------------- GET ALL ----------------
@app.route("/courses", methods=["GET"])
def list_courses():
    resp = courses_table.scan(Limit=50)
    return jsonify(resp.get("Items", [])), 200


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=False)