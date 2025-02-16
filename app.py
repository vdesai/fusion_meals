from fastapi import FastAPI
from recipe_ai import generate_fusion_recipe

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the AI Fusion Recipe Generator!"}

@app.get("/generate_fusion_recipe/")
def get_fusion_recipe(ingredients: str, cuisine1: str, cuisine2: str, diet: str = "None"):
    """
    API endpoint to generate a fusion recipe with dietary preferences.
    """
    recipe = generate_fusion_recipe(ingredients, cuisine1, cuisine2, diet)  # ✅ Pass diet as argument
    return recipe