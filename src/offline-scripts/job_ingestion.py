import os
import json
from pymongo import MongoClient


client = MongoClient("mongodb+srv://subodh:root@sub-cluster.wo2nvbg.mongodb.net/")
db = client["startup-init"]
collection = db["jobs"]

def read_json_files(directory: str):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as file:
                file_data = json.load(file)
                for key, value in file_data.items():
                    data.extend(value)
    return data

def load_jobs_to_mongodb(directory: str):
    try:
        jobs_data = read_json_files(directory)
        if not jobs_data:
            print("No job data found in the specified directory")
            return
        
        collection.insert_many(jobs_data)
        print("Jobs data successfully loaded into MongoDB")
    except Exception as e:
        print(f"An error occurred: {e}")

directory = "resources/todb"

load_jobs_to_mongodb(directory)
