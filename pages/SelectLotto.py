import streamlit as st
import pandas as pd
import numpy as np
import ast
import pytz
import time
import os
import warnings
from datetime import datetime
from collections import Counter
from itertools import combinations

from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier, AdaBoostClassifier,
    StackingClassifier, BaggingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIG per loterie
# ─────────────────────────────────────────────
LOTO_CONFIG = {
    "Romania 6/49":         {"file": "loto649.csv",   "nums": 6, "max_num": 49},
    "Romania - Joker":      {"file": "lotoJoker.csv", "nums": 5, "max_num": 45},
    "Romania 5/40":         {"file": "loto540.csv",   "nums": 5, "max_num": 40},
}
SEED = 2024

# ─────────────────────────────────────────────
# STILIZARE
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        div.stButton > button {
            background-color: #FF3131;
            color: black;
            font-size: 20px;
            font-family: "Comic Sans MS", sans-serif;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 0 10px #FF3131, 0 0 20px #FF3131, 0 0 30px #FF3131;
        }
        div.stButton > button:hover {
            background-color: #FF5733;
            box-shadow: 0 0 20px #FF5733, 0 0 30px #FF5733, 0 0 40px #FF5733;
        }
        .neon-table { border-collapse: collapse; width: 100%; }
        .neon-table th, .neon-table td {
            padding: 10px; text-align: center; border: 1px solid #000;
        }
        .neon-table th {
            background-color: #00FFFF; color: black; font-size: 18px;
            font-family: "Verdana", sans-serif;
            text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #00FFFF;
        }
        .neon-table td {
            color: white; background-color: #222;
            text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title('🎰 LOTTO PREDICTION')

# ─────────────────────────────────────────────
# SELECTARE LOTERIE + INCARCARE DATE
# ─────────────────────────────────────────────
st.subheader("Selectează și încarcă baza de date")

selected_label = st.selectbox("📂 **Alege loteria:**", list(LOTO_CONFIG.keys()))
cfg = LOTO_CONFIG[selected_label]
file_path  = cfg["file"]
nums_req   = cfg["nums"]
max_num    = cfg["max_num"]

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try:
    last_mod = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%d %B %Y, ora %H:%M")
except FileNotFoundError:
    last_mod = "nedisponibilă"

try:
    data = load_data(file_path)
    st.write(f"📂 **Fișier:** `{file_path}`  🕒 **Ultima modificare:** {last_mod}")
    st.dataframe(data.tail(5))
except FileNotFoundError:
    st.error("❌ Fișierul nu a fost găsit. Verifică dacă există în folderul curent.")
    st.stop()

X = data.iloc[:, 0].values.reshape(-1, 1)
y = data.iloc[:, 1:].values

most_recent_draw    = data.iloc[-1, 0]
most_recent_numbers = data.iloc[-1, 1:].tolist()

st.markdown(
    f"<h2 style='color:#FFFF00;font-size:20px;"
    f"text-shadow:0 0 10px #FFFF00,0 0 20px #FFFF00,0 0 30px #FFFF00;'>"
    f"📌 Ultima Extragere: {most_recent_draw} | Numere: {most_recent_numbers}</h2>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# MODELE
# ─────────────────────────────────────────────
def build_models():
    return {
        'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=SEED),
        'Stacking': StackingClassifier(
            estimators=[
                ('rf', RandomForestClassifier(n_estimators=10, random_state=SEED)),
                ('dt', DecisionTreeClassifier(random_state=SEED))
            ],
            final_estimator=LogisticRegression()
        ),
        'SVM':          SVC(random_state=SEED, probability=True),
        'Bagging':      BaggingClassifier(n_estimators=50, random_state=SEED),
        'CatBoost':     CatBoostClassifier(verbose=0, random_state=SEED),
        'MLP':          MLPClassifier(random_state=SEED, max_iter=50),
        #'XGBoost':      XGBClassifier(
            #n_estimators=200, learning_rate=0.1, max_depth=6,
            #subsample=0.8, colsample_bytree=0.8,
            #random_state=SEED, eval_metric='logloss', verbosity=0
        #)
    }

# ─────────────────────────────────────────────
# ANTRENARE + PREDICTIE
# ─────────────────────────────────────────────
def predict_numbers_and_accuracy(models, X, y, nums_req, max_num):
    st.subheader("Antrenarea modelelor de Machine Learning")
    progress_bar = st.progress(0)
    status_text  = st.empty()
    status_text.text('Se calculează predicțiile, așteptați...')

    model_predictions = {}
    num_models = len(models)

    for i, (model_name, model) in enumerate(models.items(), start=1):
        status_text.text(f"⚙️ Antrenez: {model_name}  ({i}/{num_models})")
        accuracies  = []
        predictions = []

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED
        )

        for j in range(y.shape[1]):
            y_col = y_train[:, j]
            if model_name == 'XGBoost':
                model.fit(X_train, y_col - 1)
                y_pred_raw = model.predict(X_test)
                y_pred = y_pred_raw + 1
            else:
                model.fit(X_train, y_col)
                y_pred = model.predict(X_test)

            accuracies.append(accuracy_score(y_test[:, j], y_pred))

            next_x = np.array([[X.max() + 1]])
            if model_name == 'XGBoost':
                pred = int(model.predict(next_x).squeeze()) + 1
            else:
                pred = int(model.predict(next_x).squeeze())
            predictions.append(pred)

        # Numere unice în intervalul valid
        unique_preds = sorted(set(p for p in predictions if 1 <= p <= max_num))
        rng = np.random.default_rng(SEED)
        pool = list(set(range(1, max_num + 1)) - set(unique_preds))
        while len(unique_preds) < nums_req and pool:
            pick = int(rng.choice(pool))
            unique_preds.append(pick)
            pool.remove(pick)
        unique_preds = sorted(unique_preds[:nums_req])

        mean_acc = round(np.mean(accuracies) * 100, 2)
        model_predictions[model_name] = {
            'Numere prezise': unique_preds,
            'Acuratețe (%)': mean_acc
        }

        progress_bar.progress(i / num_models)
        time.sleep(0.05)

    status_text.text('✅ Gata!')
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()
    return model_predictions

# ─────────────────────────────────────────────
# PREDICTIE FINALA prin frecventa
# ─────────────────────────────────────────────
def compute_final_prediction(predictions_df, top_n=24):
    all_numbers = []
    for numere in predictions_df['Numere prezise']:
        try:
            lst = ast.literal_eval(str(numere)) if isinstance(numere, str) else numere
            all_numbers.extend(lst)
        except Exception:
            pass
    if not all_numbers:
        return []
    freq = Counter(all_numbers)
    return [int(n) for n, _ in freq.most_common(top_n)]

# ─────────────────────────────────────────────
# TAB-URI
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔮 Predicții ML", "📊 Statistici frecvență", "✅ Verificare potriviri"])

# ══════════════ TAB 1 ══════════════
with tab1:
    if st.button('🚀 Generează predicții ML'):
        models = build_models()
        predictions = predict_numbers_and_accuracy(models, X, y, nums_req, max_num)
        pred_df = pd.DataFrame(predictions).T.reset_index()
        pred_df.columns = ['Model', 'Numere prezise', 'Acuratețe (%)']
        pred_df.index   = pred_df.index + 1

        st.session_state['saved_predictions'] = pred_df
        pred_df.to_csv('predictions_temp.csv', index=False)

    if 'saved_predictions' in st.session_state:
        st.subheader("📋 Predicții per model")
        st.table(st.session_state['saved_predictions'])

        if st.button('🎯 Calculează varianta finală'):
            final = compute_final_prediction(st.session_state['saved_predictions'])
            st.session_state['final_numbers'] = final

    if 'final_numbers' in st.session_state:
        fn = st.session_state['final_numbers']
        st.markdown(
            f"<h2 style='color:#39FF14;font-size:25px;"
            f"text-shadow:0 0 10px #39FF14,0 0 20px #39FF14,0 0 30px #39FF14;'>"
            f"📌 VARIANTA FINALĂ: {fn}</h2>",
            unsafe_allow_html=True
        )
        st.info(f"Sunt afișate {len(fn)} numere în ordinea descrescătoare a șansei de apariție.")

# ══════════════ TAB 2 ══════════════
with tab2:
    st.subheader("📊 Frecvența istorică a numerelor")
    all_drawn = y.flatten()
    freq_series = pd.Series(all_drawn).value_counts().sort_index()

    freq_df = pd.DataFrame({
        'Număr': freq_series.index,
        'Apariții': freq_series.values,
        'Frecvență (%)': (freq_series.values / len(data) * 100).round(2)
    })

    # Gap mediu (câte trageri în medie între apariții)
    gaps = {}
    for num in range(1, max_num + 1):
        positions = np.where(y == num)[0]
        if len(positions) > 1:
            gaps[num] = round(np.diff(positions).mean(), 1)
        else:
            gaps[num] = None

    freq_df['Gap mediu'] = freq_df['Număr'].map(gaps)
    freq_df['Ultima apariție (extragere)'] = freq_df['Număr'].apply(
        lambda n: int(data.iloc[np.where(y == n)[0][-1], 0]) if len(np.where(y == n)[0]) > 0 else '-'
    )
    st.dataframe(freq_df, width='stretch')

    # Top 10 cele mai frecvente
    top10 = freq_df.nlargest(10, 'Apariții')
    st.markdown("**🔥 Top 10 numere calde:**  " + "  |  ".join(f"`{int(n)}`" for n in top10['Număr']))

    cold10 = freq_df.nsmallest(10, 'Apariții')
    st.markdown("**❄️ Top 10 numere reci:**  " + "  |  ".join(f"`{int(n)}`" for n in cold10['Număr']))

# ══════════════ TAB 3 ══════════════
with tab3:
    st.subheader("✅ Verificare potriviri istorice")

    if 'final_numbers' in st.session_state:
        user_numbers = st.session_state['final_numbers']
        st.write(f"**Variantă verificată:** `{user_numbers}`")

        total = len(data)
        matches = {i: 0 for i in range(2, 14)}

        for _, row in data.iterrows():
            extracted = row[1:].tolist()
            cnt = len(set(user_numbers) & set(extracted))
            if 2 <= cnt <= 13:
                matches[cnt] += 1

        rows = []
        for i in range(3, 14):
            if matches[i] > 0:
                prob = matches[i] / total * 100
                rows.append({'Potriviri': i, 'De câte ori': matches[i], 'Probabilitate (%)': f"{prob:.2f}%"})

        if rows:
            st.table(pd.DataFrame(rows))
        else:
            st.info("Nu există potriviri de 3+ numere în istoricul disponibil.")
    else:
        st.info("⚠️ Generează mai întâi predicțiile și calculează varianta finală în Tab 1.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
tz  = pytz.timezone('Europe/Bucharest')
now = datetime.now(tz).strftime("%d-%m-%Y")
st.subheader(f"🕒 Baza de date actualizată pentru tragerea din {now}")