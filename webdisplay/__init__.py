from flask import Flask, redirect, url_for, render_template
import csv

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=('GET',))
    def index():
        return redirect(url_for('stats'))

    @app.route("/stats", methods=('GET',))
    def stats():
        return render_template("stats.html")
    
    @app.route("/about", methods=('GET',))
    def about():
        return render_template("about.html")
    
    @app.route("/raw_data", methods=('GET',))
    def raw_data():
        data = []
        with open('./webdisplay/static/scrapped_data.csv', 'r') as f:
            reader = csv.reader(f)

            for i,row in enumerate(reader):
                if(i>0):
                    r = [i]
                    r.extend(row)
                    data.append(r)

        return render_template("raw_data.html", data=data)
    
    return app