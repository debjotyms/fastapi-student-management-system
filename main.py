from fastapi import FastAPI, Path, HTTPException, Query
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

@app.get("/students/{id}")
def student_info(id: str = Path(..., description = "ID of the student in the DB", example = "1")):
    data = load_data()
    if id in data:
        return data[id] 
    raise HTTPException(status_code=404, detail="Student not found")


@app.get("/students_query/query")
def query_check(
    id: str = Query(..., description="This is the students id!", example="1"),
    sort_by: str = Query("name", description="This handle which field is used for sort.", example="name"),
    order: str = Query("asc", description="Accending or Deccending?", example="asc or desc")
):
    data = load_data()

    valid_fields = ["name", "age", "major", "university"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Not a valid field. Try using somethign from here {sort_by}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"Not a valid field. Try using somethign from here {order}")


    sorted_data = sorted(data.values(), key=lambda x:x.get(sort_by,0), reverse=(order=="desc"))

    return sorted_data