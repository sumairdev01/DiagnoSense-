import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer

# -----------------------------------------
# CONFIG: update these paths if needed
# -----------------------------------------
FILES = {
    "liver":    "liver.csv",
    "cardio":   "cardio.csv",
    "diabetes": "diabetes.csv",
}

# ==========================================
# 1. LIVER MODEL
# ==========================================
try:
    print("\n[INFO] Training Liver Model...")

    df = pd.read_csv(FILES["liver"], sep=None, engine="python")

    # Map Gender to numeric
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Target column
    target = "Dataset"
    X = df.drop(columns=[target])
    y = df[target]

    # Handle missing values
    imputer = SimpleImputer(strategy="median")
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"   Accuracy: {acc:.4f}")

    with open("liver_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("[SUCCESS] Liver Model Saved -> liver_model.pkl")

except Exception as e:
    print(f"[ERROR] Liver Model Failed: {e}")


# ==========================================
# 2. CARDIO MODEL
# ==========================================
try:
    print("\n[INFO] Training Cardio Model...")

    df = pd.read_csv(FILES["cardio"], sep=None, engine="python")

    # Remove id column if present
    df = df.drop(columns=["id"], errors="ignore")

    # Sample 10,000 rows for speed on large dataset
    if len(df) > 10000:
        print(f"   Large dataset ({len(df):,} rows) - sampling 10,000 rows...")
        df = df.sample(n=10000, random_state=42)

    target = "cardio"
    X = df.drop(columns=[target])
    y = df[target]

    # Handle missing values
    imputer = SimpleImputer(strategy="median")
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"   Accuracy: {acc:.4f}")

    with open("cardio_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("[SUCCESS] Cardio Model Saved -> cardio_model.pkl")

except Exception as e:
    print(f"[ERROR] Cardio Model Failed: {e}")


# ==========================================
# 3. DIABETES MODEL
# ==========================================
try:
    print("\n[INFO] Training Diabetes Model...")

    df = pd.read_csv(FILES["diabetes"], sep=None, engine="python")

    target = "Outcome"
    X = df.drop(columns=[target])
    y = df[target]

    # Handle missing values
    imputer = SimpleImputer(strategy="median")
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"   Accuracy: {acc:.4f}")

    with open("diabetes_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("[SUCCESS] Diabetes Model Saved -> diabetes_model.pkl")

except Exception as e:
    print(f"[ERROR] Diabetes Model Failed: {e}")


print("\n[DONE] All models trained and saved as .pkl files in the current directory.")