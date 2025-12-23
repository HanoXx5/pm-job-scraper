import pandas as pd
import json


def load_raw_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def extract_country(location_string):
    if pd.isna(location_string) or not location_string:
        return None
    parts = location_string.split(', ')
    return parts[-1]


def extract_city(location_string):
    if pd.isna(location_string) or not location_string:
        return None
    parts = location_string.split(', ')
    return parts[0]


def extract_employment_type(job_insights):
    if isinstance(job_insights, list) and len(job_insights) > 0:
        return job_insights[0]
    return None


def check_is_remote(location, work_type):
    location_remote = False
    work_type_remote = False

    if isinstance(location, str):
        location_remote = 'remote' in location.lower()

    if isinstance(work_type, str):
        work_type_remote = 'remote' in work_type.lower()

    return location_remote or work_type_remote

def check_is_internship(job_title):
    if isinstance(job_title, str):
        return 'intern' in job_title.lower() or 'praktikum' in job_title.lower() or 'praktikant' in job_title.lower() or 'internship' in job_title.lower()
    return False


def clean_jobs(raw_data):
    df = pd.DataFrame(raw_data)

    df['country'] = df['location'].apply(extract_country)
    df['city'] = df['location'].apply(extract_city)
    df['posted_date'] = pd.to_datetime(df['posted_at'], errors='coerce')
    df['employment_type'] = df['job_insights'].apply(extract_employment_type)
    df['is_internship'] = df['job_title'].apply(check_is_internship)
    df['is_remote'] = df.apply(
        lambda row: check_is_remote(row['location'], row.get('work_type')),
        axis=1
    )

    columns_to_keep = [
        'job_id', 'job_title', 'company', 'city', 'country',
        'posted_date', 'employment_type', 'is_internship', 'is_remote',
        'applicant_count', 'job_url'
    ]

    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df_clean = df[existing_columns].copy()

    df_clean = df_clean.rename(columns={
        'job_title': 'title',
        'job_url': 'url'
    })

    df_clean = df_clean.drop_duplicates(subset='job_id')

    return df_clean


def save_cleaned_data(df, filepath):
    df.to_csv(filepath, index=False)

if __name__ == "__main__":
    test_data = [
        {
            "job_id": "4200179442",
            "job_title": "Product Manager2 (m/f/d)",
            "company": "SIXT",
            "location": "Munich, Bavaria, Germany",
            "work_type": None,
            "posted_at": "2025-12-16 11:27:45",
            "job_insights": ["Full-time"],
            "applicant_count": None,
            "job_url": "https://www.linkedin.com/jobs/view/4200179442"
        },
        {
            "job_id": "4200179442",
            "job_title": "Product Manager (m/f/d)",
            "company": "SIXT",
            "location": "Munich, Bavaria, Germany",
            "work_type": None,
            "posted_at": "2025-12-16 11:27:45",
            "job_insights": ["Full-time"],
            "applicant_count": None,
            "job_url": "https://www.linkedin.com/jobs/view/4200179442"
        }
    ]

    df = clean_jobs(test_data)
    print(df.to_string())