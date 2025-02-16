import openai
import re
import json
from database import save_meal_plan  # Import DB function

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Retrieve API keys securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_meal_plan(diet="Balanced", preferences=""):
    """
    Generates a 7-day AI meal plan based on diet and preferences.
    """
    diet_instructions = {
        "Balanced": "Include a mix of proteins, carbohydrates, and healthy fats.",
        "Diabetes-Friendly": "Limit sugar, refined carbs, and high-GI foods. Focus on fiber and proteins.",
        "Low-Carb": "Minimize carbohydrate intake and increase healthy fats and proteins.",
        "High-Protein": "Ensure each meal has a high-protein source like lentils, tofu, or lean meats.",
        "Vegan": "Exclude all animal products and suggest plant-based protein sources.",
        "Gluten-Free": "Avoid wheat, barley, and rye. Suggest gluten-free grains like quinoa or rice.",
        "Keto": "Ensure very low carbs, moderate protein, and high healthy fats like avocados and nuts.",
        "Heart-Healthy": "Use heart-friendly ingredients like olive oil, nuts, leafy greens, and avoid processed foods."
    }

    diet_instruction = diet_instructions.get(diet, "Provide a general healthy meal plan.")

    prompt = f"""
    You are a top AI nutritionist.

    User has requested a **7-day meal plan** for a **{diet} diet**.
    Preferences: {preferences}
    
    Generate:
    - **Breakfast, Lunch, and Dinner** for 7 days
    - **Grocery list** with categorized items
    - **Nutritional breakdown** (Calories, Protein, Carbs, Fats) per meal
    - Ensure the plan is diverse and easy to cook.
    
    Respond in a structured way.
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        meal_plan_text = response.choices[0].message.content.strip()

        # Extract grocery list
        grocery_list = extract_grocery_list(meal_plan_text)

        # ✅ Save the meal plan & grocery list in the database
        save_meal_plan(diet, preferences, meal_plan_text, grocery_list)

        return {"meal_plan": meal_plan_text, "grocery_list": grocery_list}

    except Exception as e:
        return {"meal_plan": f"❌ Error: {str(e)}", "grocery_list": {}}

import re

def extract_grocery_list(meal_plan_data):
    """Extracts a structured grocery list from the AI-generated meal plan."""
    grocery_list = {}

    # Ensure meal_plan_data is a dictionary and get meal_plan text
    if isinstance(meal_plan_data, dict):
        meal_plan_text = meal_plan_data.get("meal_plan", "")
    elif isinstance(meal_plan_data, str):
        meal_plan_text = meal_plan_data
    else:
        return {}

    if not isinstance(meal_plan_text, str):  # Ensure it's a string before regex processing
        print("DEBUG: Error - meal_plan_text is not a string!", type(meal_plan_text))
        return {}

    # 🔹 Debugging: Print the full extracted meal plan
    print("DEBUG: Meal Plan Text\n", meal_plan_text)

    # 🔹 Match the **Grocery List:** section using a more flexible approach
    grocery_section_match = re.search(
        r"\*\*\s*Grocery List\s*\*\*[:\s]*([\s\S]+?)(?=\n\n\*\*|\n\nNutritional|$)",
        meal_plan_text,
        re.IGNORECASE
    )

    if grocery_section_match:
        grocery_section = grocery_section_match.group(1).strip()
        print("DEBUG: Extracted Grocery Section\n", grocery_section)  # 🔹 Debugging

        # 🔹 Match category headers and their corresponding items
        category_matches = re.findall(r"\*\*\s*(.+?)\s*\*\*[:\s]*([\s\S]+?)(?=\n\*\*|\Z)", grocery_section)

        if category_matches:
            for category, items in category_matches:
                # 🔹 Process item lists: remove extra spaces, dashes, and split by commas/newlines
                item_list = [item.strip("-• ").strip() for item in re.split(r"[\n,]", items) if item.strip()]
                grocery_list[category.strip()] = item_list
        else:
            # 🔹 If no categories are found, extract items as a single list
            item_list = [item.strip("-• ").strip() for item in grocery_section.split("\n") if item.strip()]
            if item_list:
                grocery_list["General Items"] = item_list  # 🔹 Fallback category

    else:
        print("DEBUG: Grocery section NOT found!")  # 🔹 Debugging

    return grocery_list if grocery_list else {}
