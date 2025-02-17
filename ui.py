import streamlit as st
import requests
import openai
import googlemaps  
import json
from meal_planner import generate_meal_plan, extract_grocery_list
from database import save_meal_plan, get_latest_meal_plan

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Retrieve API keys securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


AMAZON_AFFILIATE_TAG = "desaivinit-20"  # ✅ Amazon Associates Tag

# Initialize APIs
client = openai.OpenAI(api_key=OPENAI_API_KEY)
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Generate Amazon Fresh Search URL
def amazon_search_url(item):
    search_term = item.replace(" ", "+")
    return f"https://www.amazon.com/s?k={search_term}&tag={AMAZON_AFFILIATE_TAG}"

# Custom Styling
st.markdown(
    """
    <style>
        body { background-color: #f8f9fa; color: #333; }
        .stButton > button {
            background-color: #64b5f6 !important;
            color: white !important;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton > button:hover { background-color: #42a5f5 !important; }
        .stMarkdown h1 { color: #5c67f2; }
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Navigation Sidebar
page = st.sidebar.radio("📌 Select Feature", ["Fusion Recipe Generator", "AI Meal Planner + Grocery Ordering"])

if page == "Fusion Recipe Generator":
    st.markdown("<h1 style='text-align: center;'>🌍 AI-Powered Fusion Recipe Generator 🍽️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>🔍 Discover unique fusion dishes from different cuisines!</p>", unsafe_allow_html=True)

    ingredients = st.text_input("🛒 **Enter Ingredients (comma-separated):**", placeholder="E.g., potatoes, tomatoes, paneer")
    col1, col2 = st.columns(2)
    cuisine_options = ["Indian", "Mexican", "Italian", "Chinese", "Japanese", "French", "Mediterranean", "Thai", "Korean", "American"]
    cuisine1 = col1.selectbox("🥘 First Cuisine", cuisine_options, index=0)
    cuisine2 = col2.selectbox("🍜 Second Cuisine", cuisine_options, index=3)
    diet_options = ["None", "Diabetes-Friendly", "Low-Carb", "High-Protein", "Vegan", "Gluten-Free", "Keto", "Heart-Healthy"]
    diet_preference = st.selectbox("🥗 **Select Dietary Preference (Optional):**", diet_options, index=0)

    if st.button("✨ Generate Fusion Recipe"):
        if not ingredients.strip():
            st.warning("⚠️ Please enter at least one ingredient!")
        else:
            with st.spinner("🔄 AI is generating your fusion recipe..."):
                response = requests.get("http://127.0.0.1:8000/generate_fusion_recipe/", 
                                        params={"ingredients": ingredients, "cuisine1": cuisine1, "cuisine2": cuisine2, "diet": diet_preference})
            
            if response.status_code == 200:
                recipe_data = response.json()
                recipe_text = recipe_data.get("recipe", "❌ Recipe not found. Try again!")
                st.success(recipe_text)
            else:
                st.error("🚨 Error fetching recipe. Try again later.")

elif page == "AI Meal Planner + Grocery Ordering":
    st.markdown("<h1 style='text-align: center;'>📆 AI Meal Planner & Amazon Fresh 🛒</h1>", unsafe_allow_html=True)
    diet_choice = st.selectbox("🥗 **Select Diet Type:**", ["Balanced", "Diabetes-Friendly", "Low-Carb", "High-Protein", "Vegan", "Gluten-Free", "Keto", "Heart-Healthy"])
    preferences = st.text_input("💡 **Any Preferences? (E.g., no dairy, spicy food, quick meals)**", "")

    if st.button("📅 Generate 7-Day Meal Plan"):
        with st.spinner("🔄 AI is creating your meal plan..."):
            meal_plan_data = generate_meal_plan(diet=diet_choice, preferences=preferences)
            grocery_list = extract_grocery_list(meal_plan_data)
            save_meal_plan(diet_choice, preferences, meal_plan_data, grocery_list)  # ✅ Save to Database

        st.success("✅ Meal Plan Generated!")

        # Display Meal Plan in a Styled Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"## 📆 {diet_choice} Meal Plan")
        st.markdown(meal_plan_data["meal_plan"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Display Grocery List with Amazon Links
        if grocery_list:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📋 Grocery List (Order on Amazon Fresh)")
            for category, items in grocery_list.items():
                st.markdown(f"**{category}**")
                for item in items:
                    amazon_link = amazon_search_url(item)
                    st.markdown(f"- [{item}]({amazon_link}) 🛒")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ No grocery list extracted! Please check the format.")

    # Grocery Store Finder
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>🛒 Find Nearby Grocery Stores 🏪</h2>", unsafe_allow_html=True)
    user_location = st.text_input("📍 Enter your location (city, zip code, or address):")

    if st.button("🔎 Search Stores"):
        if not user_location.strip():
            st.warning("⚠️ Please enter a location!")
        else:
            with st.spinner("🔄 Finding your location..."):
                try:
                    geocode_result = gmaps.geocode(user_location)
                    if not geocode_result:
                        st.error("🚨 Invalid location entered! Please enter a valid city or zip code.")
                    else:
                        location_data = geocode_result[0]['geometry']['location']
                        latitude, longitude = location_data['lat'], location_data['lng']

                        with st.spinner("🔄 Searching for nearby grocery stores..."):
                            results = gmaps.places_nearby(location=(latitude, longitude), radius=5000, type="supermarket")
                            stores = results.get("results", [])

                            if stores:
                                st.markdown("### 🏬 Nearby Grocery Stores:")
                                for store in stores[:5]:
                                    store_name = store.get("name", "Unknown Store")
                                    store_address = store.get("vicinity", "Address not available")
                                    st.markdown(f"✔️ **{store_name}** - {store_address}")
                            else:
                                st.warning("⚠️ No grocery stores found nearby. Try another location.")
                except Exception as e:
                    st.error(f"🚨 Error fetching grocery stores: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>💡 <i>Powered by AI | Created by [Vinit Desai]</i></p>", unsafe_allow_html=True)
