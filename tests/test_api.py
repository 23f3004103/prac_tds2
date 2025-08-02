import pandas as pd

url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
tables = pd.read_html(url)

highest_grossing_films = tables[0]

# Clean the data
# highest_grossing_films.columns = highest_grossing_films.columns.droplevel()
highest_grossing_films = highest_grossing_films[['Rank', 'Title', 'Worldwide gross', 'Year']]

# Convert 'Worldwide gross' to numeric
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('$', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace(',', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('T', '000')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('SM', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('F', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('DKR', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('TS3', '')
highest_grossing_films['Worldwide gross'] = highest_grossing_films['Worldwide gross'].str.replace('RK', '')
highest_grossing_films['Worldwide gross'] = pd.to_numeric(highest_grossing_films['Worldwide gross'], errors='coerce')

# Answer the questions
bn_movies_before_2000 = highest_grossing_films[(highest_grossing_films['Worldwide gross'] >= 2000000000) & (highest_grossing_films['Year'] < 2000)].shape[0]
earliest_over_1_5_bn = highest_grossing_films[highest_grossing_films['Worldwide gross'] > 1500000000].sort_values('Year').iloc[0]['Title']

result = {
    "Number of $2 bn movies released before 2000": bn_movies_before_2000,
    "Earliest film that grossed over $1.5 bn": earliest_over_1_5_bn
}

print(result)