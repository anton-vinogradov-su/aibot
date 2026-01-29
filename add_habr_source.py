"""Add Habr.com as news source"""
from app.models import SessionLocal, Source


def add_habr_source():
    """Add Habr news source to database"""
    db = SessionLocal()
    try:
        # Check if already exists
        existing = db.query(Source).filter(Source.name == "habr").first()

        if existing:
            print(f"✓ Habr source already exists (ID: {existing.id})")
            print(f"  URL: {existing.url}")
            print(f"  Enabled: {existing.enabled}")
            return

        # Create new source
        source = Source(
            type="website",
            name="habr",
            url="https://habr.com/ru/news/",
            enabled=True
        )
        db.add(source)
        db.commit()
        db.refresh(source)

        print("=" * 60)
        print("✓ Habr source added successfully!")
        print("=" * 60)
        print(f"  ID: {source.id}")
        print(f"  Name: {source.name}")
        print(f"  URL: {source.url}")
        print(f"  Type: {source.type}")
        print(f"  Enabled: {source.enabled}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    add_habr_source()
