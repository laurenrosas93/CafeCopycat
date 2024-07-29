# Welcome to CafeCopyCat!

This guide will help you install and run the CafeCopyCat application, allowing you to explore, create, and save drink recipes. Follow the steps below to get started.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Using CafeCopyCat](#using-cafecopycat)
   - [Home Page](#home-page)
   - [Browsing Categories](#browsing-categories)
   - [Searching for Drinks](#searching-for-drinks)
   - [Viewing a Recipe](#viewing-a-recipe)
   - [Creating a Recipe](#creating-a-recipe)
   - [Saving and Rating Recipes](#saving-and-rating-recipes)
4. [Common Issues and Fixes](#common-issues-and-fixes)
5. [Known Limitations](#known-limitations)
6. [Possible Future Work](#possible-future-work)

## Prerequisites
- Python 3.6 or higher

## Installation

1. **Clone the Repository:**
   git clone https://github.com/laurenrosas93/CafeCopycat.git
   cd CafeCopycat
   
2. **Configuration**
    Ensure that the following directories exist
- `data/` for data files.
- `static/uploads/` for uploaded images.

3. **Running-the-Application**
   python main.py

## Using CafeCopyCat

### Home Page
**Visit the home page:**
Open your web browser and navigate to `http://localhost:5001`. You will see the home page with various drink categories and the featured drink of the day.

**Page details:**
- **Categories:** Displays drink categories.
- **Drink of the Day:** Shows a random drink.
- **Search:** Allows searching for drinks by name or ingredient.
- **Created Drinks:** Will become available to click and view once you create and submit a recipe.
- **Saved Recipes:** Will route to saved recipes page. If a recipe has been saved a thumbnail image will appear with the drink details. If no recipe has been saved yet, you will be routed to search for a drink.

### Browsing Categories
**Browse Categories:**
Click on any category button to see a list of drinks in that category.

### Searching for Drinks
**Search by Name or Ingredient:**
Use the search bar to find drinks by name or ingredient. You can also filter by alcoholic or non-alcoholic drinks.

### Viewing a Recipe
**View Recipe Details:**
Click on any drink to view its detailed recipe, including ingredients and instructions.

### Creating a Recipe
**Create a New Recipe:**
Navigate to the "Create Recipe" page using the navigation bar. Fill out the form with your drink's name, category, ingredients, measurements, and instructions. You can also upload an image.

**Submit the Recipe:**
Click the "Submit" button to save your recipe. Your created recipe will be available in the "Created Recipes" category.

### Saving and Rating Recipes
**Save a Recipe:**
On any recipe page, you can add notes and rate the recipe using the star rating system. Click "Save Recipe" to save it to your saved recipes.

**View Saved Recipes:**
Go to the "Saved Recipes" page to see all your saved recipes along with your notes and ratings.

## Common Issues and Fixes

**Common Errors:**
- **File Not Found:** Ensure all necessary files, like `data/default.csv`, exist.
- **API Errors:** Check your internet connection and API key configurations.
- **Server Errors:** If the server crashes, check the console for error messages and debug accordingly.

## Known Limitations

**Uploading Images:**
Ensure the `UPLOAD_FOLDER` directory exists and has appropriate permissions for uploading files.

**Measurement Conversions:**
Some measurements may not convert correctly if entered in an unexpected format.

**Search Functionality:**
Search is limited to basic queries and may not handle complex searches.

## Possible Future Work

**Expand Categories:**
Add more drink categories and options for users.

**User Authentication:**
Implement user accounts for personalized experiences.

**API Integration:**
Expand integration with more cocktail APIs for a larger database of drinks.
