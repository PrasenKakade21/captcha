from flask import Flask,session,Response,request,render_template
from captcha import generate_captcha
import redis
# Create a Flask application instance with the name of the current module
app = Flask(__name__)
app.secret_key = "kakdi"
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Use the route() decorator to bind a URL path (/) to a function
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/captcha")
def captcha():
    captcha_text,captcha_buf = generate_captcha()
    uid = request.args.get("uid", "").strip()
    session["captcha"] = captcha_text
    r.set(uid,captcha_text,ex=120)
    return Response(captcha_buf, mimetype="image/png")


@app.route("/verify")
def verify():
    user_guess = request.args.get("guess", "").strip().upper()
    uid = request.args.get("uid", "").strip()
    stored_captcha = r.get(uid)
    
    if stored_captcha is None:
        return "Expired or invalid CAPTCHA " + uid

    if user_guess == stored_captcha:
        r.delete(uid)
        return "True " + stored_captcha 
    return "False " + stored_captcha 


if __name__ == "__main__":
    app.run(debug=True) # Run the app in debug mode
