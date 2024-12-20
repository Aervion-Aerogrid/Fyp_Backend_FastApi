from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from models import Admin  # Assuming Admin is your SQLAlchemy model

# Define Pydantic models
class AdminCreate(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True  # Enables compatibility with ORM
        
        # Pydantic model for admin login
class AdminLogin(BaseModel):
    username: str
    password: str

def create_admin(db: Session, admin: AdminCreate):
    query = text("SELECT * FROM admins WHERE username = :username")
    result = db.execute(query, {"username": admin.username}).fetchone()

    if result:
        return None  # Username already exists

    insert_query = text("INSERT INTO admins (username, password) VALUES (:username, :password)")
    db.execute(insert_query, {"username": admin.username, "password": admin.password})
    db.commit()
    
    return {"message": "Admin created successfully"}

def get_admin_by_username(db: Session, username: str) -> AdminResponse:
    query = text("SELECT id, username, password FROM admins WHERE username = :username")  # Fetch the password
    result = db.execute(query, {"username": username}).fetchone()

    if result is None:
        return None  # Admin not found

    return AdminResponse(id=result[0], username=result[1], password=result[2])  # Include password in response



# New function for admin login logic
def login_admin_logic(db: Session, admin: AdminLogin) -> AdminResponse:
    print(f"Login attempt for username: {admin.username}")
    
    # Fetch admin details by username
    query = text("SELECT id, username, password FROM admins WHERE username = :username")
    result = db.execute(query, {"username": admin.username}).fetchone()
    
    if result is None:
        print("Admin not found in the database")
        raise HTTPException(status_code=404, detail="Admin not found")

    # Extract the stored password
    stored_password = result[2]  # Assuming password is the third column in your result
    print(f"Stored password hash: {stored_password}, Provided password: {admin.password}")

    # Compare the provided password with the stored hashed password
    if not verify_admin_password(stored_password, admin.password):
        print("Invalid password provided")
        raise HTTPException(status_code=403, detail="Invalid password")

    # Return admin details if the password is correct
    return AdminResponse(id=result[0], username=result[1])