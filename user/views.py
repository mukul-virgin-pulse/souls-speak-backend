from model import User
from schema import UserCreate
from db.mongodb import user_collection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(email: str):
    user = await user_collection.find_one({"email": email})
    if user:
        return User(**user)

async def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.model
    user_dict["hashed_password"] = hashed_password
    new_user = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return User(**created_user)
