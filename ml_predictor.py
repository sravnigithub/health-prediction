import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
MODEL_PATH = "model.pkl"

# Medical reference ranges
GLUCOSE_MIN = 60.0
GLUCOSE_MAX = 149.9
CHOLESTEROL_MIN = 60.0
CHOLESTEROL_MAX = 199.9
HB_MIN = 12.0
HB_MAX = 17.5

LABEL_NORMAL = "Normal"
LABEL_ABNORMAL = "Requires Medical Attention"

# Global model instance
model: RandomForestClassifier | None = None


# ── Dataset generation ───────────────────────────────────────────────────────
def _generate_dataset() -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a realistic synthetic dataset of 1000 patients.
    Features: glucose, haemoglobin, cholesterol
    Labels: 0 = Normal, 1 = Abnormal
    """
    np.random.seed(42)
    rows = []

    # 600 Normal patients
    for i in range(600):
        glucose = np.random.uniform(GLUCOSE_MIN + 10, GLUCOSE_MAX - 10)
        cholesterol = np.random.uniform(CHOLESTEROL_MIN + 60, CHOLESTEROL_MAX - 5)
        haemoglobin = np.random.uniform(HB_MIN, HB_MAX)
        rows.append([glucose, haemoglobin, cholesterol, 0])

    # 400 Abnormal patients — varied abnormality types
    for i in range(400):
        case = i % 4
        if case == 0:
            # High glucose (diabetic range)
            glucose = np.random.uniform(150, 280)
            cholesterol = np.random.uniform(100, 250)
        elif case == 1:
            # Low glucose (hypoglycemia)
            glucose = np.random.uniform(30, 59)
            cholesterol = np.random.uniform(100, 250)
        elif case == 2:
            # High cholesterol
            glucose = np.random.uniform(70, 140)
            cholesterol = np.random.uniform(200, 300)
        else:
            # Low cholesterol
            glucose = np.random.uniform(70, 140)
            cholesterol = np.random.uniform(20, 59)

        # Abnormal haemoglobin (too low or too high)
        hb_base = 9.0 if np.random.rand() > 0.5 else 19.0
        haemoglobin = float(np.clip(hb_base + np.random.uniform(-2, 2), 5, 22))

        rows.append([glucose, haemoglobin, cholesterol, 1])

    df = pd.DataFrame(
        rows, columns=["glucose", "haemoglobin", "cholesterol", "label"]
    ).sample(frac=1, random_state=42).reset_index(drop=True)

    X = df[["glucose", "haemoglobin", "cholesterol"]].values
    y = df["label"].values
    return X, y


# ── Training ─────────────────────────────────────────────────────────────────
def train_model() -> None:
    """
    Train a Random Forest classifier on the synthetic dataset.
    - Evaluates with 5-fold cross-validation
    - Saves the trained model to MODEL_PATH for reuse
    """
    global model
    # Load persisted model if available
    if os.path.exists(MODEL_PATH):
        logger.info("Loading persisted model from %s", MODEL_PATH)
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return

    logger.info("Training new Random Forest model on 1000-sample dataset …")
    X, y = _generate_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",  # handles class imbalance (600 normal vs 400 abnormal)
        random_state=42,
        n_jobs=-1,
    )

    # Cross-validation on training set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="accuracy")
    logger.info(
        "Cross-validation accuracy: %.4f ± %.4f",
        cv_scores.mean(),
        cv_scores.std(),
    )

    clf.fit(X_train, y_train)

    # Test set evaluation
    y_pred = clf.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    logger.info("Test set accuracy: %.4f", test_acc)
    logger.info(
        "Classification report:\n%s",
        classification_report(y_test, y_pred, target_names=["Normal", "Abnormal"]),
    )

    # Feature importances
    features = ["glucose", "haemoglobin", "cholesterol"]
    importances = clf.feature_importances_
    logger.info("Feature importances:")
    for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
        logger.info("  %-15s : %.4f", feat, imp)

    # Persist model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    logger.info("Model saved to %s", MODEL_PATH)
    model = clf


# ── Prediction ───────────────────────────────────────────────────────────────
def _apply_hard_rules(
    glucose: float,
    haemoglobin: float,
    cholesterol: float,
) -> str | None:
    """
    Apply evidence-based medical reference ranges before the ML model.
    Returns a result string if a rule fires, else None.

    Reference ranges:
    Glucose     : 60 – 149 mg/dL (normal fasting)
    Cholesterol : 60 – 199 mg/dL (healthy total)
    Haemoglobin : 12.0 – 17.5 g/dL
    """
    reasons = []
    if glucose >= 150:
        reasons.append(f"glucose {glucose:.1f} ≥ 150 mg/dL (diabetic range)")
    elif glucose < GLUCOSE_MIN:
        reasons.append(f"glucose {glucose:.1f} < 60 mg/dL (hypoglycemia)")

    if cholesterol >= 200:
        reasons.append(f"cholesterol {cholesterol:.1f} ≥ 200 mg/dL (high)")
    elif cholesterol < CHOLESTEROL_MIN:
        reasons.append(f"cholesterol {cholesterol:.1f} < 60 mg/dL (very low)")

    if haemoglobin < HB_MIN:
        reasons.append(f"haemoglobin {haemoglobin:.1f} < 12.0 g/dL (low)")
    elif haemoglobin > HB_MAX:
        reasons.append(f"haemoglobin {haemoglobin:.1f} > 17.5 g/dL (high)")

    if reasons:
        logger.info("Hard rule triggered: %s", "; ".join(reasons))
        return LABEL_ABNORMAL
    return None


def predict_health(
    glucose: float,
    haemoglobin: float,
    cholesterol: float,
) -> str:
    """
    Predict patient health status.
    Decision order:
    1. Hard medical rules → immediate result if any value is out of range
    2. Random Forest model → final prediction with confidence logging

    Returns: "Normal" or "Requires Medical Attention"
    """
    global model
    # Step 1: Hard rules (fast gate — no model needed)
    rule_result = _apply_hard_rules(glucose, haemoglobin, cholesterol)
    if rule_result:
        return rule_result

    # Step 2: ML model
    if model is None:
        logger.warning("Model not initialised — running train_model() now")
        train_model()

    features = np.array([[glucose, haemoglobin, cholesterol]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    confidence = float(max(probability))

    result = LABEL_NORMAL if prediction == 0 else LABEL_ABNORMAL
    logger.info(
        "ML prediction: %s (confidence: %.2f) | inputs: glucose=%.1f, hb=%.1f, cholesterol=%.1f",
        result,
        confidence,
        glucose,
        haemoglobin,
        cholesterol,
    )
    return result


# ── Quick self-test (run file directly) ──────────────────────────────────────
if __name__ == "__main__":
    train_model()
    print("\n── Prediction tests ──")
    cases = [
        (90, 14.0, 170, "Normal"),
        (95, 13.5, 185, "Normal"),
        (180, 10.0, 250, "Abnormal"),
        (55, 13.0, 170, "Abnormal (low glucose)"),
        (100, 11.0, 170, "Abnormal (low Hb)"),
        (100, 14.0, 220, "Abnormal (high cholesterol)"),
        (100, 14.0, 40, "Abnormal (low cholesterol)"),
        (100, 18.0, 170, "Abnormal (high Hb)"),
    ]
    for g, hb, ch, note in cases:
        result = predict_health(g, hb, ch)
        status = "✓" if ("Normal" in result) == ("Normal" in note) else "✗"
        print(f" {status} [{note:30s}] → {result}")
