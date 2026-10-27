
import requests
from flask import jsonify

@app.route("/classmate-students", methods=["GET"])
def get_classmate_students():
    url = "https://ladoing-kc-jane-marie.onrender.com/students"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        data = response.json()
        return jsonify(data), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "The classmate API timed out. Please try again."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Could not connect to the classmate API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "The classmate API did not return valid JSON."
        }), 502
