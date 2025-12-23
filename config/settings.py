import os

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID", "KE649tixwpoRnZtJJ")
DATABASE_PATH = "database/jobs.db"

# Search configuration
SEARCH_QUERIES = [
    # Product Management roles
    "product manager intern",
    "product manager praktikum",
    "product manager werkstudent",
    "junior product manager",
    "associate product manager",
    "product owner intern",
    "product owner praktikum",
    # Technical Sales roles
    "technical sales intern",
    "sales engineer intern",
    "pre-sales intern",
    "solutions engineer intern",
    "business development intern",
    "sales praktikum",
    "vertrieb praktikum",
]

SEARCH_LOCATION = "Germany"
SEARCH_LIMIT = 500  # Jobs per weekly scrape