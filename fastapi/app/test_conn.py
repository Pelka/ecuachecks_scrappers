from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

DATABASE_URL = (
    "mysql+mysqlconnector://ecuachec_user:b%_ihCZd]wNI@23.145.120.242:3306/ecuachec_prueba"
)
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionLocal().execute(text("SELECT 1"))
    print("\n\n----------- Connection successful !")

except Exception as e:
    print(e)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# DeclarativeBase = declarative_base()
