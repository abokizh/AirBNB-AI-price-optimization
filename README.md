# AirBNB-AI-price-optimization
This model scrapes current AirBNB listings in Florida, and uses their data like, number of guests, beds, rooms, occupancy level to predict and optimize you AirBNB price based on what occupancy you want it to have.

## Model
Model uses ```XGBoost``` regression with ```RandomizedSearchCV```
The **data** is parsed with self made parser of AirBNB given the seach filters given
Current dataset contains AirBNBs data from Tampa, Miami, Panama City Beach, Orlando, Fort Myers and stored in ```florida_data.csv``` file
Current Test ```RMSE~29``` and Train ```RMSE~24``` 
## Parser
```web_parser.py``` - parses links from search page of AirBNB and parses:
- **guests** - number of guests property can host
- **rooms** - number of rooms in AirBNB
- **beds** - number of beds in AirBNB
- **price** - price per night of the property
- **booked** - number days the property is booked
- **available** - number of guests property is available

Insert links of the search page with properties to be parsed:
```
base_urls = [
    "https://www.airbnb.com/s/Tampa--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
    "https://www.airbnb.com/s/Miami--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
    "https://www.airbnb.com/s/Panama-City-Beach--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
    "https://www.airbnb.com/s/Orlando--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
    "https://www.airbnb.com/s/Fort-Myers--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
]
```

## Demo

This project includes demo on streamlit - <a target=”_blank” href="https://airbnbai.streamlit.app">Demo</a>