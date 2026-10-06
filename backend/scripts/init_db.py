from app.core.database import create_tables


def main() -> None:
    create_tables()
    print("Database tables created.")


if __name__ == "__main__":
    main()
