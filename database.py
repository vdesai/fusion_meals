import sqlite3
import json

DB_NAME = "meal_plans.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            diet_type TEXT NOT NULL,
            preferences TEXT,
            meal_plan TEXT NOT NULL,
            grocery_list TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Save meal plan
def save_meal_plan(diet_type, preferences, meal_plan, grocery_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meal_plans (diet_type, preferences, meal_plan, grocery_list)
        VALUES (?, ?, ?, ?)
    ''', (diet_type, preferences, json.dumps(meal_plan), json.dumps(grocery_list)))
    conn.commit()
    conn.close()

# Retrieve latest meal plan
def get_latest_meal_plan():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT diet_type, preferences, meal_plan, grocery_list FROM meal_plans ORDER BY created_at DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "diet_type": result[0],
            "preferences": result[1],
            "meal_plan": json.loads(result[2]),
            "grocery_list": json.loads(result[3])
        }
    return None

# Initialize database
init_db()
