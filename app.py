from flask import Flask, session, Response, request, render_template, jsonify
from captcha import generate_captcha
import redis
from dotenv import load_dotenv
import uuid
import os

# Create a Flask application instance with the name of the current module
load_dotenv()
app = Flask(__name__)
app.secret_key = "kakdi"
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    username=os.getenv("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSOWRD"),
)


# Use the route() decorator to bind a URL path (/) to a function
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/captcha", methods=["GET", "POST"])
def captcha():
    try:
        # Get UID from request
        data = {}
        uid = str(uuid.uuid4())
        print(uid)
        try:
            data = request.get_json(silent=True)
        except Exception as e:
            raise ValueError(e)

        # Generate captcha
        captcha_text, captcha_buf = generate_captcha(data)
        if not captcha_text or not captcha_buf:
            raise ValueError("Failed to generate captcha")

        # Store captcha in Redis with TTL of 2 minutes
        try:
            r.set(uid, captcha_text, ex=120)
        except redis.RedisError as e:
            app.logger.error(f"Redis error: {e}")
            return jsonify({"error": "Internal server error"}), 500

        # Return captcha image
        response = Response(captcha_buf, mimetype="image/png")
        response.headers["hash"] = uid
        return response

    except Exception as e:
        app.logger.error(f"Captcha generation failed: {e}")
        return jsonify({"error": "Failed to generate captcha"}), 500


@app.route("/verify")
def verify():
    try:
        # Get parameters
        user_guess = request.args.get("guess", "").strip().upper()
        uid = request.args.get("uid", "").strip()

        if not uid or not user_guess:
            return jsonify({"error": "UID and guess are required"}), 400

        # Get captcha from Redis
        try:
            stored_captcha = r.get(uid)
        except redis.RedisError as e:
            app.logger.error(f"Redis error: {e}")
            return jsonify({"error": "Internal server error"}), 500

        if stored_captcha is None:
            return (
                jsonify({"result": False, "reason": "Expired or invalid CAPTCHA"}),
                400,
            )

        # Decode bytes to string if necessary
        if isinstance(stored_captcha, bytes):
            stored_captcha = stored_captcha.decode()

        # Check user guess
        if user_guess == stored_captcha:
            try:
                r.delete(uid)  # Delete after successful verification
            except redis.RedisError as e:
                app.logger.error(f"Redis delete error: {e}")
            return jsonify({"result": True})

        return jsonify({"result": False, "reason": "incorrect"})

    except Exception as e:
        app.logger.error(f"Captcha verification failed: {e}")
        return jsonify({"error": "Failed to verify captcha"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
