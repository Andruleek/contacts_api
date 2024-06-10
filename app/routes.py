from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database configuration
engine = create_engine("sqlite:///contacts.db")
DBSession(app, engine)
engine = create_engine(DB_URL)
Base = declarative_base()

# Define the Contact model
class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    birthday = Column(Date)

# Create the database tables
Base.metadata.create_all(engine)

# Create a session maker
Session = sessionmaker(bind=engine)

# Define the Contact schema
class ContactSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: str

# Define the routes
from fastapi import APIRouter, status, HTTPException
from .models import Contact
from .schemas import ContactSchema, ContactUpdateSchema
from sqlalchemy.orm import Session
from fastapi import Depends
from .database import get_db

contact_router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
    responses={404: {"description": "Not found"}}
)

@contact_router.post("/", status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactSchema, db: Session = Depends(get_db)):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@contact_router.get("/")
def read_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts

@contact_router.get("/{contact_id}")
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@contact_router.put("/{contact_id}")
def update_contact(contact_id: int, contact: ContactUpdateSchema, db: Session = Depends(get_db)):
    contact_to_update = db.query(Contact).get(contact_id)
    if not contact_to_update:
        raise HTTPException(status_code=404, detail="Contact not found")
    for var, value in vars(contact).items():
        setattr(contact_to_update, var, value) if value else None
    db.add(contact_to_update)
    db.commit()
    db.refresh(contact_to_update)
    return contact_to_update

@contact_router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact_to_delete = db.query(Contact).get(contact_id)
    if not contact_to_delete:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact_to_delete)
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import get_db

router = APIRouter()

@router.get("/contacts/search/", response_model=list[schemas.Contact])
def search_contacts(
    query: str,
    db: Session = Depends(get_db),
):
    contacts = crud.search_contacts(db, query)
    return contacts

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi_sqlalchemy import DBSession
from sqlalchemy import create_engine
from models import Contact

app = FastAPI()

class ContactSchema:
    def __init__(self):
        self.fields = ("id", "name", "birthday")

@app.get("/contacts")
async def get_contacts():
    contacts = Contact.query.all()
    return JSONResponse(content=ContactSchema().dump(contacts), media_type="application/json")

@app.get("/contacts/birthdays")
async def get_birthdays():
    today = datetime.date.today()
    next_seven_days = (today + datetime.timedelta(days=7)).date()
    birthdays = Contact.query.filter(Contact.birthday.between(today, next_seven_days)).all()
    return JSONResponse(content=ContactSchema().dump(birthdays), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)