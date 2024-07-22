from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import requests
import os
from datetime import datetime
import random
from fractions import Fraction
from urllib.parse import quote
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Ensure the upload directory exists
if not os.path.exists(app.config.get('UPLOAD_FOLDER', 'static/uploads')):
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'))

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
app.config["CREATED_RECIPES"] = []

def save_drinks(df):
    df.to_csv('data/default.csv', index=False)

def fetch_categories_with_drinks():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/list.php?c=list')
    try:
        if response.status_code == 200:
            json_response = response.json()
            categories = [{'name': item['strCategory'], 'has_drinks': bool(fetch_drinks_by_category(item['strCategory']))}
                          for item in json_response['drinks']
                          if '/' not in item['strCategory']]
            categories.append({'name': 'Created Recipes', 'has_drinks': bool(app.config["CREATED_RECIPES"])})
            print(f"Categories fetched: {categories}")  # Debugging line
            return categories
        print(f"Failed to fetch categories. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for categories. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error when fetching categories. Error: {e}. Response: {response.text}")
    return []

def fetch_drinks_by_category(category):
    if category == 'Created Recipes':
        return app.config["CREATED_RECIPES"]
    try:
        response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/filter.php?c={quote(category)}')
        if response.status_code == 200:
            json_response = response.json()
            if 'drinks' in json_response:
                print(f"Drinks for category {category}: {json_response['drinks']}")  # Debugging line
                return json_response['drinks']
        print(f"Failed to fetch drinks for category {category}. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for category {category}. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error for category {category}. Error: {e}. Response: {response.text}")
    return []

def fetch_drinks_by_name(name):
    drinks = app.config["DRINKS_DF"][app.config["DRINKS_DF"]['strDrink'].str.contains(name, case=False, na=False)].to_dict('records')
    created_drinks = [d for d in app.config["CREATED_RECIPES"] if name.lower() in d['strDrink'].lower()]
    return drinks + created_drinks

def fetch_drinks_by_ingredient(ingredient):
    try:
        response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={ingredient}')
        if response.status_code == 200:
            json_response = response.json()
            if 'drinks' in json_response:
                return json_response['drinks']
        print(f"Failed to fetch drinks by ingredient {ingredient}. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for ingredient {ingredient}. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error for ingredient {ingredient}. Error: {e}. Response: {response.text}")
    return []

def fetch_drink_details(drink_id):
    # Check if the drink_id is for a custom saved recipe
    saved_recipe = next((d for d in app.config["SAVED_RECIPES"] if d['idDrink'] == drink_id), None)
    if saved_recipe:
        return saved_recipe

    # Check if the drink_id is for a custom created recipe
    created_recipe = next((d for d in app.config["CREATED_RECIPES"] if d['idDrink'] == drink_id), None)
    if created_recipe:
        return created_recipe

    # Otherwise, fetch from the API
    try:
        response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}')
        if response.status_code == 200:
            json_response = response.json()
            if 'drinks' in json_response:
                return json_response['drinks'][0]
        print(f"Failed to fetch drink details for id {drink_id}. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for drink id {drink_id}. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error for drink id {drink_id}. Error: {e}. Response: {response.text}")
    return None

def fetch_drinks_by_filter(categories=None):
    drinks = app.config["DRINKS_DF"]
    if categories:
        drinks = drinks[drinks['strCategory'].isin(categories)]
    return drinks

def fetch_drinks_by_letter(letter):
    try:
        response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}')
        if response.status_code == 200:
            json_response = response.json()
            if 'drinks' in json_response:
                drinks = json_response['drinks']
                for drink in drinks:
                    drink.setdefault('strAlcoholic', None)
                return drinks
        print(f"Failed to fetch drinks by letter {letter}. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for letter {letter}. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error for letter {letter}. Error: {e}. Response: {response.text}")
    return []

def fetch_drinks_by_alcoholic(alcoholic):
    if alcoholic == "Alcoholic":
        url = 'https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Alcoholic'
    else:
        url = 'https://www.thecocktaildb.com/api/json/v1/1/filter.php?a=Non_Alcoholic'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_response = response.json()
            if 'drinks' in json_response:
                drinks = json_response['drinks']
                for drink in drinks:
                    drink['strAlcoholic'] = alcoholic
                return drinks
        print(f"Failed to fetch drinks by alcoholic type {alcoholic}. Status code: {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception for alcoholic type {alcoholic}. Error: {e}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error for alcoholic type {alcoholic}. Error: {e}. Response: {response.text}")
    return []

