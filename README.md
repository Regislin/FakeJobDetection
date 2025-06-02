#  Fake Job Detection using Machine Learning

This project focuses on detecting fake job postings using advanced machine learning techniques, specifically the **CatBoost** classifier. It helps identify fraudulent job listings based on key attributes like job descriptions, titles, and requirements.

---

##  Overview

Fake job scams are increasing, and this project aims to address the issue using data-driven approaches. By training a model on the [Kaggle Fake Job Postings Dataset](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction), we can distinguish between genuine and fake listings with high accuracy.

---

## Tech Stack

- **Python 3**
- **CatBoost** (for classification)
- **Pandas & NumPy** (data handling)
- **Scikit-learn** (evaluation metrics)
- **Matplotlib / Seaborn** (visualizations)
- **NLTK / spaCy** (text preprocessing)
- (Optional: Flask / Streamlit if you added a web interface)

---

## Dataset

- **Source:** [Kaggle: Fake Job Postings Dataset](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction)
- **Description:** Includes job title, location, description, requirements, and label indicating if the job is fake or real.
- **Size:** ~17,000 job postings

---

## Model Used

- **CatBoost Classifier**  
  Chosen for its:
  - Built-in handling of categorical variables
  - High accuracy
  - Fast performance on tabular data

---

## Preprocessing Steps

- Cleaned text fields (description, requirements)
- Removed null and irrelevant data
- Text vectorization using TF-IDF
- Encoded categorical features
- Split dataset into training and testing sets

---

## Performance

| Metric     | Score   |
|------------|---------|
| Accuracy   | 96%     |
| Precision  | 95%     |
| Recall     | 97%     |
| F1-Score   | 96%     |

*(Update the scores based on your actual results)*

---

## How to Run

```bash
# Clone this repository
git clone https://github.com/yourusername/fake-job-detection.git
cd fake-job-detection

# Install dependencies
pip install -r requirements.txt

# Run the script / notebook
python fake_job_detection.py
