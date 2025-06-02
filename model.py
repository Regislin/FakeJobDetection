import pandas as pd
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

df = pd.read_csv('Jobs.csv')


text_features = ['job_title', 'job_description', 'requirements', 'benefits']
df['combined_text'] = df[text_features].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
X = df['combined_text']
y = df['is_real']


vectorizer = TfidfVectorizer(max_features=1000)
X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

model = CatBoostClassifier(iterations=500, 
                          learning_rate=0.1, 
                          depth=6, 
                          random_seed=42,
                          verbose=100)
model.fit(X_train, y_train)


joblib.dump(model, 'job_model_catboost.pkl')
joblib.dump(vectorizer, 'vectorizer_catboost.pkl')