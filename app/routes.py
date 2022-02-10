from app import app
import json
# from flask import jsonify
import requests
from .models.report_data_model import DailyReport

@app.route('/')
@app.route('/test')
def index():
    url = "https://covid19.ddc.moph.go.th/api/Cases/today-cases-by-provinces"
    x = requests.get(url)
    xJson = json.loads(x.text)
    list = []
    for i in xJson:
        report = DailyReport(i)
        print(report.toString())
        list.append(report.toString())

    print(xJson[0]["new_case"])
    return json.dumps(list)