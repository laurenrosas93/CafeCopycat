from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
import os
from datetime import datetime
import random  

app = Flask(__name__)

# Load the list of drinks and their details from the CSV file
def create_drinks_table():
    try:
        drinks_df = pd.read_csv('data/default.csv')
    except FileNotFoundError:
        drinks_df = pd.DataFrame(columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb'])
    print('Drinks table created:\n', drinks_df.head())
    return drinks_df

app.config["drinks_df"] = create_drinks_table()
app.config["saved_recipes"] = []

def save_drinks(df):
    df.to_csv('data/default.csv', index=False)

def fetch_categories():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/list.php?c=list')
    if response.status_code == 200:
        categories = [item['strCategory'] for item in response.json()['drinks']]
        return categories
    return []

def fetch_drinks_by_name(name):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

def fetch_drink_details(drink_id):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}')
    if response.status_code == 200:
        return response.json()['drinks'][0]
    return {}

def fetch_drinks_by_filter(categories=None):
    drinks = app.config["drinks_df"]
    
    if categories:
        drinks = drinks[drinks['strCategory'].isin(categories)]
    
    return drinks

def get_random_drink():
    drinks = app.config["drinks_df"]
    if not drinks.empty:
        return drinks.sample(1).iloc[0].to_dict()
    return {}

def convert_to_metric(measurement):
    conversions = {
        'oz': 29.5735,
        'ml': 1,
        'cl': 10,
        'l': 1000
    }
    try:
        amount, unit = measurement.split()
        amount = float(amount)
        if unit in conversions:
            return f"{amount * conversions[unit]:.2f} ml"
    except ValueError:
        return measurement
    return measurement

def convert_to_imperial(measurement):
    conversions = {
        'ml': 0.033814,
        'cl': 0.33814,
        'l': 33.814,
        'oz': 1
    }
    try:
        amount, unit = measurement.split()
        amount = float(amount)
        if unit in conversions:
            return f"{amount * conversions[unit]:.2f} oz"
    except ValueError:
        return measurement
    return measurement

def initialize_drinks():
    if app.config["drinks_df"] is None or app.config["drinks_df"].empty:
        drinks = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            drinks.extend(fetch_drinks_by_name(letter))
        app.config["drinks_df"] = pd.DataFrame(drinks, columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb'])
        print("Initialized drinks list\n", app.config["drinks_df"])
        save_drinks(app.config["drinks_df"])

@app.route('/')
def home():
    initialize_drinks()
    categories = app.config["drinks_df"]['strCategory'].unique()
    drink_of_the_day = get_random_drink()
    return render_template('home.html', categories=categories, drink_of_the_day=drink_of_the_day)

@app.route('/category/<category_name>')
def category(category_name):
    drinks = app.config["drinks_df"][app.config["drinks_df"]['strCategory'] == category_name]
    print(f"Drinks in category {category_name}:\n{drinks}")
    return render_template('category.html', category=category_name, drinks=drinks.to_dict('records'))

@app.route('/recipe/<drink_id>', methods=['GET', 'POST'])
def recipe(drink_id):
    details = fetch_drink_details(drink_id)
    is_saved = any(d['idDrink'] == drink_id for d in app.config["saved_recipes"])
    rating = next((d['rating'] for d in app.config["saved_recipes"] if d['idDrink'] == drink_id), None)
    
    if request.method == 'POST':
        if 'save' in request.form and not is_saved:
            rating = request.form.get('rating')
            save_recipe(details, rating)  # Saves the recipe with the rating if the save button was clicked
            return redirect(url_for('saved_recipes'))
        elif 'rate' in request.form:
            rating = request.form.get('rating')
            for d in app.config["saved_recipes"]:
                if d['idDrink'] == drink_id:
                    d['rating'] = rating
                    break

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

    return render_template('recipe.html', details=details, is_saved=is_saved, rating=rating)

@app.route('/saved_recipes')
def saved_recipes():
    return render_template('saved_recipes.html', saved_recipes=app.config["saved_recipes"])

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    categories = request.args.getlist('categories')
    
    if query:
        drinks = fetch_drinks_by_name(query)
    else:
        drinks = fetch_drinks_by_filter(categories)
    
    return render_template('search_results.html', drinks=drinks.to_dict('records'))

def save_recipe(details, rating):  # Save the recipe details and rating to the text file
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
        f.write(f"Rating: {rating}\n")
    details['saved_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    details['rating'] = rating
    app.config["saved_recipes"].append(details)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
