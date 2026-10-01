import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE_DIR = Path(__file__).resolve().parent.parent

df = pd.read_csv(BASE_DIR / "data" / "products.csv")

X_train, X_test, y_train, y_test = train_test_split(
    df["description"], df["category"],
    test_size=0.25, random_state=42, stratify=df["category"]
)

model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), lowercase=True, stop_words=["fresh", "export", "grade", "bulk", "pack"]),
    LogisticRegression(max_iter=1000, class_weight="balanced"),
)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test), zero_division=0))

(BASE_DIR / "models").mkdir(exist_ok=True)
joblib.dump(model, BASE_DIR / "models" / "classifier.joblib")

print(model.predict(["frozen mango pulp in drums"]))
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, df["description"], df["category"], cv=4)
print("CV accuracy:", scores.mean().round(2))
from sklearn.pipeline import make_pipeline, make_union

features = make_union(
    TfidfVectorizer(ngram_range=(1, 2), lowercase=True, stop_words=["fresh", "export", "grade", "bulk", "pack"]),
    TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True),
)

model = make_pipeline(features, LogisticRegression(max_iter=1000, class_weight="balanced"))
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix

pred = cross_val_predict(model, df["description"], df["category"], cv=4)
wrong = df[pred != df["category"]].copy()
wrong["predicted"] = pred[pred != df["category"]]
print(wrong.to_string())

labels = sorted(df["category"].unique())
print(pd.DataFrame(confusion_matrix(df["category"], pred, labels=labels), index=labels, columns=labels))