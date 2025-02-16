import openai

# OpenAI API Key
OPENAI_API_KEY = "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"

def generate_fusion_recipe(ingredients, cuisine1, cuisine2, diet="None"):
    """
    Generates a fusion recipe based on ingredients, cuisines, and dietary preference.
    Includes grocery list, nutritional breakdown, and a health score.
    """

    diet_instructions = {
        "Diabetes-Friendly": "Avoid sugar, white rice, potatoes, and refined flour. Suggest healthy alternatives.",
        "Low-Carb": "Limit high-carb ingredients like potatoes and rice. Suggest protein-rich alternatives.",
        "High-Protein": "Ensure the recipe includes high-protein ingredients like lentils, tofu, and beans.",
        "Vegan": "Exclude all animal products, including dairy and eggs. Use plant-based alternatives.",
        "Gluten-Free": "Avoid wheat, barley, and rye. Suggest gluten-free grains like quinoa or rice.",
        "Keto": "Ensure very low carbs, moderate protein, and high healthy fats like avocados and nuts.",
        "Heart-Healthy": "Use heart-friendly ingredients like olive oil, nuts, leafy greens, and avoid processed foods.",
        "None": "No dietary restrictions."
    }

    diet_instruction = diet_instructions.get(diet, "No dietary restrictions.")

    prompt = f"""
    You are an AI chef specializing in fusion cuisine.

    User has requested a fusion dish combining **{cuisine1} and {cuisine2}** cuisine.
    Available ingredients: {ingredients}.
    
    **Dietary Preference:** {diet_instruction}

    Generate:
    - A **creative and unique recipe name**
    - **List of categorized grocery items** (Vegetables, Proteins, Spices, Other)
    - **Step-by-step cooking instructions**
    - **Estimated cooking time**
    - **Calories per serving**
    - **Macronutrients (Protein, Carbs, Fats per serving)**
    - **Health Score (A, B, C - based on nutritional content)**

    Ensure the recipe follows the dietary preference. If ingredients are missing, suggest alternatives.
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        recipe_text = response.choices[0].message.content.strip()

        if not recipe_text or "recipe not found" in recipe_text.lower():
            return {"recipe": "⚠️ AI couldn't generate a recipe. Try modifying the ingredients!"}

        return {"recipe": recipe_text}

    except Exception as e:
        return {"recipe": f"❌ Error: {str(e)}"}

# Example usage
if __name__ == "__main__":
    user_ingredients = input("Enter ingredients: ")
    cuisine1 = input("Enter first cuisine (e.g., Indian): ")
    cuisine2 = input("Enter second cuisine (e.g., Mexican): ")
    recipe = generate_fusion_recipe(user_ingredients, cuisine1, cuisine2)
    print("\nAI Fusion Recipe Suggestion:\n", recipe)
