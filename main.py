from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, computed_field, Field
from typing import Annotated, Optional

app = FastAPI()

def load_data():
    with open('students.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('students.json', 'w') as f:
        json.dump(data, f)

class Student(BaseModel):
    id: Annotated[str, Field(..., description="This is the ID of the student", title="Student ID", example="S008")]
    name: Annotated[str, Field(..., description="This is the name of the student", title="Student Name", example="Debjoty Mitra")]
    age: Annotated[int, Field(..., description="This is the age of the student", title="Student Age", example=24)]
    major: Annotated[str, Field(..., description="This is the major of the student", title="Student Major", example="Computer Science")]
    university: Annotated[str, Field(..., description="This is the university of the student", title="Student University", example="MIT")]
    height: Annotated[float, Field(..., description="This is the height of the student in m", title="Student Height", example=1.73)]
    weight: Annotated[float, Field(..., description="This is the weight of the student in kg", title="Student Weight", example=70.2)]
    gender: Annotated[str, Field(..., description="This is the gender of the student", title="Student Gender", example="Male")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / (self.height ** 2)
        return round(bmi, 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "underweight"
        elif self.bmi > 25:
            return "overweight"
        else:
            return "normal"

class StudentUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    major: Annotated[Optional[str], Field(default=None)]
    university: Annotated[Optional[str], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None)]
    weight: Annotated[Optional[float], Field(default=None)]
    gender: Annotated[Optional[str], Field(default=None)]

@app.get('/')
def root():
    return "Welcome to FastAPI Student Management System"

# qwery parameter example
@app.get('/test')
def root(
    name:int = Query(..., example = 15, gt=18, lt=63,   description="This is a simple test for the query parameter", title="Test Query"),
    roll:int = Query(..., example = 20)
):
    return f"name: {name} roll: {roll}"

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

@app.post('/create')
def create_student(student: Student):
    data = load_data()
    if student.id in data:
        return HTTPException(status_code=400, detail="student already exists!")
    data[student.id] = student.model_dump(exclude="id")

    save_data(data)
    return JSONResponse(status_code=201, content={'message':'student created successfully'})

@app.put('/update/{id}')
def update_student(id: str, studentupdate: StudentUpdate):
    data = load_data()

    if id not in data:
        raise HTTPException(status_code=404, detail="Student not found!")

    update_data = studentupdate.model_dump(exclude_unset=True) # only dumps the given fields
    
    for key,value in update_data.items():
        data[id][key] = value

    final_data = data[id]
    final_data["id"] = id
    final_data = Student(**final_data)

    data[id] = final_data.model_dump(exclude={"id"})

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'Student information succefully updated'})

@app.delete('/delete/{id}')
def delete_student(id: str):
    data = load_data()
    if id not in data:
        raise HTTPException(status_code=404, detail="Student not found!")
    
    del data[id]

    save_data(data)