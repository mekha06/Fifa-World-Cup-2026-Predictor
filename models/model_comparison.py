import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import os

# Setup paths
base_path = r"D:\Coding journey\Fifa World Cup 2026 Predictor"
csv_path = os.path.join(base_path, "world_cup_dataset.csv")
models_dir = os.path.join(base_path, "models")

def train_and_compare():
    df = pd.read_csv(csv_path).dropna(subset=['finish_stage'])
    
    # Label Encoding for Confederation
    le = LabelEncoder()
    df['confederation_encoded'] = le.fit_transform(df['confederation'])
    
    features = [
        'elo_rating', 'win_percentage_since_last_cup', 'goals_scored_per_game', 
        'goals_conceded_per_game', 'points_per_game', 'previous_wc_finish', 
        'host', 'confederation_encoded'
    ]
    
    # Validation Logic: Using the LAST World Cup to predict the NEXT
    # Cycle 1: 2014 predicts 2018
    # Cycle 2: 2018 predicts 2022
    cycles = [
        (2014, 2018),
        (2018, 2022)
    ]
    
    model_types = {
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42),
        "Linear Regression": LinearRegression()
    }
    
    final_results = []
    
    for model_name, model in model_types.items():
        maes = []
        r2s = []
        
        for train_yr, test_yr in cycles:
            train_df = df[df['year'] == train_yr]
            test_df = df[df['year'] == test_yr]
            
            if len(train_df) > 0 and len(test_df) > 0:
                X_train = train_df[features]
                y_train = train_df['finish_stage']
                X_test = test_df[features]
                y_test = test_df['finish_stage']
                
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                maes.append(mean_absolute_error(y_test, preds))
                r2s.append(r2_score(y_test, preds))
        
        final_results.append({
            "Model": model_name,
            "Avg MAE": np.mean(maes),
            "Avg R2": np.mean(r2s)
        })

    results_df = pd.DataFrame(final_results).sort_values(by="Avg MAE")
    results_df.to_csv(os.path.join(models_dir, "comparison_results.csv"), index=False)
    print("Model comparison (Last Year -> Next Year) completed.")
    print(results_df)

if __name__ == "__main__":
    train_and_compare()
