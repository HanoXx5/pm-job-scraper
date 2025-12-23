import sqlite3
import pandas as pd
from pathlib import Path


def create_connection(db_path):

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    return connection


def create_tables(conn):

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            city TEXT,
            country TEXT,
            posted_date DATE,
            employment_type TEXT,
            is_remote BOOLEAN,
            applicant_count INTEGER,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Indizes für schnellere Abfragen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_country ON jobs(country)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)
    """)
    conn.commit()


def insert_jobs(conn, df):

    df_to_insert = df.copy()

    df_to_insert.to_sql(
        'jobs',
        conn,
        if_exists='replace',
        index=False
    )


def run_query(conn, query):
    return pd.read_sql_query(query, conn)



def get_jobs_per_country(conn):

    query = """
        SELECT 
            country,
            COUNT(*) AS job_count
        FROM jobs
        GROUP BY country
        ORDER BY job_count DESC
    """
    return run_query(conn, query)


def get_jobs_per_company(conn, limit=10):

    query = f"""
        SELECT 
            company,
            COUNT(*) AS job_count
        FROM jobs
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT {limit}
    """
    return run_query(conn, query)


def get_posting_trends(conn):

    query = """
        SELECT 
            DATE(posted_date) AS date,
            COUNT(*) AS posts
        FROM jobs
        WHERE posted_date IS NOT NULL
        GROUP BY DATE(posted_date)
        ORDER BY date
    """
    return run_query(conn, query)


def get_remote_ratio(conn):

    query = """
        SELECT 
            SUM(CASE WHEN is_remote = 1 THEN 1 ELSE 0 END) AS remote_count,
            SUM(CASE WHEN is_remote = 0 THEN 1 ELSE 0 END) AS onsite_count,
            COUNT(*) AS total,
            ROUND(SUM(CASE WHEN is_remote = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS remote_percentage
        FROM jobs
    """
    return run_query(conn, query)


def get_jobs_by_city(conn, country=None, limit=15):
    if country:
        query = f"""
            SELECT 
                city,
                COUNT(*) AS job_count
            FROM jobs
            WHERE country = '{country}'
            GROUP BY city
            ORDER BY job_count DESC
            LIMIT {limit}
        """
    else:
        query = f"""
            SELECT 
                city,
                country,
                COUNT(*) AS job_count
            FROM jobs
            GROUP BY city, country
            ORDER BY job_count DESC
            LIMIT {limit}
        """
    return run_query(conn, query)


def search_jobs(conn, keyword):

    query = f"""
        SELECT 
            title,
            company,
            city,
            country,
            posted_date
        FROM jobs
        WHERE LOWER(title) LIKE LOWER('%{keyword}%')
        ORDER BY posted_date DESC
    """
    return run_query(conn, query)


# ============================================================
# HAUPTPROGRAMM
# ============================================================

if __name__ == "__main__":

    conn = create_connection("database/jobs.db")

    # Tabellen erstellen
    create_tables(conn)

    # Beispieldaten einfügen (normalerweise kommt das aus cleaner.py)
    test_df = pd.DataFrame([
        {
            'job_id': '123',
            'title': 'Product Manager Intern',
            'company': 'SIXT',
            'city': 'Munich',
            'country': 'Germany',
            'posted_date': '2025-12-16',
            'employment_type': 'Full-time',
            'is_remote': False,
            'applicant_count': 25,
            'url': 'https://linkedin.com/jobs/123'
        },
        {
            'job_id': '456',
            'title': 'Associate Product Manager',
            'company': 'BMW',
            'city': 'Berlin',
            'country': 'Germany',
            'posted_date': '2025-12-15',
            'employment_type': 'Full-time',
            'is_remote': True,
            'applicant_count': 50,
            'url': 'https://linkedin.com/jobs/456'
        }
    ])

    insert_jobs(conn, test_df)

    # Beispiel-Queries testen
    print("\n📊 Jobs pro Land:")
    print(get_jobs_per_country(conn))

    print("\n🏢 Top Companies:")
    print(get_jobs_per_company(conn))

    print("\n🌍 Remote Ratio:")
    print(get_remote_ratio(conn))

    # Verbindung schließen
    conn.close()
    print("\n🔌 Verbindung geschlossen")