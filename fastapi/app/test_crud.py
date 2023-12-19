from db import crud
from db.database import SessionLocal
from data_desing import models, schemas

from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import Depends


def main():
    db = SessionLocal()

    crud.create_scraper_task(db, ["ant", "sri"])


if __name__ == "__main__":
    main()
