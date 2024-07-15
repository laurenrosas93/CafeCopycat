from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import requests
import os
from datetime import datetime
import random
from fractions import Fraction
from urllib.parse import quote

app = Flask(__name__)

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Load the list of drinks and their details from the CSV file
def create_drinks_table():
    try:
        drinks_df = pd.read_csv('data/default.csv')
    except FileNotFoundError:
        drinks_df = pd.DataFrame(columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb', 'strIngredient1', 'strAlcoholic'])
        drinks_df.to_csv('data/default.csv', index=False)  # Save the empty DataFrame to avoid future errors
    print('Drinks table created:\n', drinks_df.head())
    return drinks_df

app.config["DRINKS_DF"] = create_drinks_table()
app.config["SAVED_RECIPES"] = []

def save_drinks(df):
    df.to_csv('data/default.csv', index=False)

def fetch_categories_with_drinks():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/list.php?c=list')
    if response.status_code == 200:
        categories = [item['strCategory'] for item in response.json()['drinks']]
        non_empty_categories = []
        for category in categories:
            drinks = fetch_drinks_by_category(category)
            if drinks:
                non_empty_categories.append(category)
        return non_empty_categories
    return []

def fetch_drinks_by_category(category):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/filter.php?c={quote(category)}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

def fetch_drinks_by_name(name):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

def fetch_drinks_by_ingredient(ingredient):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={ingredient}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

def fetch_drink_details(drink_id):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}')
    if response.status_code == 200:
        return response.json()['drinks'][0]
    return None

def fetch_drinks_by_filter(categories=None):
    drinks = app.config["DRINKS_DF"]
    if categories:
        drinks = drinks[drinks['strCategory'].isin(categories)]
    return drinks

def fetch_drinks_by_letter(letter):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}')
    if response.status_code == 200 and response.json()['drinks']:
        drinks = response.json()['drinks']
        for drink in drinks:
            drink.setdefault('strAlcoholic', None)
        return drinks
    return []

def fetch_drinks_by_alcoholic(alcoholic):
    if alcoholic == "Alcoholic":
        url = 'https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Alcoholic'
    else:
        url = 'https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Non_Alcoholic'
    response = requests.get(url)
    if response.status_code == 200 and response.json()['drinks']:
        drinks = response.json()['drinks']
        for drink in drinks:
            drink['strAlcoholic'] = alcoholic
        return drinks
    return []

def get_random_drink():
    drinks = app.config["DRINKS_DF"]
    if not drinks.empty:
        return drinks.sample(1).iloc[0].to_dict()
    return {}

def convert_to_metric(measurement):
    conversions = {
        'oz': 29.5735,
        'lb': 453.592,  # added conversion for lbs and cups
        'cup': 240,
        'ml': 1,
        'cl': 10,
        'l': 1000
    }
    try:
        if measurement:
            parts = measurement.split()
            if len(parts) == 2:
                amount, unit = parts
            elif len(parts) == 3 and parts[1] in ["to", "taste"]:  # handle "to taste" and similar phrases
                return measurement
            else:
                amount = parts[0]
                unit = parts[-1]

            amount = float(Fraction(amount))  # Convert fractional amounts
            if unit in conversions:
                return f"{amount * conversions[unit]:.2f} ml"
    except (ValueError, AttributeError):
        return measurement
    return measurement

def convert_to_imperial(measurement):
    conversions = {
        'ml': 0.033814,
        'cl': 0.33814,
        'l': 33.814,
        'oz': 1,
        'cup': 0.00422675,
        'lb': 0.00220462
    }
    try:
        if measurement:
            parts = measurement.split()
            if len(parts) == 2:
                amount, unit = parts
            elif len(parts) == 3 and parts[1] in ["to", "taste"]:  # handle "to taste" and similar phrases
                return measurement
            else:
                amount = parts[0]
                unit = parts[-1]

            amount = float(Fraction(amount))  # Convert fractional amounts
            if unit in conversions:
                return f"{amount * conversions[unit]:.2f} oz"
    except (ValueError, AttributeError):
        return measurement
    return measurement

