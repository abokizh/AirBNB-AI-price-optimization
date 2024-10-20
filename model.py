import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

class Model:
    xgb_model = None

    def train(self):
        df = pd.read_csv('florida_data.csv')

        # Drop NAs
        df_cleaned = df.dropna()

        # Add occupancy percentage column and drop booked and available columns
        df_cleaned["occupancy"] = 100 * df_cleaned['booked']/(df_cleaned['available']+df_cleaned['booked'])


        Q1_price = df_cleaned['price'].quantile(0.25)
        Q3_price = df_cleaned['price'].quantile(0.75)
        IQR_price = Q3_price - Q1_price

        Q1_occupancy = df_cleaned['occupancy'].quantile(0.25)
        Q3_occupancy = df_cleaned['occupancy'].quantile(0.75)
        IQR_occupancy = Q3_occupancy - Q1_occupancy


        # Define the bounds for outliers
        lower_bound_price = Q1_price - 1.5 * IQR_price
        upper_bound_price = Q1_price + 1.5 * IQR_price


        lower_bound_occupancy = Q1_occupancy - 1.5 * IQR_occupancy
        upper_bound_occupancy = Q3_occupancy + 1.5 * IQR_occupancy

        # Filter out rows that have 'price' and 'occupancy' outside these bounds
        df_no_outliers = df_cleaned[
            (df_cleaned['price'] >= lower_bound_price) & (df_cleaned['price'] <= upper_bound_price) &
            (df_cleaned['occupancy'] >= lower_bound_occupancy) & (df_cleaned['occupancy'] <= upper_bound_occupancy)
            ]

        print(lower_bound_occupancy, upper_bound_occupancy)

        # Features (X) and target (y)
        X = df_no_outliers.drop(columns=['price', 'booked', 'available', 'id'])  # Assuming 'price' is the target variable
        y = df_no_outliers['price']

        print(len(X))

        # If there are categorical columns, use LabelEncoder to convert them to numeric (as a simple approach)
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            label_encoders[column] = LabelEncoder()
            X[column] = label_encoders[column].fit_transform(X[column])

        # Split the dataset into training and testing sets (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print(X_train)

        ### Initialize the XGBRegressor model ###
        self.xgb_model = XGBRegressor(max_depth=3, learning_rate=0.1, n_estimators=100)

        # Hyperparameter tuning 
        param_distributions = {
            'max_depth': [3, 4, 5, 6],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'n_estimators': [100, 200, 300],
            'subsample': [0.7, 0.8, 0.9, 1.0],
            'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
            'min_child_weight': [1, 2, 3, 4]
        }
        self.xgb_model = RandomizedSearchCV(self.xgb_model, param_distributions, scoring='neg_mean_squared_error', n_iter=100, cv=3, random_state=42)


        # Train the model
        self.xgb_model.fit(X_train, y_train)

        # Make predictions on the test set
        y_test_pred = self.xgb_model.predict(X_test)

        # Make predictions on the training set
        y_train_pred = self.xgb_model.predict(X_train)

        # Evaluate the model (using Mean Squared Error here as a metric)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mse = mean_squared_error(y_train, y_train_pred)

        print(f'XGBRegression Test RMSE: {test_mse**(1/2)}')
        print(f'XGBRegression Train RMSE: {train_mse**(1/2)}\n')

        # # Plot feature importance
        # xgb.plot_importance(self.xgb_model.best_estimator_)  # 'best_estimator_' if using RandomizedSearchCV
        # plt.show()

    def predict(self, user_input): 
        user_input_df = pd.DataFrame(user_input)
        return self.xgb_model.predict(user_input_df)[0]


# user_inputs = [
#     {
#         'guests': [10],
#         'rooms': 5,
#         'beds': 9,
#         'baths': 5,
#         'occupancy': 50
#     },
#     {
#         'guests': [30],
#         'rooms': 5,
#         'beds': 5,
#         'baths': 5,
#         'occupancy': 50
#     },
#     {
#         'guests': [3],
#         'rooms': 1,
#         'beds': 2,
#         'baths': 1.5,
#         'occupancy': 70
#     },
# ]

