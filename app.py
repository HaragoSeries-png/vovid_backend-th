from email.policy import default
import os
from typing import Type
import json
from urllib import response
import requests
from requests import get
from flask import Flask, make_response 
from flask_mongoengine import MongoEngine
from flask_apscheduler import APScheduler
from datetime import date, datetime
from apscheduler.schedulers.blocking import BlockingScheduler


project_root = os.path.dirname(__file__)
app = Flask(__name__)

database_name = "vovid-th"
DB_URI = "mongodb+srv://chanon:132231@cluster0.broqy.mongodb.net/vovid-th?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)

scheduler = BlockingScheduler()


@app.route("/30-day",methods=['POST'])
def timeline():
   url = "https://covid19.ddc.moph.go.th/api/Cases/timeline-cases-by-provinces"
   response = get(url)
   jsonText = json.loads(response.text)
   jsonText.reverse()
   arr = []
   for i in range(78*7):
      content = jsonText[i]
      report  = Daily_report(
         date = content["txn_date"],
         newCase = content["new_case"],
         totalCase = content["total_case"],
         newDeath = content["new_death"],
         death = content["total_death"],
         province = content["province"]
      )
      # arr.append(content["province"])
      # print(content["province"]+" have " + str(arr.count(content["province"])))
      report.save()
   # print(type(response))
   return make_response()

@app.route("/daily",methods=['POST'])
@scheduler.scheduled_job('cron', id='fetch_daily', day='*',hour='9', minute='0')
def dailyFunc():
   url = "https://covid19.ddc.moph.go.th/api/Cases/today-cases-by-provinces"
   response = get(url)
   jsonText = json.loads(response.text)
   for i in range(78):
      content = jsonText[i]
      report  = Daily_report(
         date = content["txn_date"],
         newCase = content["new_case"],
         totalCase = content["total_case"],
         newDeath = content["new_death"],
         death = content["total_death"],
         province = content["province"]
      )
      report.save()
   return "content"

@app.route("/api/today-cases",methods=['get'])
def todayCases():
   today = date.today()

   today_date = today.isoformat()

   print("today date is "+today_date)
   responseData = Daily_report.objects(date=today_date).to_json()
   print(type(responseData))
   return responseData

@app.route("/api/today-cases",methods=['get'])
def monthCases():
   today = date.today()

   today_date = today.isoformat()

   print("today date is "+today_date)
   responseData = Daily_report.objects(date=today_date).to_json()
   print(type(responseData))
   return responseData

def ss():
   print("cron job activate")

@app.route("/2")
def show2():
   url = "https://raw.github.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.json"
   response = get(url)
   xJson = json.loads(response.text)
   JsonKey = [
      "location",
      "new_cases",
      "total_cases",
      "new_deaths",
      "total_deaths",
      "last_updateed_date"
   ]
   reList = []
   for key,value in xJson.items():
      print(key) 
      print(value["location"])
      re = {
         "location":value["location"],
         "new_cases":value["new_cases"],
         "total_cases":value["total_cases"],
         "new_deaths":value["new_deaths"],
         "total_deaths":value["total_deaths"],
         "last_updated_date":value["last_updated_date"]
      }
      reList.append(re)
   # report = Daily_report(report_id = 1, date = "20-10",death=10,deathNew=50)
   # print(type(report))
   # report.save()
   return json.dumps(reList)


class Daily_report(db.Document):

   report_id = db.IntField()

   date = db.StringField()
   newCase = db.IntField()
   totalCase = db.IntField()
   newDeath = db.IntField()
   death = db.IntField()
   province = db.StringField()
   create_at = db.DateTimeField(default=datetime.now)

   def toJson(self):
      return {
         "date":self.date,
         "death":self.death,
         "deathNew":self.deathNew
      }


if __name__ == "__main__":
   app.run()
