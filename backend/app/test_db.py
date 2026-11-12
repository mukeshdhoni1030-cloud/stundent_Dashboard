
from sqlalchemy import text
from app.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("DATABASE CONNECTION SUCCESSFUL!")
        print("Test result:", result.scalar())

except Exception as error:
    print("DATABASE CONNECTION FAILED!")
    print("Error:", error)
