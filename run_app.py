from flask import Flask, render_template, request, redirect, url_for, jsonify 
import pandas as pd
import requests
import os

app = Flask(__name__)
drinks_df = None

# Load the list of drinks and their details from the CSV file
def load_drinks():
    global drinks_df
    try:
        drinks_df = pd.read_csv('data/default.csv')
    except FileNotFoundError:
        drinks_df = pd.DataFrame(columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb'])

# Save the list of drinks to the CSV
def save_drinks(df):
    df.to_csv('data/default.csv', index=False)

# Pull the list of drink categories from API
def fetch_categories():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/list.php?c=list')
    if response.status_code == 200:
        categories = [item['strCategory'] for item in response.json()['drinks']]
        return categories
    return []

# Pull drinks by first letter from API
def fetch_drinks_by_letter(letter):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

# Pull drinks by name from API
def fetch_drinks_by_name(name):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}')
    if response.status_code == 200 and response.json()['drinks']:
        return response.json()['drinks']
    return []

# Pull detailed drink info by ID from API
def fetch_drink_details(drink_id):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}')
    if response.status_code == 200:
        return response.json()['drinks'][0]
    return {}

# Covert measmurements between imerial and and metric; chosen by user
def convert_to_metric(measurement):
    conversions = {
        'oz': 29.5735,
        'ml': 1,
        'cl': 10,
        'l': 1000
    }
    amount, unit = measurement.split()
    amount = float(amount)
    if unit in conversions:
        return f"{amount * conversions[unit]:.2f} ml"
    return measurement

def convert_to_imperial(measurement):
    conversions = {
        'ml': 0.033814,
        'cl': 0.33814,
        'l': 33.814,
        'oz': 1
    }
    amount, unit = measurement.split()
    amount = float(amount)
    if unit in conversions:
        return f"{amount * conversions[unit]:.2f} oz"
    return measurement

# Load the drinks list (only once)
def initialize_drinks():
    global drinks_df
    if drinks_df is None or drinks_df.empty:
        drinks = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            drinks.extend(fetch_drinks_by_letter(letter))
        drinks_df = pd.DataFrame(drinks, columns=['idDrink', 'strDrink', 'strCategory', 'strDrinkThumb'])
        save_drinks(drinks_df)

@app.route('/') #defining homepage- will need to work on UI
def home():
    initialize_drinks() #Ensure the drinks are loaded from the CSV or API
    categories = drinks_df['strCategory'].unique() ## Extract unique categories from the DataFrame
    return render_template('home.html', categories=categories, drinks=drinks_df.to_dict('records'))

@app.route('/recipe/<drink_id>', methods=['GET', 'POST'])
def recipe(drink_id):
    details = fetch_drink_details(drink_id)  ## pulls detailed information about the drink
    
    if request.method == 'POST':
        if 'save' in request.form:
            save_recipe(details)  # Saves the recipe if the save button was clicked
        unit = request.form.get('unit') # Get the selected unit system from the form
        if unit == 'metric':
            details['measurements'] = convert_to_metric('1 oz')
        else:
            details['measurements'] = convert_to_imperial('1 ml')
    
    return render_template('recipe.html', details=details)  #visual recipe details

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query') #get search query from request
    if query:
        drinks = fetch_drinks_by_name(query) #if searched by name, will pull up drink by name
    else:
        drinks = []
    return render_template('search_results.html', drinks=drinks)

@app.route('/search_by_letter', methods=['GET'])
def search_by_letter():
    letter = request.args.get('letter')  #search by letter
    if letter:
        drinks = fetch_drinks_by_letter(letter)  #should pull up drinks by searched letter
    else:
        drinks = []
    return render_template('search_results.html', drinks=drinks)

def save_recipe(details): #defines a function to save the recipe details to the text file
    if not os.path.exists('saved_recipes'): #Checks if the directory for saved recipe exists
        os.makedirs('saved_recipes') #creates the directory if it doesnt already exist
    filename = os.path.join('saved_recipes', f"{details['strDrink']}.txt") # defines the file name of the saved recipe, uses drink's name
    with open(filename, 'w') as f: #open file to write
        f.write(f"Recipe for {details['strDrink']}:\n")  #writes drink name as file name
        f.write(f"Category: {details['strCategory']}\n") #adds drink category
        f.write(f"Instructions: {details['strInstructions']}\n") #writes the drink instructions and adds to file
        f.write("Ingredients:\n")
        for i in range(1, 16):
            ingredient = details.get(f"strIngredient{i}") #gets the ingredient
            measure = details.get(f"strMeasure{i}") #gets the measurement
            if ingredient:
                f.write(f"{ingredient}: {measure}\n") #if ingredient not "none", writes the ingredient details witb measurements to file

if __name__ == '__main__':
    load_drinks()
    app.run(debug=True, port=5001)  # NOTE: runs Flask in debug mode (please let me know if you would like another way for this such as two .py files for Flask and TkInter)



##ToDO##
# Expand the drink categories to include more than just cocktails, such as mocktails and other beverages.
# Add user options to rate drinks and log the date they were made.
#Fix overall UI
# Include ingredient-based search functionality.
# Fix the measurement conversion options between metric and imperial units. 
# Eventually, integrate user authentication for a more personalized experience.##
