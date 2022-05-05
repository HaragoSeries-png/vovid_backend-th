from dbm import dumb
import os
import random
from typing import Type
import json
from requests import get
from flask import Flask, make_response ,request
from flask_mongoengine import MongoEngine
from datetime import date, datetime,timedelta
from flask_cors import CORS
import pickle
import pandas as pd


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
   start_date = args.get("date",default=yesterday.isoformat(),type=str)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = date.fromisoformat(start_date) 
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
   start_date = args.get("date",default=yesterday.isoformat(),type=str)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = date.fromisoformat(start_date) 
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
   start_date = args.get("date",default=yesterday.isoformat(),type=str)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   curr_date = date.fromisoformat(start_date) 
   arr = []
   
   # print(f_date)
   # print(t_date)  
   for i in range(r_date):
      locations_list = json.loads(Daily_report.objects(date=curr_date.isoformat()).only("location","newDeath","newCase","death","totalCase").exclude("id").order_by("location").to_json())
      
      new_deaths = 0
      new_cases = 0
      total_death = 0
      total_cases = 0

      if locations_list:
         new_deaths = sum(i["newDeath"] for i in locations_list)
         new_cases = sum(i["newCase"] for i in locations_list)
         total_death = sum(i["death"] for i in locations_list)
         total_cases = sum(i["totalCase"] for i in locations_list)

      obj = {"date":curr_date.isoformat(),
         "new_deaths":new_deaths,
         "new_cases":new_cases,
         "total_deaths":total_death,
         "total_cases":total_cases
      }  
      arr.append(obj)
      curr_date = curr_date-timedelta(days = 1)


   return json.dumps(arr)

@app.route("/api/daily-data",methods=['get'])
def daily_data():
   args = request.args
   
   today = date.today()
   yesterday = today-timedelta(days=1) 
   r_date = args.get("date", default=yesterday.isoformat(), type=str)
   # t_date = args.get("to", default=yesterday.isoformat(), type=str)
   arr = []
   
   # print(f_date)
   # print(t_date)  

   locations_list = json.loads(Daily_report.objects(date=r_date).only("location","newDeath","newCase","death","totalCase").exclude("id").order_by("location").to_json())
   
   new_deaths = 0
   new_cases = 0
   total_death = 0
   total_cases = 0

   if locations_list:
      new_deaths = sum(i["newDeath"] for i in locations_list)
      new_cases = sum(i["newCase"] for i in locations_list)
      total_death = sum(i["death"] for i in locations_list)
      total_cases = sum(i["totalCase"] for i in locations_list)

   obj = {"date":r_date,
   "new_deaths":new_deaths,
   "new_cases":new_cases,
   "total_deaths":total_death,
   "total_cases":total_cases
   }  
   return json.dumps(obj)

@app.route("/api/month-cases",methods=['get'])
def monthCases():
   today = date.today()

   today_date = today.isoformat()

   print("today date is "+today_date)
   responseData = Daily_report.objects(date=today_date).to_json()
   print(type(responseData))
   return responseData

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

cluster_name = ["new_case_cluster","total_case_cluster","new_death_cluster","total_death_cluster"]
s_c = ["newCase","totalCase","newDeath","death"]

