import sqlite3
import os
from datetime import datetime, timedelta
import random

DATABASE = os.path.join('instance', 'scholarhub.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def populate_scholarships():
    conn = get_db()
    cursor = conn.cursor()
    
    # List of titles, descriptions, and types to mix and match
    titles = [
        "Future Leaders in Tech", "Women in Engineering Grant", "Global Health Initiative",
        "Creative Arts Preservation", "Minority Business Scholar", "Clean Energy Research Fund",
        "AI Ethics & Safety Grant", "Ocean Conservation Award", "Space Exploration Scholarship",
        "Digital Humanities Fellowship", "Sustainable Agriculture Grant", "Mental Health Advocacy Award",
        "Cybersecurity Defender Scholarship", "Urban Planning Excellence", "Music Theory & Performance",
        "Veterinary Medicine Support", "Early Childhood Education Grant", "Journalism Integrity Award",
        "Quantum Computing Research", "Sports Medicine & Therapy"
    ]
    
    types = ["Merit-Based", "Need-Based", "Research", "Athletic", "Service-Based", "Field-Specific"]
    levels = ["High School", "Undergraduate", "Graduate", "PhD", "All Levels"]
    # NSP style amounts: mostly annual, ranging from 6k to 50k
    amounts = ["₹60,000/year", "₹10,000/year", "₹12,000/year", "₹20,000/year", "₹25,000/year", "₹50,000/year", "₹70,000/year", "₹30,000/month"]
    
    descriptions = [
        "Supporting students who demonstrate exceptional promise in their chosen field.",
        "Aims to remove financial barriers for dedicated students striving for excellence.",
        "Recognizing innovative research proposals that address real-world challenges.",
        "For students who balance academic success with community leadership.",
        "Helping the next generation of professionals achieve their educational goals."
    ]

    new_scholarships = []
    skipped_count = 0
    
    for i in range(len(titles)):
        title = titles[i]
        
        # Check if already exists
        exists = cursor.execute("SELECT 1 FROM scholarships WHERE title = ?", (title,)).fetchone()
        
        if exists:
            skipped_count += 1
            print(f"Skipping duplicate: {title}")
            continue

        amount = random.choice(amounts)
        
        # Random deadline between now and 6 months from now
        days_ahead = random.randint(30, 180)
        deadline = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        type_ = random.choice(types)
        level = random.choice(levels)
        eligibility = f"{level} students, GPA {random.randint(25, 40)/10.0}+"
        desc = random.choice(descriptions) + f" This {type_.lower()} award is open to {level.lower()} students."

        new_scholarships.append((title, amount, deadline, eligibility, desc, type_, level))

    print(f"Adding {len(new_scholarships)} new scholarships (Skipped {skipped_count} duplicates)...")
    
    if new_scholarships:
        cursor.executemany(
            """
            INSERT INTO scholarships (title, amount, deadline, eligibility, description, type, level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            new_scholarships
        )
    else:
        print("No new scholarships to add.")
    
    conn.commit()
    print("Database populated successfully!")
    conn.close()

if __name__ == '__main__':
    populate_scholarships()