def get_random_drink():
    drinks = app.config["DRINKS_DF"]
    if not drinks.empty:
        return drinks.sample(1).iloc[0].to_dict()
    return {}

def convert_to_metric(measurement):
    conversions = {
        'oz': 29.5735,
        'lb': 453.592,
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
            elif len(parts) == 3 and parts[1] in ["to", "taste"]:
                return measurement
            else:
                amount = parts[0]
                unit = parts[-1]

            amount = float(Fraction(amount))
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
            elif len(parts) == 3 and parts[1] in ["to", "taste"]:
                return measurement
            else:
                amount = parts[0]
                unit = parts[-1]

            amount = float(Fraction(amount))
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
    print(f"Categories: {categories}")  # Debugging line
    drink_of_the_day = get_random_drink()
    return render_template('home.html', categories=categories, drink_of_the_day=drink_of_the_day)

@app.route('/category/<category_name>')
def category(category_name):
    # Convert underscores back to spaces
    category_name = category_name.replace('_', ' ')
    print(f"Category name received: {category_name}")  # Debugging line
    
    drinks = fetch_drinks_by_category(category_name)
    print(f"Drinks fetched: {drinks}")  # Debugging line
    
    if not drinks:
        return render_template('not_found.html')
    
    return render_template('category.html', category=category_name, drinks=drinks)

@app.route('/recipe/<drink_id>', methods=['GET', 'POST'])
def recipe(drink_id):
    details = fetch_drink_details(drink_id)
    if details is None:
        return render_template('not_found.html')

    is_saved = any(d['idDrink'] == drink_id for d in app.config["SAVED_RECIPES"])
    recipe_saved = False
    notes = details.get('notes', "")
    rating = details.get('rating', None)

    if request.method == 'POST':
        if 'save' in request.form:
            notes = request.form.get('notes')
            rating = int(request.form.get('rating'))
            save_recipe(details, notes, rating)
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
    rating = int(data['rating'])

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

@app.route('/created_recipes')
def created_recipes():
    if not app.config["CREATED_RECIPES"]:
        return render_template('no_saved_recipes.html')
    return render_template('created_recipes.html', saved_recipes=app.config["CREATED_RECIPES"])

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

@app.route('/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    categories = fetch_categories_with_drinks()
    if request.method == 'POST':
        drink_name = request.form.get('drink_name')
        category = request.form.get('category')
        alcoholic = request.form.get('alcoholic')
        instructions = request.form.get('instructions')

        # Handle file upload
        file = request.files['drink_image']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            strDrinkThumb = url_for('static', filename=f'uploads/{filename}', _external=True)
        else:
            strDrinkThumb = ''

        new_recipe = {
            'idDrink': str(random.randint(100000, 999999)),  # Generate a random ID
            'strDrink': drink_name,
            'strCategory': 'Created Recipes',
            'strAlcoholic': alcoholic,
            'strInstructions': instructions,
            'strDrinkThumb': strDrinkThumb,
            'notes': "",
            'rating': None
        }

        for i in range(1, 16):
            ingredient = request.form.get(f'ingredient{i}')
            measure = request.form.get(f'measure{i}')
            unit = request.form.get(f'unit{i}')
            if ingredient and measure:
                new_recipe[f'strIngredient{i}'] = ingredient
                new_recipe[f'strMeasure{i}'] = f"{measure} {unit}"
            else:
                new_recipe[f'strIngredient{i}'] = None
                new_recipe[f'strMeasure{i}'] = None

        app.config["CREATED_RECIPES"].append(new_recipe)
        return redirect(url_for('created_recipes'))

    return render_template('create_recipe.html', categories=[c['name'] for c in categories if c['has_drinks']])

def save_recipe(details, notes, rating=None):
    details['saved_date'] = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    details['notes'] = notes
    details['rating'] = rating
    if details['strCategory'] == 'Created Recipes':
        app.config["CREATED_RECIPES"].append(details)
    else:
        app.config["SAVED_RECIPES"].append(details)

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
