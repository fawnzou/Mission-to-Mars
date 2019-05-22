from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of our Flask app.
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection

mongo = PyMongo(app, uri="mongodb://localhost:27017/Marsinfo_app")

@app.route("/")
def home():
    # Find one record of data from the mongo database
    Marsinfo_data = mongo.db.collection.find_one()
    print(Marsinfo_data)
    # Return template and data
    return render_template('index.html', Marsinfo=Marsinfo_data)

@app.route("/scrape")
def scraper():
    # Run the scrape function
    Marsinfo_data = scrape_mars.scrape()
    # Update the Mongo database using update and upsert=True
    mongo.db.collection.update({}, Marsinfo_data, upsert=True)
    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)



