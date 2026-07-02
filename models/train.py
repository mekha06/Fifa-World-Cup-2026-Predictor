import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Setup paths
base_path = r"D:\Coding journey\Fifa World Cup 2026 Predictor"
csv_path = os.path.join(base_path, "world_cup_dataset.csv")
predict_csv_path = os.path.join(base_path, "prediction_dataset.csv")
final_dir = os.path.join(base_path, "finalmodel")
os.makedirs(final_dir, exist_ok=True)

def train_and_evaluate():
    print("=== FIFA World Cup ML Training Pipeline ===")
    
    # 1. DATA LOADING & CLEANING
    df = pd.read_csv(csv_path).dropna(subset=['finish_stage'])
    
    # 2. FEATURE ENGINEERING
    df['elo_host_boost'] = df['elo_rating'] * (df['host'] + 1)
    df['attack_efficiency'] = df['win_percentage_since_last_cup'] * df['goals_scored_per_game']
    
    le = LabelEncoder()
    df['confederation_encoded'] = le.fit_transform(df['confederation'])

    features = [
        'elo_rating', 'win_percentage_since_last_cup', 'goals_scored_per_game', 
        'goals_conceded_per_game', 'points_per_game', 'previous_wc_finish', 
        'host', 'confederation_encoded', 'elo_host_boost', 'attack_efficiency'
    ]

    X = df[features]
    y = df['finish_stage']
    groups = df['year']

    # 3. DEFINE MODELS
    models = {
        'Ridge Regression': Ridge(alpha=10.0, random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        'XGBoost': XGBRegressor(
            objective='reg:absoluteerror', 
            colsample_bytree=0.6, 
            learning_rate=0.05, 
            max_depth=3, 
            n_estimators=100, 
            reg_alpha=1, 
            reg_lambda=2, 
            subsample=0.8, 
            random_state=42,
            tree_method='hist'
        )
    }

    # 4. LEAVE-ONE-GROUP-OUT CROSS-VALIDATION
    logo = LeaveOneGroupOut()
    comparison_results = []
    cv_predictions = {name: [] for name in models}
    actuals_list = []

    print("Evaluating models with Leave-One-Group-Out CV (by Year)...")
    
    for name, model in models.items():
        maes, r2s, rmses = [], [], []
        preds_all = []
        actuals_all = []
        
        for train_idx, test_idx in logo.split(X, y, groups):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
            maes.append(mean_absolute_error(y_test, preds))
            r2s.append(r2_score(y_test, preds))
            rmses.append(np.sqrt(mean_squared_error(y_test, preds)))
            
            preds_all.extend(preds)
            if name == list(models.keys())[0]:
                actuals_all.extend(y_test)
                
        cv_predictions[name] = preds_all
        if not actuals_list:
            actuals_list = actuals_all

        avg_mae = np.mean(maes)
        avg_rmse = np.mean(rmses)
        avg_r2 = np.mean(r2s)
        
        print(f"Model: {name:16s} | MAE: {avg_mae:.4f} | RMSE: {avg_rmse:.4f} | R2: {avg_r2:.4f}")
        comparison_results.append({
            'Model': name,
            'MAE': avg_mae,
            'RMSE': avg_rmse,
            'R2': avg_r2
        })

    comparison_df = pd.DataFrame(comparison_results).sort_values('MAE')
    comparison_df.to_csv(os.path.join(final_dir, "model_comparison.csv"), index=False)

    best_model_name = comparison_df.iloc[0]['Model']
    print(f"Best model selected: {best_model_name}")

    # 5. GENERATE CONFUSION MATRIX FOR BEST MODEL
    best_preds = cv_predictions[best_model_name]
    y_true_round = np.round(actuals_list).astype(int)
    y_pred_round = np.clip(np.round(best_preds), 1, 7).astype(int)

    cm = confusion_matrix(y_true_round, y_pred_round)
    plt.figure(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=sorted(np.unique(y_true_round)))
    disp.plot(cmap='Blues', values_format='d')
    plt.title(f"Confusion Matrix (Rounded Stages) - {best_model_name}")
    plt.tight_layout()
    plt.savefig(os.path.join(final_dir, "confusion_matrix.png"), dpi=150)
    plt.close()

    # 6. TRAIN BEST MODEL ON FULL DATASET
    best_model = models[best_model_name]
    best_model.fit(X, y)

    # Save feature importances if the best model supports it
    if hasattr(best_model, 'feature_importances_'):
        importances = pd.Series(best_model.feature_importances_, index=features).sort_values(ascending=False)
        importances.to_csv(os.path.join(final_dir, "feature_importance.csv"))
        print("\nFeature Importances for Best Model:")
        print(importances.to_string())

    # Save comparison stats to text file
    metrics_summary = "=== MODEL COMPARISON SUMMARY ===\n"
    for idx, row in comparison_df.iterrows():
        metrics_summary += f"{row['Model']}: MAE={row['MAE']:.4f}, RMSE={row['RMSE']:.4f}, R2={row['R2']:.4f}\n"
    metrics_summary += f"\nSelected Best Model: {best_model_name}\n"
    
    with open(os.path.join(final_dir, "metrics.txt"), "w", encoding="utf-8") as f:
        f.write(metrics_summary)

    # 7. LOAD 2026 PREDICTION DATASET & GENERATE PREDICTIONS
    print("Loading 2026 qualified teams...")
    predict_df = pd.read_csv(predict_csv_path)
    
    # Process 2026 features
    predict_df['confederation_encoded'] = le.transform(predict_df['confederation'])
    predict_df['elo_host_boost'] = predict_df['elo_rating'] * (predict_df['host'] + 1)
    predict_df['attack_efficiency'] = predict_df['win_percentage_since_last_cup'] * predict_df['goals_scored_per_game']

    # Predict stage
    predict_df['predicted_finish_stage'] = best_model.predict(predict_df[features])
    
    # Output file
    results = predict_df[['team', 'elo_rating', 'predicted_finish_stage']].sort_values('predicted_finish_stage', ascending=False)
    results.columns = ['Team', 'Elo_Rating', 'Predicted_Stage']
    results.to_csv(os.path.join(final_dir, "final_predictions_2026.csv"), index=False)
    print(f"Predictions successfully written to: {os.path.join(final_dir, 'final_predictions_2026.csv')}")
    print("\nTop 10 predicted 2026 teams:")
    print(results.head(10).to_string(index=False))

if __name__ == "__main__":
    train_and_evaluate()
