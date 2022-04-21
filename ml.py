from sklearn.cluster import KMeans
from app import Daily_report

r_date = "2022-04-17"

s= Daily_report.objects(date=r_date).only("location","newDeath","newCase","death","totalCase","date").exclude("id").order_by("location").to_json()
print(s)