@app.route("/api/cluster")
def cluster():
   req_enum = ["new-cases","total-cases","new-deaths","total-deaths"]
   dataProvince = [
    ["th-kr", 10], 
    ["th-bm", 10], 
    ["th-kn", 0], 
    ["th-kl", 10],
    ["th-kp", 10],
    ["th-kk", 10],
    ["th-ct", 10], 
    ["th-cc", 10],
    ["th-cb", 10], 
    ["th-cn", 10], 
    ["th-cy", 0],
    ["th-cp", 0], 
    ["th-tg",10],
    ["th-tt", 10], 
    ["th-tk", 0], 
    ["th-nn", 10], 
    ["th-np", 10],
    ["th-nf", 0], 
    ["th-nr", 10],
    ["th-nt", 0], 
    ["th-ns", 0], 
    ["th-no", 10],
    ["th-nw", 0],
    ["th-na", 0],
    ["th-bk", 0],
    ["th-br", 10], 
    ["th-pt", 10],
    ["th-pk", 0], 
    ["th-pb", 0], 
    ["th-pi", 0],
    ["th-pa", 10],
    ["th-py", 0],
    ["th-pg", 10],
    ["th-pl", 10], 
    ["th-pc", 10], 
    ["th-ps", 10], 
    ["th-pu", 0], 
    ["th-ms", 0], 
    ["th-md", 0], 
    ["th-yl", 0], 
    ["th-ys", 0], 
    ["th-rn", 0], 
    ["th-ry", 0],
    ["th-rt", 0], 
    ["th-re", 10], 
    ["th-lb", 10], 
    ["th-lg", 0], 
    ["th-ln", 0], 
    ["th-si", 10], 
    ["th-sn", 0],
    ["th-sg", 0], 
    ["th-sa", 10], 
    ["th-sp", 10], 
    ["th-sm", 10], 
    ["th-ss", 10], 
    ["th-sr", 10], 
    ["th-sk", 0], 
    ["th-sb", 10], 
    ["th-sh", 10], 
    ["th-st", 10], 
    ["th-su", 0], 
    ["th-so", 0], 
    ["th-nk", 0],
    ["th-nb", 0], 
    ["th-ac", 0], 
    ["th-un", 0], 
    ["th-ud", 0], 
    ["th-ut", 0], 
    ["th-ur", 0], 
    ["th-at", 10],
    ["th-cr", 0], 
    ["th-cm", 0], 
    ["th-pe", 10], 
    ["th-ph", 10], 
    ["th-le", 0],
    ["th-pr", 0], 
    ["th-mh", 0], 
  ]
   args = request.args
   cluster_r = args.get("cluster",type=str)
   if cluster_r not in req_enum:
      return "wrong. try new-cases, total-cases, new-deaths, total-deaths"

   idx_o = req_enum.index(cluster_r)
   day = date.today()
   while True:
      s= Daily_report.objects(date=day.isoformat()).only("location",s_c[idx_o]).exclude("id").order_by("location")
      if len(s)>0:
         s = s.to_json()
         break
      day = day-timedelta(days=1) 

   filename ='models/'+cluster_name[idx_o]+'_model.pkl'
   model = pickle.load(open(filename,'rb'))

   df = pd.read_json(s)
   y = model.predict(df[{s_c[idx_o]}])
   

   clll = []
   for i in range(len(model.cluster_centers_)):
      obj ={"cluster":i,"value":model.cluster_centers_[i][0]} 
      clll.append(obj)
   newlist = sorted(clll, key=lambda d: d['value']) 
   cld={}
   for i in range(len(newlist)):
      cld[newlist[i]["cluster"]] = i+1

   for i in range(len(dataProvince)):      
      dataProvince[i][1] = cld[y[i]]
   res = {
      "date" : day.isoformat(),
      "dataProvince":dataProvince
   }

   return res

@app.route("/api/ml")
def ml():
   s= Daily_report.objects().only("location","newDeath","newCase","death","totalCase","date").exclude("id").order_by("location").to_json()
   return s



def mm_util(dataFrame):
  for w_index in range(4):
    print(s_c[w_index])
    for i in range(5):
      td = dataFrame[dataFrame[cluster_name[w_index]]==i][s_c[w_index]]
      max = td.max()
      min = td.min()    
      count = len(td)  
      print('cluster '+str(i)+' max = '+str(max)+' min = '+str(min)+" have " + str(count)+" record")
    print("-----------------")

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
class Cluster_data(db.Document):

   date = db.StringField()
   location = db.StringField()
   new_case_cluster = db.StringField()
   total_case_cluster = db.StringField()
   new_death_cluster = db.StringField()
   total_death_cluster = db.StringField()
   created_at = db.DateTimeField(default=datetime.now)


if __name__ == "__main__":
   app.run()
   
