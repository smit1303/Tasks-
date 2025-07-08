from fastapi import FastAPI, HTTPException, UploadFile, File, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr
from typing import Dict, List, Optional, Annotated
import json
import os

app = FastAPI()

DATA_FILE = "Data_.json"

# Load data from the file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save data to the file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Pydantic model for adding a contact
class Contact(BaseModel):
    id: int = Field(..., gt=0)
    name: constr(strip_whitespace=True, min_length=1)
    phone: constr(strip_whitespace=True, min_length=1)

# Pydantic model for updating a contact
class ContactUpdate(BaseModel):
    phone: constr(strip_whitespace=True, min_length=1)

# Home route
@app.get("/")
def hello():
    return {"message": "Contact management API"}

# About route
@app.get("/about")
def about():
    return {"message": "A fully functional API to manage your contacts"}

# View all contact data from file
@app.get("/view")
def view():
    data = load_data()
    return data

# Get all contacts
@app.get("/contacts")
def get_all_contacts():
    data = load_data()
    return data

# Get contact by ID
@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int = Path(..., description= 'The ID of the contact to retrive', example='1')):
    data = load_data()
    if str(contact_id) not in data:
        raise HTTPException(status_code=404, detail="Contact not found")
    return data[str(contact_id)]

@app.get('/sort')
def sort_contacts(sort_by: str  =  Query(..., description="Field to sort by name"), order: str = Query("asc", description="Order of sorting: 'asc' or 'desc'")):
   
    valid_sort_fields = ['name', 'phone']

    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_sort_fields)}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'")
    
    data = load_data()

    sorted_order = True if order == "desc" else False

    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=sorted_order)

    return sorted_data

# Add a new contact
@app.post("/contacts")
def add_contact(contact: Contact):
    data = load_data()
    if str(contact.id) in data:
        raise HTTPException(status_code=400, detail="Contact ID already exists")
    data[str(contact.id)] = {"name": contact.name, "phone": contact.phone}
    save_data(data)
    return {"message": "Contact added", "contact": data[str(contact.id)]}

# Update contact's phone number
@app.put("/contacts/{contact_id}")
def update_contact(contact_id: int, update: ContactUpdate):
    data = load_data()
    if str(contact_id) not in data:
        raise HTTPException(status_code=404, detail="Contact not found")
    data[str(contact_id)]["phone"] = update.phone
    save_data(data)
    return {"message": "Contact updated", "contact": data[str(contact_id)]}

# Delete a contact
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int):
    data = load_data()
    if str(contact_id) not in data:
        raise HTTPException(status_code=404, detail="Contact not found")
    deleted = data.pop(str(contact_id))
    save_data(data)
    return {"message": f"Contact '{deleted['name']}' deleted"}

# Upload an image and return metadata
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    size_kb = round(len(contents) / 1024, 2)
    return JSONResponse(content={
        "filename": file.filename,
        "size_kb": size_kb,
        "mime_type": file.content_type
    })
