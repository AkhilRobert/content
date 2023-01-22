# FIXME: Change the collection name to valid one on deploy
import html
from typing import Union

from bson import json_util
from flask import Flask, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Testing"
mongo = PyMongo(app)

# TODO: Remove this while deploying
CORS(app)

collection = mongo.db.testing  # pyright: ignore

map = {
    "Puducherry": "in-py",
    "Lakshadweep": "in-ld",
    "West Bengal": "in-wb",
    "Odisha": "in-or",  # Orissa -> Odisha
    "Bihar": "in-br",
    "Sikkim": "in-sk",
    "Chhattisgarh": "in-ct",
    "Tamil Nadu": "in-tn",
    "Madhya Pradesh": "in-mp",
    "Gujarat": "in-2984",
    "Goa": "in-ga",
    "Nagaland": "in-nl",
    "Manipur": "in-mn",
    "Arunachal Pradesh": "in-ar",
    "Mizoram": "in-mz",
    "Tripura": "in-tr",
    "Daman and Diu": "in-3464",
    "Delhi (Ut)": "in-dl",  # Delhi -> Delhi (Ut)
    "Haryana": "in-hr",
    "Chandigarh": "in-ch",
    "Himachal Pradesh": "in-hp",
    "Jammu & Kashmir": "in-jk",  # and -> &
    "Kerala": "in-kl",
    "Karnataka": "in-ka",
    "Dadra and Nagar Haveli": "in-dn",
    "Maharashtra": "in-mh",
    "Assam": "in-as",
    "Andhra Pradesh": "in-ap",
    "Meghalaya": "in-ml",
    "Punjab": "in-pb",
    "Rajasthan": "in-rj",
    "Uttar Pradesh": "in-up",
    "Uttarakhand": "in-ut",  # Uttaranchal -> Uttarakhand
    "Jharkhand": "in-jh",
}


def get_key(state_name: str) -> Union[str, None]:
    try:
        return map[state_name]
    except KeyError:
        return None


def get_state(id: str) -> str:
    for k, v in map.items():
        if v == id:
            return k

    return ""


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/api/map")
def total_count():
    """
    query : db.testing.aggregate([{$group: {_id: {State: "$State"}, count: {$sum: "$Total"}}}])
    This groups using state and count on the total field

    ---
    Total data for the map view
    """
    formatted_states = []
    states = collection.aggregate(
        [{"$group": {"_id": {"State": "$State"}, "count": {"$sum": "$Total"}}}]
    )
    for s in states:
        # Ignoring the extra data as we don't need them for the map :\
        # TODO: find a better solution
        key = (
            get_key(s["_id"]["State"]) if get_key(s["_id"]["State"]) is not None else ""
        )
        formatted_states.append([key, s["count"]])

    return formatted_states


@app.route("/<string:id>")
def state_page(id: str):
    state = get_state(id)
    return render_template("state.html", state=state)


@app.route("/api/by-year/<string:state>")
def get_by_year(state: str):
    """
    query : db.testing.aggregate(
        [
            {"$match": {"State": state}},
            {
                "$group": {
                    "_id": {"year": "$year"},
                    "count": {"$sum": "$total"},
                },
            },
            {"$sort": {"_id.Year": 1}},
        ]
    )

    This filters using the state name and then groups using the by year
    and then sums the total number of suicide cases for that year

    ---
    Data for the year wise graph
    """

    data = collection.aggregate(
        [
            {"$match": {"State": html.unescape(state)}},
            {
                "$group": {
                    "_id": {"Year": "$Year"},
                    "count": {"$sum": "$Total"},
                },
            },
            {"$sort": {"_id.Year": 1}},
        ]
    )
    return json_util.dumps(data)


@app.route("/api/by-gender/<string:state>")
def get_by_gender(state: str):
    data = collection.aggregate(
        [
            {"$match": {"State": html.unescape(state)}},
            {
                "$group": {
                    "_id": {"Gender": "$Gender"},
                    "count": {"$sum": "$Total"},
                },
            },
        ]
    )
    return json_util.dumps(data)


@app.route("/api/by-education/<string:state>")
def get_by_education_status(state: str):
    data = collection.aggregate(
        [
            {"$match": {"State": html.unescape(state)}},
            {
                "$group": {
                    "_id": {"Gender": "$Gender"},
                    "count": {"$sum": "$Total"},
                },
            },
        ]
    )
    return json_util.dumps(data)


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(port=4000, debug=True)
