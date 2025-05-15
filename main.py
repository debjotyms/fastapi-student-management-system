from fastapi import FastAPI
import json

app = FastAPI()

def load_data():
    with open('students.json', 'r') as f:
        data = json.load(f)
    return data

@app.get('/')
def root():
    return "Welcome to FastAPI Student Management System"

@app.get('/students')
def root():
    data = load_data()
    return data