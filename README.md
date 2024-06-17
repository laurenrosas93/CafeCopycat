# larosas-project

Project Spec: CafeCopyCat
A.	Description
•	This app will be designed for enthusiasts who enjoy making coffee drinks, mocktails, cocktails, and other specialty drinks at home
•	It will provide users with detailed recipes, step-by-step instructions, ingredient lists, and brewing or mixing tips for a wide variety of beverages. 
•	It will include a feature for users to rate the drinks they make and log the date they made them
•	The user will be able to filter by ingredients and type of drink to find recipes they are interested in recreating
•	Additionally, it will support measurement conversions to accommodate users from different regions

B.	Task Vignettes
Task 1: Exploring and Making a Drink
Vignette: Emma opens the CafeCopycat (temporary name) app on her laptop. She sees a categorized list of drinks, including coffee drinks, mocktails, and cocktails. Intrigued by the Pumpkin Spice Latte, she clicks on it and is taken to a detailed recipe page. Emma follows the step-by-step instructions and successfully makes the drink. After enjoying it, she rates the drink 4 out of 5 stars and logs the date she made it.
Details:
•	User navigates to the app's homepage.
•	User clicks on a recipe link.
•	App retrieves and displays the recipe details.
•	User follows the instructions and makes the drink.
•	User rates the drink and logs the date.
•	Rating and log are saved in the SQLite database.
Task 2: Finding Drinks Based on Ingredients
Vignette: John wants to make a drink but only has limited ingredients at home. He opens the Cafecopycat app and uses the "Find by Ingredients" feature. He enters the ingredients he has (e.g., milk, coffee, sugar) and clicks "Search." The app displays a list of drinks he can make with those ingredients. John selects a Mocha Frappuccino and follows the provided recipe.
Details:
•	User selects the "Find by Ingredients" feature.
•	User inputs available ingredients.
•	App searches the database for recipes matching the ingredients.
•	App displays a list of matching recipes.
•	User selects a recipe and follows the instructions.
Task 3: Using Measurement Conversions
Vignette: Lily finds a Margarita recipe she loves, but the measurements are in milliliters and she prefers using ounces. She opens the recipe on the drink copycat app and uses the measurement conversion feature. The app converts all measurements to ounces, and Lily proceeds to make the drink with her preferred units.
Details:
•	User selects a recipe.
•	User activates the measurement conversion feature.
•	App converts measurements in the recipe from milliliters to ounces (or vice versa).
•	User follows the converted recipe instructions.





C.	Technical Flow

1.	User Input
•	User Registration: User creates an account to save data for rating drinks, saved recipes, and other user specific data
•	Once logged in:
	Users can select a recipe from the homepage OR
	Users can rate drinks and log the date made OR
	Users can enter available ingredients to find matching recipes OR
	Users can request measurement conversions.

2.	Where to get data:
o	Recipe data is fetched from a predefined dataset or API:
	I found this free API for the cocktails: https://www.thecocktaildb.com/api.php
o	Ratings and logs are retrieved and updated in the database.

3.	Code working in the background for:
o	Ingredient matching and recipe search
o	Measurement conversions 

4.	Results
o	Recipe details are displayed on the recipe page.
o	User ratings and logs are stored and retrievable 
o	Matching recipes are displayed based on user input ingredients.
o	Converted measurements are updated in real-time on the page by switching toggle switches in settings














Mockup
  
   
![image](https://github.com/laurenrosas93/CafeCopycat/assets/95515803/15203867-1803-4c68-9163-d54479fc41ee)