def initialize_drinks():
    if app.config["DRINKS_DF"] is None or app.config["DRINKS_DF"].empty:
        drinks = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            drinks.extend(fetch_drinks_by_letter(letter))
        app.config["DRINKS_DF"] = pd.DataFrame(drinks, columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb'])
        save_drinks(app.config["DRINKS_DF"])

@app.route('/')
def home():
    initialize_drinks()
    categories = fetch_categories_with_drinks()
    drink_of_the_day = get_random_drink()
    return render_template('home.html', categories=categories, drink_of_the_day=drink_of_the_day)

@app.route('/category/<category_name>')
def category(category_name):
    category_name = category_name.replace("%20", " ").replace("%2F", "/")
    drinks = app.config["DRINKS_DF"][app.config["DRINKS_DF"]['strCategory'] == category_name]
    if drinks.empty:
        return render_template('not_found.html')
    return render_template('category.html', category=category_name, drinks=drinks.to_dict('records'))


@app.route('/recipe/<drink_id>', methods=['GET', 'POST'])
def recipe(drink_id):
    details = fetch_drink_details(drink_id)
    if details is None:
        return render_template('not_found.html')

    is_saved = any(d['idDrink'] == drink_id for d in app.config["SAVED_RECIPES"])
    recipe_saved = False
    notes = ""
    rating = next((d['rating'] for d in app.config["SAVED_RECIPES"] if d['idDrink'] == drink_id), None)

    if request.method == 'POST':
        if 'save' in request.form:
            notes = request.form.get('notes')
            rating= int(request.form.get('rating'))
            save_recipe(details, notes, rating)  # Save the recipe with notes and rating
            recipe_saved = True
            return redirect(url_for('recipe', drink_id=drink_id, saved='true'))

        unit = request.form.get('unit')
        if unit == 'metric':
            for i in range(1, 16):
                measure_key = f'strMeasure{i}'
                if details.get(measure_key):
                    details[measure_key] = convert_to_metric(details[measure_key])
        else:
            for i in range(1, 16):
                measure_key = f'strMeasure{i}'
                if details.get(measure_key):
                    details[measure_key] = convert_to_imperial(details[measure_key])

    recipe_saved = request.args.get('saved') == 'true'

    return render_template('recipe.html', details=details, is_saved=is_saved, recipe_saved=recipe_saved, notes=notes, rating=rating)

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    data = request.json
    drink_id = data['idDrink']
    rating = int(data)['rating']

    for recipe in app.config["SAVED_RECIPES"]:
        if recipe['idDrink'] == drink_id:
            recipe['rating'] = rating
            break
    else:
        for recipe in app.config["DRINKS_DF"].to_dict('records'):
            if recipe['idDrink'] == drink_id:
                recipe['rating'] = rating
                app.config["SAVED_RECIPES"].append(recipe)
                break

    save_drinks(app.config["DRINKS_DF"])
    return jsonify({"success": True})

@app.route('/saved_recipes')
def saved_recipes():
    if not app.config["SAVED_RECIPES"]:
        return render_template('no_saved_recipes.html')
    return render_template('saved_recipes.html', saved_recipes=app.config["SAVED_RECIPES"])

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    ingredient = request.args.get('ingredient')
    alcoholic = request.args.get('alcoholic')
    
    drinks = []

    if query and len(query) == 1:
        drinks = fetch_drinks_by_letter(query)
    elif query:
        drinks = fetch_drinks_by_name(query)
    elif ingredient:
        drinks = fetch_drinks_by_ingredient(ingredient)
    elif alcoholic:
        drinks = fetch_drinks_by_alcoholic(alcoholic)
    else:
        drinks = app.config["DRINKS_DF"].to_dict('records')
    
    if not drinks:
        return render_template('not_found.html')
    
    return render_template('search_results.html', drinks=drinks)

def save_recipe(details, notes, rating=None):
    if not os.path.exists('saved_recipes'):
        os.makedirs('saved_recipes')
    filename = os.path.join('saved_recipes', f"{details['strDrink']}.txt")
    with open(filename, 'w') as f:
        f.write(f"Recipe for {details['strDrink']}:\n")
        f.write(f"Category: {details['strCategory']}\n")
        f.write(f"Instructions: {details['strInstructions']}\n")
        f.write("Ingredients:\n")
        for i in range(1, 16):
            ingredient = details.get(f"strIngredient{i}")
            measure = details.get(f"strMeasure{i}")
            if ingredient:
                f.write(f"{ingredient}: {measure}\n")
        f.write(f"Notes: {notes}\n")
        if rating:
            f.write(f"Rating: {rating}\n")
    details['saved_date'] = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    details['notes'] = notes
    details['rating'] = rating
    app.config["SAVED_RECIPES"].append(details)
    save_drinks(app.config["DRINKS_DF"])

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
