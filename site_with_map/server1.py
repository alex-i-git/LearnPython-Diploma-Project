from db import Survey
from flask import Flask, render_template

my_flask_app = Flask(__name__)

@my_flask_app.route("/")
def index():
	surv = Survey
	result = surv.query.filter(Survey.latitude > 0).filter(Survey.longitude > 0).all()
	for item in result:
		print(item)
	return render_template("index.html", surveys=result)

@my_flask_app.route("/about/")
def about():

	return render_template("about.html")

if __name__ == "__main__":
	my_flask_app.run(debug=True)