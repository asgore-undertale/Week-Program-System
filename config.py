import os

db_dir = os.path.join(os.getcwd(), 'databases')
class Config:
    SECRET_KEY = 'PIO757UJK24356Lkh134nohvh34vfh124355'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(db_dir, 'UniversityDb.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

POPULATION_SIZE = 20
GENERATIONS_NUM = 100
SELECTION_RATE = 0.2
DUMP_RATE = 0.2
ERASION_RATE = 0.2