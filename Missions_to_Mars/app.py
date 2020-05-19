#Import dependencies
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

#Set app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/marsmission_app"
mongo = PyMongo(app)

#Get mars data - if available will fetch else it will return no results
@app.route("/")
def index():
    marsinfo = mongo.db.marsinfo.find_one()
    return render_template("index.html", marsinfo=marsinfo)

#Scrape data
@app.route("/scrape")
def scraper():
    marsinfo = mongo.db.marsinfo
    mars_data = scrape_mars.scrape()
    marsinfo.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

#Reminder - set flag to False before deploying the app
if __name__ == "__main__":
    app.run(debug=False)
