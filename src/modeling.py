import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from joblib import dump, load
from imblearn.over_sampling import SMOTE
import shap
import xgboost as xgb
import os

print("MODEL PIPELINE BAŞLADI")

# Yalnızca gerekli hedefler
TARGETS = {
    'target_churn_risk': 'churn',
    'target_upselling_potential': 'upsell',
}

def load_features(path='outputs/features.csv'):
    return pd.read_csv(path)

def smote_balance(X, y):
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    return X_res, y_res

def train_and_evaluate(X, y, model, model_name, target_name):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        X_train_bal, y_train_bal = smote_balance(X_train, y_train)
        model.fit(X_train_bal, y_train_bal)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:,1]
        auc = roc_auc_score(y_test, y_prob)
        aucs.append(auc)
        print(f"Fold {fold+1} - {target_name}")
        print(classification_report(y_test, y_pred))
        print(f"AUC: {auc:.3f}\n")
    print(f"Ortalama AUC ({target_name}): {np.mean(aucs):.3f}")
    dump(model, f'models/{model_name}.joblib')
    print("FIT FEATURES:", list(X.columns))
    with open("outputs/model_features_fit.txt", "a", encoding="utf-8") as f:
        f.write(f"{target_name}: "+str(list(X.columns))+"\n")
    return model

def shap_importance(model, X, model_name):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap.summary_plot(shap_values, X, show=False)
    import matplotlib.pyplot as plt
    plt.savefig(f'outputs/shap_{model_name}.png')
    plt.close()

def main():
    df = load_features()
    for target_col, target_label in TARGETS.items():
        # Modelin beklediği feature isimlerini yükle
        rf_model_path = f'models/rf_{target_label}.joblib'
        if os.path.exists(rf_model_path):
            model = load(rf_model_path)
            model_features = model.feature_names_in_
            for col in model_features:
                if col not in df.columns:
                    df[col] = 0
            X = df[model_features]
        else:
            # Eğitim için ilk seferde tüm target ve kimlik sütunlarını çıkar
            exclude_cols = ['user_id', 'target_made_payment', 'target_churn_risk', 'target_upselling_potential', 'first_event', 'first_payment_date', 'recent_payment']
            X = df[[col for col in df.columns if col not in exclude_cols]]
        y = df[target_col]
        print(f"\n--- {target_col} sınıf dağılımı ---")
        print(y.value_counts())
        if y.value_counts().min() < 5 or y.nunique() < 2:
            print(f"UYARI: {target_col} için yeterli sınıf yok, model eğitimi atlanıyor.\n")
            continue
        # Random Forest
        rf = RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42)
        rf = train_and_evaluate(X, y, rf, f'rf_{target_label}', target_label)
        shap_importance(rf, X, f'rf_{target_label}')
        # XGBoost
        xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        param_grid = {'max_depth': [3, 5], 'n_estimators': [100, 200]}
        grid = GridSearchCV(xgb_model, param_grid, scoring='roc_auc', cv=3)
        X_bal, y_bal = smote_balance(X, y)
        grid.fit(X_bal, y_bal)
        print(f"XGBoost en iyi parametreler: {grid.best_params_}")
        best_xgb = grid.best_estimator_
        y_pred = best_xgb.predict(X)
        y_prob = best_xgb.predict_proba(X)[:,1]
        print(classification_report(y, y_pred))
        print(f"AUC: {roc_auc_score(y, y_prob):.3f}")
        dump(best_xgb, f'models/xgb_{target_label}.joblib')
        shap_importance(best_xgb, X, f'xgb_{target_label}')

if __name__ == "__main__":
    os.makedirs('models', exist_ok=True)
    main()
