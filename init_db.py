"""Database initialization script"""
import asyncio
import sys

from app.models import Source, Keyword, init_db, SessionLocal


def initialize_database():
    """Initialize database with tables and default data"""
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")

    db = SessionLocal()
    try:
        # Check if RBC source already exists
        existing_source = db.query(Source).filter(Source.name == "rbc").first()
        if not existing_source:
            print("Adding default RBC source...")
            rbc_source = Source(
                type="website",
                name="rbc",
                url="https://www.rbc.ru/politics/",
                enabled=True
            )
            db.add(rbc_source)
            db.commit()
            print("RBC source added successfully!")
        else:
            print("RBC source already exists, skipping...")

        # Add some default keywords (optional)
        default_keywords = ["технологии", "искусственный интеллект", "наука"]
        for word in default_keywords:
            existing_kw = db.query(Keyword).filter(Keyword.word == word).first()
            if not existing_kw:
                keyword = Keyword(word=word)
                db.add(keyword)
                print(f"Added keyword: {word}")

        db.commit()
        print("\nDatabase initialization completed successfully!")
        print("\nNext steps:")
        print("1. Make sure your .env file is configured with your API keys")
        print("2. Start the services: docker-compose up")
        print("3. Access the API at http://localhost:8000")
        print("4. Check the docs at http://localhost:8000/docs")

    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
