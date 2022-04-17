import os
from typing import Type
import json
from requests import get
from flask import Flask, make_response ,request
from flask_mongoengine import MongoEngine
from flask_apscheduler import APScheduler
from datetime import date, datetime,timedelta
from flask_cors import CORS,cross_origin


project_root = os.path.dirname(__file__)
app = Flask(__name__)
CORS(app)

database_name = "vovid-th"
DB_URI = "mongodb+srv://chanon:132231@cluster0.broqy.mongodb.net/vovid-th?authSource=admin&replicaSet=Cluster0-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)




@app.route("/30-day",methods=['POST'])
def timeline():
   url = "https://covid19.ddc.moph.go.th/api/Cases/timeline-cases-by-provinces"
   response = get(url)
   jsonText = json.loads(response.text)
   jsonText.reverse()
   arr = []
   for i in range(78*30):
      content = jsonText[i]
      report  = Daily_report(
         date = content["txn_date"],
         newCase = content["new_case"],
         totalCase = content["total_case"],
         newDeath = content["new_death"],
         death = content["total_death"],
         location = content["province"]
      )
      # arr.append(content["province"])
      # print(content["province"]+" have " + str(arr.count(content["province"])))
      report.save()
   # print(type(response))
   return make_response()

@app.route("/daily",methods=['POST'])
def dailyFunc():
   url = "https://covid19.ddc.moph.go.th/api/Cases/today-cases-by-provinces"
   response = get(url)
   jsonText = json.loads(response.text)
   recent_date = jsonText[0]["txn_date"]
   print(recent_date)
   if Daily_report.objects(date= recent_date):
      print("alredy update")
      print("end daily fuc")
      return "end"
   for i in range(78):
      content = jsonText[i]
      report  = Daily_report(
         date = content["txn_date"],
         newCase = content["new_case"],
         totalCase = content["total_case"],
         newDeath = content["new_death"],
         death = content["total_death"],
         location = content["province"]
      )
      report.save()
      print("save complete")
   return "content"

@app.route("/api/weekly-cases2",methods=['get'])
def todayCases():
   today = date.today()
   curr_date = today
   date_arr = []
   exc_field = ["id","created_at"]
  
   while len(date_arr)<7:
      today_date = curr_date.isoformat()
      print("today date is "+today_date)
      date_arr.append(today_date)
      curr_date = curr_date-timedelta(days=1)
   
   responseData = Daily_report.objects(date__in=date_arr).exclude(*exc_field).distinct(field="location").to_json()
   return responseData

@app.route("/api/weekly-cases",methods=['get'])
def todayCases2():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   args.get("date", default=yesterday.isoformat(), type=str)
   curr_date = yesterday
   date_arr = []
   exc_field = ["id","created_at"]
   data_arr = []
  
   while len(date_arr)<7:
      today_date = curr_date.isoformat()
      date_arr.append(today_date)      
      qData = Daily_report.objects(date=today_date).exclude(*exc_field).order_by("location").to_json()
      reData ={"date":today_date,"result":json.loads(qData)}
      curr_date = curr_date-timedelta(days=1)   
      data_arr.append(reData)

   return json.dumps(data_arr)

@app.route("/api/cases",methods=['get'])
def Cases2():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   qdate = args.get("date", default=yesterday.isoformat(), type=str)
   curr_date = yesterday
   date_arr = []
   exc_field = ["id","created_at"]
   data_arr = []
  
     
   qData = Daily_report.objects(date=qdate).exclude(*exc_field).order_by("location").to_json()
   reData ={"date":qdate,"result":json.loads(qData)}  
   data_arr.append(reData)

   return json.dumps(data_arr)

@app.route("/api/sum-of-cases-range",methods=['get'])
def sumnOfCases():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   f_date = args.get("from", default=(yesterday-timedelta(days=7)).isoformat(), type=str)
   t_date = args.get("to", default=yesterday.isoformat(), type=str)
   arr = []
   
   print(f_date)
   print(t_date)  
   # locations = Daily_report.objects(date=yesterday.isoformat()).only("location").exclude("id").order_by("location").to_json()
   from_data = Daily_report.objects(date=f_date).exclude("id").order_by("location").to_json()
   to_data =Daily_report.objects(date=t_date).exclude("id").order_by("location").to_json()

   for f,t in zip(json.loads(from_data),json.loads(to_data)) :
      print("location : "+f["location"])
      obj = {"location":f["location"],"sum-case":t["totalCase"]-f["totalCase"]}
      arr.append(obj)
   return json.dumps(arr)

@app.route("/api/sum-of-cases",methods=['get'])
def sumnOfCases2():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   r_date = args.get("range", default=7, type=int)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = yesterday
   arr = []
   
   # print(f_date)
   # print(t_date)  
   for i in range(r_date):
      locations_list = json.loads(Daily_report.objects(date=curr_date.isoformat()).only("location","newCase").exclude("id").order_by("location").to_json())
      
      sum_of_cases = 0

      if locations_list:
         sum_of_cases = sum(i["newCase"] for i in locations_list)

      obj = {"date":curr_date.isoformat(),"sum_of_cases":sum_of_cases}  
      arr.append(obj)
      curr_date = curr_date-timedelta(days = 1)


   return json.dumps(arr)

@app.route("/api/sum-of-deaths",methods=['get'])
def sumnOfDeath():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   r_date = args.get("range", default=7, type=int)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = yesterday
   arr = []
   
   # print(f_date)
   # print(t_date)  
   for i in range(r_date):
      locations_list = json.loads(Daily_report.objects(date=curr_date.isoformat()).only("location","newDeath").exclude("id").order_by("location").to_json())
      
      sum_of_deaths = 0

      if locations_list:
         sum_of_deaths = sum(i["newDeath"] for i in locations_list)

      obj = {"date":curr_date.isoformat(),"sum_of_death":sum_of_deaths}  
      arr.append(obj)
      curr_date = curr_date-timedelta(days = 1)


   return json.dumps(arr)

@app.route("/api/sum-of",methods=['get'])
def sumnOf():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   r_date = args.get("range", default=7, type=int)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = yesterday
   arr = []
   
   # print(f_date)
   # print(t_date)  
   for i in range(r_date):
      locations_list = json.loads(Daily_report.objects(date=curr_date.isoformat()).only("location","newDeath","newCase").exclude("id").order_by("location").to_json())
      
      sum_of_deaths = 0
      sum_of_cases = 0

      if locations_list:
         sum_of_deaths = sum(i["newDeath"] for i in locations_list)
         sum_of_cases = sum(i["newCase"] for i in locations_list)

      obj = {"date":curr_date.isoformat(),"sum_of_death":sum_of_deaths,"sum_of_cases":sum_of_cases}  
      arr.append(obj)
      curr_date = curr_date-timedelta(days = 1)


   return json.dumps(arr)



@app.route("/api/month-cases",methods=['get'])
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

   date = db.StringField()
   newCase = db.IntField()
   totalCase = db.IntField()
   newDeath = db.IntField()
   death = db.IntField()
   location = db.StringField()
   created_at = db.DateTimeField(default=datetime.now)

   def toJson(self):
      return {
         "date":self.date,
         "death":self.death,
         "deathNew":self.deathNew
      }


if __name__ == "__main__":
   app.run()
   
