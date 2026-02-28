from sqlalchemy import text
from app.db.database import engine

def main():
    try:
        with engine.connect() as conn:
            value = conn.execute(text("SELECT 1")).scalar()
        print("DB CONNECT OK - SELECT 1 returned:", value)
    except Exception as e:
        print("DB CONNECT FAILED")
        print(type(e).__name__, str(e))

if __name__ == "__main__":
    main()