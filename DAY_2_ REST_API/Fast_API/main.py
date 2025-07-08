from fastapi import FastAPI
import json
app = FastAPI()

def load_data():
    with open("data.json", 'r') as file:
        data =json.load(file)

    return data
 
@app.get("/")
def hello():
    return {"message": "patient management system API"}

@app.get('/about')
def about():
    return {'meassage': 'A fully functional APi to manage Your patients Records'}

@app.get('/view')
def view():
    data = load_data()

    return data