import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


class Model:
    xgb_model = None

    def train(self):
        df = pd.read_csv('accommodation_data.csv')

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
        user_input = {
            'guests': [2],
            'rooms': 2,
            'beds': 1,
            'baths': 1.5,
            'occupancy': 70
        }
        user_input_df = pd.DataFrame(user_input)
        print(self.xgb_model.predict(user_input_df)[0])