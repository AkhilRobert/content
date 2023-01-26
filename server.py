import html
import math
import os
from typing import Union

from bson import json_util
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)


collection = mongo.db.india  # pyright: ignore

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

population = {
    "Puducherry": 808_117,
    "Lakshadweep": 52_820,
    "West Bengal": 68_077_970,
    "Odisha": 31_659_740,  # Orissa -> Odisha
    "Bihar": 64_531_200,
    "Sikkim": 406_000,
    "Chhattisgarh": 17_615_600,
    "Tamil Nadu": 55_859_300,
    "Madhya Pradesh": 48_566_800,
    "Gujarat": 41_309_580,
    "Goa": 1_170_115,
    "Nagaland": 1_210_492,
    "Manipur": 1_837_900,
    "Arunachal Pradesh": 865_900,
    "Mizoram": 690_963,
    "Tripura": 2_757_205,
    "Daman and Diu": 102_110,
    "Delhi (Ut)": 9_421_311,
    "Haryana": 16_464_600,
    "Chandigarh": 642_374,
    "Himachal Pradesh": 5_170_877,
    "Jammu & Kashmir": 7_718_700,
    "Kerala": 29_098_523,
    "Karnataka": 44_977_200,
    "Dadra and Nagar Haveli": 138_290,
    "Maharashtra": 78_937_190,
    "Assam": 22_414_320,
    "Andhra Pradesh": 66_508_170,
    "Meghalaya": 1_774_778,
    "Punjab": 20_281_971,
    "Rajasthan": 44_005_990,
    "Uttar Pradesh": 132_062_800,
    "Uttarakhand": 7_051_600,
    "Jharkhand": 21_844_550,
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
            {
                "$match": {
                    "State": html.unescape(state),
                    "Type_code": "Professional_Profile",
                },
            },
            {
                "$group": {
                    "_id": {"cause": "$Type"},
                    "count": {"$sum": "$Total"},
                },
            },
        ]
    )
    return json_util.dumps(data)


@app.route("/api/by-age/<string:state>")
def get_by_age_group(state: str):
    data = collection.aggregate(
        [
            {
                "$match": {
                    "State": html.unescape(state),
                },
            },
            {
                "$group": {
                    "_id": {"Age_group": "$Age_group"},
                    "count": {"$sum": "$Total"},
                },
            },
        ]
    )
    return json_util.dumps(data)


@app.route(
    "/api/predict/<string:state>",
    methods=("POST", "GET"),
)
def get_prediction(state: str):

    if request.json is None:
        return {"percentage": 0}

    data = collection.aggregate(
        [
            {
                "$match": {
                    "State": html.unescape(state),
                    "Type": request.json["profession"],
                    "Gender": request.json["gender"],
                },
            },
            {
                "$group": {
                    "_id": "$State",
                    "count": {"$sum": "$Total"},
                },
            },
        ]
    )

    data = list(data)
    count = data[0]["count"]
    return {"percentage": math.ceil((count / population[html.unescape(state)]) * 100)}


if __name__ == "__main__":
    app.run(port=4000)