# model = Model()
# model.train()  # Train the model

# for user_input in user_inputs:
#     predicted_price = model.predict(user_input)
#     print(f'Price: {predicted_price}')

## Streamlit 

import streamlit as st

# Set the title of the app
st.title("Optimize your AirBNB price")
st.write("This AI model takes your AirBNB parameters like number of rooms, beds, and fits the price for you desired occupancy.")

# Create numeric inputs for guests, rooms, beds, and baths
guests = st.number_input("Number of Guests", min_value=1, max_value=100, value=1)
rooms = st.number_input("Number of Rooms", min_value=1, max_value=20, value=1)
beds = st.number_input("Number of Beds", min_value=1, max_value=20, value=1)
baths = st.number_input("Number of Baths", min_value=0.5, max_value=10.0, value=1.0, step=0.5)


# Create a checkbox for maximizing revenue
maximize_revenue = st.checkbox("Maximize Revenue")
different_occupations = st.checkbox("See Price Per Occupation rate")
# Disable occupancy slider if 'Maximize Revenue' is checked
if maximize_revenue and not different_occupations:
    st.write("Finds best price to predict occupancy maximizing your AirBNB earning")
elif different_occupations and not maximize_revenue:
    st.write("Gives predicted price to get different occupancies and earnings")
elif different_occupations and maximize_revenue:
    st.error("Please check only one or neither checkbox!")
else:
    occupancy = st.slider("Desired Occupancy (%)", min_value=0, max_value=100, value=70)

# Optionally, you can add a button to submit the inputs
if st.button("Get Price"):

    model = Model()
    model.train()  # Train the model

    if maximize_revenue:
        user_input = {
            'guests': [guests],
            'rooms': rooms,
            'beds': beds,
            'baths': baths,
        }

        occupancy = 0
        price = 0
        revenue = 0
        for i in range(1, 101):
            user_input["occupancy"] = i
            predicted_price = model.predict(user_input)

            # Maximize price
            if revenue < (predicted_price * 30 * (i/100)):
                revenue = predicted_price * 30 * (i/100)
                price = predicted_price
                occupancy = i

        st.success(f"Pricing your AirBNB at ${predicted_price:.2f} per night, will lead to {occupancy}% occupancy")
        st.success(f"This will maximize your earnings, leading to a monthly revenue of ${revenue:.2f}")
    elif different_occupations:
        user_input = {
            'guests': [guests],
            'rooms': rooms,
            'beds': beds,
            'baths': baths,
        }

        table = {
            "Price": [],
            "Occupancy": [],
            "Monthly Revenue": []
        }

        for i in range(10, 101, 10):
            user_input["occupancy"] = i
            predicted_price = model.predict(user_input)
            table["Price"].append(f"${predicted_price:.2f}")
            table["Occupancy"].append(f"{i}%")
            table["Monthly Revenue"].append(f"${(predicted_price * 30 * (i/100)):.2f}")

        # Create a DataFrame from the data
        df = pd.DataFrame(table)

        # Display the table in Streamlit
        st.write("Table with predicted price, occupancy, and monthly revenue")
        st.table(df)  # Or you can use st.write(df) as well
        

    else:
        user_input = {
            'guests': [guests],
            'rooms': rooms,
            'beds': beds,
            'baths': baths,
            'occupancy': occupancy
        }

        predicted_price = model.predict(user_input)
        st.success(f"Your AirBNB that can host up to {guests} guests, with {rooms} rooms, {beds} beds, and {baths} baths, needs to be priced ${predicted_price:.2f} per night")
        st.success(f"Predicted monthly revenue: ${(predicted_price*30*(occupancy/100)):.2f}")