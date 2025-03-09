import os

db_dir = os.path.join(os.getcwd(), "databases")
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Configuration settings
class Config:
    SECRET_KEY = 'PIO757UJK24356Lkh134nohvh34vfh124355'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(db_dir, 'UniversityDb.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False