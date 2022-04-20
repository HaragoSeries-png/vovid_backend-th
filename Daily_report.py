import app
from flask_mongoengine import MongoEngine


db = MongoEngine()
db.init_app(app)

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