from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

app = FastAPI()

# База даних конфігурація
DB_URL = 'sqlite+aiosqlite:///contacts.db'
engine = create_async_engine(DB_URL)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Визначте схему
class ContactSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: str

    class Config:
        orm_mode = True

# Визначити маршрути
@app.get("/contacts")
async def get_contacts():
    async with AsyncSessionLocal() as session:
        contacts = await session.execute(select(Contact))
        return JSONResponse(content=[ContactSchema.from_orm(contact).dict() for contact in contacts.scalars().all()], media_type="application/json")

@app.post("/contacts")
async def create_contact(contact: ContactSchema):
    async with AsyncSessionLocal() as session:
        new_contact = Contact(**contact.dict())
        session.add(new_contact)
        await session.commit()
        await session.refresh(new_contact)
        return JSONResponse(content=ContactSchema.from_orm(new_contact).dict(), media_type="application/json")

@app.get("/contacts/{contact_id}")
async def get_contact(contact_id: int):
    async with AsyncSessionLocal() as session:
        contact = await session.execute(select(Contact).where(Contact.id == contact_id))
        contact = contact.scalars().first()
        if contact is None:
            raise HTTPException(status_code=404, detail="Контакт не знайдено")
        return JSONResponse(content=ContactSchema.from_orm(contact).dict(), media_type="application/json")

@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: ContactSchema):
    async with AsyncSessionLocal() as session:
        contact_to_update = await session.execute(select(Contact).where(Contact.id == contact_id))
        contact_to_update = contact_to_update.scalars().first()
        if contact_to_update is None:
            raise HTTPException(status_code=404, detail="Контакт не знайдено")
        contact_to_update.first_name = contact.first_name
        contact_to_update.last_name = contact.last_name
        contact_to_update.email = contact.email
        contact_to_update.phone_number = contact.phone_number
        contact_to_update.birthday = contact.birthday
        await session.commit()
        return JSONResponse(content=ContactSchema.from_orm(contact_to_update).dict(), media_type="application/json")

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    async with AsyncSessionLocal() as session:
        contact_to_delete = await session.execute(select(Contact).where(Contact.id == contact_id))
        contact_to_delete = contact_to_delete.scalars().first()
        if contact_to_delete is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        await session.delete(contact_to_delete)
        await session.commit()
        return JSONResponse(content={"message": "Contact deleted"}, media_type="application/json")