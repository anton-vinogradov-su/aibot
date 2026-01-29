"""Add all RBC rubrics as sources"""
from app.models import SessionLocal, Source


def add_all_rubrics():
    """Add all RBC rubrics to database"""
    db = SessionLocal()
    try:
        # List of all RBC rubrics
        rubrics = [
            ("politics", "Политика", "https://www.rbc.ru/rubric/politics"),
            ("economics", "Экономика", "https://www.rbc.ru/rubric/economics"),
            ("business", "Бизнес", "https://www.rbc.ru/rubric/business"),
            ("finances", "Финансы", "https://www.rbc.ru/rubric/finances"),
            ("technology_and_media", "Технологии и медиа", "https://www.rbc.ru/rubric/technology_and_media"),
            ("society", "Общество", "https://www.rbc.ru/rubric/society"),
            ("own_business", "Свое дело", "https://www.rbc.ru/rubric/own_business"),
            ("sport", "Спорт", "https://www.rbc.ru/sport"),
            ("incident", "Происшествия", "https://www.rbc.ru/rbcfreenews"),
        ]

        print("Adding RBC rubrics as sources...\n")

        # Delete old rbc source
        old_source = db.query(Source).filter(Source.name == "rbc").first()
        if old_source:
            db.delete(old_source)
            db.commit()
            print(f"✓ Deleted old source: rbc\n")

        added_count = 0
        skipped_count = 0

        for code, title, url in rubrics:
            source_name = f"rbc_{code}"

            # Check if already exists
            existing = db.query(Source).filter(Source.name == source_name).first()

            if existing:
                print(f"⊘ Skipped (exists): {title} ({source_name})")
                skipped_count += 1
                continue

            # Create new source
            source = Source(
                type="website",
                name=source_name,
                url=url,
                enabled=True
            )
            db.add(source)
            print(f"✓ Added: {title} ({source_name})")
            added_count += 1

        db.commit()

        print(f"\n{'=' * 60}")
        print(f"Summary:")
        print(f"  Added: {added_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total sources: {db.query(Source).count()}")
        print(f"{'=' * 60}")

    finally:
        db.close()


if __name__ == "__main__":
    add_all_rubrics()
