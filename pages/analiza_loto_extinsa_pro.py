import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter
import io
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

st.set_page_config(page_title="Analiza Loto Extinsă", layout="wide", page_icon="🎯")
st.title("🎯 Analiza Loto Extinsă — Pro")

# ─────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────
uploaded = st.file_uploader("Încarcă fișierul (.csv sau .xlsx)", type=["csv", "xlsx"])

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        xls = pd.ExcelFile(uploaded)
        sheet = st.selectbox("Alege sheet-ul", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet)

    # Validare structură
    if df.shape[1] < 3:
        st.error("❌ Fișierul trebuie să aibă cel puțin o coloană de dată + numere extrase.")
        st.stop()

    all_draws = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
    if all_draws.empty:
        st.error("❌ Nu s-au găsit coloane numerice. Verifică formatul fișierului.")
        st.stop()

    max_nr = int(all_draws.max().max())
    number_counter = Counter()
    for _, row in df.iterrows():
        for n in row[1:]:
            try:
                number_counter[int(n)] += 1
            except (ValueError, TypeError):
                pass

    def get_group_label(n, step=10):
        lower = ((n - 1) // step) * step + 1
        return f"{lower}-{lower + step - 1}"

    st.subheader("📋 Ultimele 3 extrageri")
    st.dataframe(df.tail(3), width='stretch')

    # ─────────────────────────────────────────────
    # TABS
    # ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🤖 Predicție ML",
        "🔢 Combinații",
        "📊 Statistici",
        "🔁 Backtest",
        "📤 Export"
    ])

    # ─────────────────────────────────────────────
    # TAB 1 — PREDICȚIE ML
    # ─────────────────────────────────────────────
    with tab1:
        st.subheader("🤖 Probabilități ML per număr")

        @st.cache_resource(show_spinner="Antrenez modelul ML...")
        def train_model(data_key):
            data_list, max_n = data_key
            data = []
            for draw in data_list:
                appeared = set(draw)
                data.append([1 if n in appeared else 0 for n in range(1, max_n + 1)])
            X = pd.DataFrame(data[:-1])
            y = pd.DataFrame(data[1:])
            base_model = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
            model = MultiOutputClassifier(base_model)
            model.fit(X, y)
            return model, data

        draws_tuple = tuple(
            tuple(int(v) for v in row if pd.notna(v))
            for _, row in all_draws.iterrows()
        )
        model, data = train_model((draws_tuple, max_nr))

        last_draw_vec = np.array(data[-1]).reshape(1, -1)
        probas = model.predict_proba(last_draw_vec)

        pred_results = []
        for i, p in enumerate(probas):
            prob = p[0][1] if len(p[0]) > 1 else float(p[0][0])
            n = i + 1
            freq = number_counter.get(n, 0)
            freq_norm = freq / max(number_counter.values()) if number_counter else 0
            hybrid = round(0.6 * prob + 0.4 * freq_norm, 4)
            pred_results.append({
                "Număr": n,
                "Prob. ML": round(prob, 4),
                "Frecvență": freq,
                "Scor Hibrid": hybrid,
                "Paritate": "Par" if n % 2 == 0 else "Impar",
                "Grupă": get_group_label(n)
            })

        pred_df = pd.DataFrame(pred_results).sort_values("Scor Hibrid", ascending=False).reset_index(drop=True)
        pred_df.index += 1

        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(pred_df, width='stretch')
        with col2:
            top10 = pred_df.head(10)
            fig = px.bar(
                top10, x="Număr", y="Scor Hibrid", color="Scor Hibrid",
                color_continuous_scale="Viridis", title="Top 10 numere după scor hibrid",
                template="plotly_dark"
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width='stretch')
        st.caption("Selectează câte numere vrei din top scor hibrid")
        top_k = st.slider("Număr recomandat de numere", 3, 24, 12)
        top_nums = [int(n) for n in pred_df.head(top_k)['Număr'].values]
        st.info(f"🏆 **Top {top_k} numere recomandate:** {top_nums}")
        
    # ─────────────────────────────────────────────
    # TAB 2 — COMBINAȚII
    # ─────────────────────────────────────────────
    with tab2:
        st.subheader("🔢 Top combinații frecvente")
        col_a, col_b = st.columns(2)
        with col_a:
            selected_size = st.slider("Dimensiunea combinației:", 2, 8, 5)
        with col_b:
            min_freq = st.number_input("Frecvență minimă:", min_value=1, value=2)

        if selected_size > 6 and len(df) > 200:
            st.warning("⚠️ Dimensiune > 6 cu multe extrageri poate fi lentă. Recomand max 6.")

        combo_counter = Counter()
        for _, row in df.iterrows():
            try:
                numbers = sorted([int(v) for v in row[1:] if pd.notna(v)])
                for combo in combinations(numbers, selected_size):
                    combo_counter[combo] += 1
            except (ValueError, TypeError):
                pass

        combo_data = [
            {
                "Combinație": str(combo),
                "Frecvență": freq,
                "Scor total": sum(number_counter.get(n, 0) for n in combo)
            }
            for combo, freq in combo_counter.items() if freq >= min_freq
        ]

        if combo_data:
            combo_df = pd.DataFrame(combo_data).sort_values("Frecvență", ascending=False).head(15).reset_index(drop=True)
            combo_df.index += 1
            st.dataframe(combo_df, width='stretch')
        else:
            st.warning("⚠️ Nicio combinație nu îndeplinește criteriul de frecvență minimă.")
            combo_df = pd.DataFrame(columns=["Combinație", "Frecvență", "Scor total"])

        st.subheader("🎯 Combinațiile extreme (după scor total)")
        if combo_counter:
            best_combo = max(combo_counter, key=lambda x: sum(number_counter.get(n, 0) for n in x))
            worst_combo = min(combo_counter, key=lambda x: sum(number_counter.get(n, 0) for n in x))
            st.success(f"✅ Cea mai probabilă: **{best_combo}** — Scor: {sum(number_counter.get(n,0) for n in best_combo)} — Frecvență: {combo_counter[best_combo]}")
            st.error(f"❌ Cea mai improbabilă: **{worst_combo}** — Scor: {sum(number_counter.get(n,0) for n in worst_combo)} — Frecvență: {combo_counter[worst_combo]}")

    # ─────────────────────────────────────────────
    # TAB 3 — STATISTICI
    # ─────────────────────────────────────────────
    with tab3:
        st.subheader("⚙️ Analiză extrageri individuale")

        extract_analysis = []
        total_pare = total_impare = total_mici = total_mari = 0
        grup_counter = Counter()

        for index, row in df.iterrows():
            try:
                numbers = [int(v) for v in row[1:] if pd.notna(v)]
            except (ValueError, TypeError):
                continue
            pare = sum(1 for n in numbers if n % 2 == 0)
            impare = len(numbers) - pare
            mici = sum(1 for n in numbers if n <= max_nr / 2)
            mari = len(numbers) - mici
            grupuri = Counter(get_group_label(n) for n in numbers)
            extract_analysis.append({
                "Extragere": index + 1,
                "Pare": pare, "Impare": impare,
                "Mici": mici, "Mari": mari,
                **grupuri
            })
            total_pare += pare; total_impare += impare
            total_mici += mici; total_mari += mari
            grup_counter.update(grupuri)

        extract_df = pd.DataFrame(extract_analysis).fillna(0)
        st.dataframe(extract_df, width='stretch')

        st.subheader("📊 Distribuție generală")
        distrib_df = pd.DataFrame({
            "Categorie": ["Pare", "Impare", "Mici", "Mari"],
            "Total": [total_pare, total_impare, total_mici, total_mari]
        })
        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(distrib_df, x="Categorie", y="Total", color="Categorie",
                             template="plotly_dark", title="Distribuție globală")
            st.plotly_chart(fig_bar, width='stretch')
        with col2:
            fig_pie = px.pie(distrib_df, names="Categorie", values="Total",
                             template="plotly_dark", title="Proporție globală")
            st.plotly_chart(fig_pie, width='stretch')

        st.subheader("📌 Tendințe generale")
        total_row = {
            "Total extrageri": len(df),
            "Total pare": total_pare, "Total impare": total_impare,
            "Total mici": total_mici, "Total mari": total_mari,
            "Grupa dominantă": grup_counter.most_common(1)[0][0] if grup_counter else "N/A"
        }
        st.table(pd.DataFrame([total_row]))

        st.subheader("📊 Analiza fiecărui număr individual (cu Gap)")
        number_stats = []
        draw_list = [
            [int(v) for v in row[1:] if pd.notna(v)]
            for _, row in df.iterrows()
        ]
        for n in sorted(number_counter):
            # Gap: câte extrageri de la ultima apariție
            gap = next(
                (i for i, draw in enumerate(reversed(draw_list)) if n in draw),
                len(draw_list)
            )
            number_stats.append({
                "Număr": n,
                "Apariții": number_counter[n],
                "Gap curent": gap,
                "Paritate": "Par" if n % 2 == 0 else "Impar",
                "Mărime": "Mic" if n <= max_nr / 2 else "Mare",
                "Grupă": get_group_label(n)
            })
        number_df = pd.DataFrame(number_stats)
        st.dataframe(number_df, width='stretch')

        st.subheader("🔥 Heatmap frecvențe per număr")
        fig_freq = px.bar(
            number_df.sort_values("Gap curent", ascending=False).head(20),
            x="Număr", y="Gap curent", color="Gap curent",
            color_continuous_scale="Reds", template="plotly_dark",
            title='Top 20 numere cu cel mai mare gap (restante)'
        )
        st.plotly_chart(fig_freq, width='stretch')

    # ─────────────────────────────────────────────
    # TAB 4 — BACKTEST
    # ─────────────────────────────────────────────
    with tab4:
        st.subheader("🔁 Backtest — Simulare predicții pe extrageri istorice")
        n_test = st.slider("Număr extrageri de testat:", 5, min(100, len(df) - 10), 5)
        top_k = st.slider("Câte numere să prezici per tragere:", 3, 10, 3)

        backtest_results = []
        with st.spinner(f"⏳ Rulez backtest pe {n_test} extrageri..."):
            progress = st.progress(0)
            indices = [i for i in range(len(data) - n_test - 1, len(data) - 1) if i >= 10]
            for step, i in enumerate(indices):
                train_X = pd.DataFrame(data[:i])
                train_y = pd.DataFrame(data[1:i+1])
                bt_model = MultiOutputClassifier(
                    RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
                )
                bt_model.fit(train_X, train_y)
                vec = np.array(data[i]).reshape(1, -1)
                bt_probas = bt_model.predict_proba(vec)
                bt_scores = []
                for j, p in enumerate(bt_probas):
                    prob = p[0][1] if len(p[0]) > 1 else float(p[0][0])
                    bt_scores.append((j + 1, prob))
                predicted_nums = set(int(n) for n, _ in sorted(bt_scores, key=lambda x: -x[1])[:top_k])
                actual_nums = set(j + 1 for j, v in enumerate(data[i + 1]) if v == 1)
                hits = len(predicted_nums & actual_nums)
                backtest_results.append({
                    "Extragere #": i + 1,
                    "Prezise": str(sorted(predicted_nums)),
                    "Reale": str(sorted(actual_nums)),
                    "Nimeriri": hits,
                    "Din": top_k
                })
                progress.progress((step + 1) / len(indices))
            progress.empty()

        bt_df = pd.DataFrame(backtest_results)
        avg_hits = bt_df["Nimeriri"].mean()
        random_expected = top_k * (len(number_counter) / max_nr)

        col1, col2, col3 = st.columns(3)
        col1.metric("Media nimeriri ML", f"{avg_hits:.2f}")
        col2.metric("Așteptat aleator", f"{random_expected:.2f}")
        col3.metric("Avantaj față de aleator", f"{avg_hits - random_expected:+.2f}")

        st.dataframe(bt_df, width='stretch')

        fig_bt = px.line(bt_df, x="Extragere #", y="Nimeriri",
                         markers=True, template="plotly_dark",
                         title=f"Nimeriri per extragere (top {top_k} numere)")
        fig_bt.add_hline(y=avg_hits, line_dash="dash", line_color="green",
                         annotation_text=f"Medie ML: {avg_hits:.2f}")
        fig_bt.add_hline(y=random_expected, line_dash="dot", line_color="red",
                         annotation_text=f"Aleator: {random_expected:.2f}")
        st.plotly_chart(fig_bt, width='stretch')

    # ─────────────────────────────────────────────
    # TAB 5 — EXPORT
    # ─────────────────────────────────────────────
    with tab5:
        st.subheader("📤 Exportă toate rezultatele în Excel")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pred_df.to_excel(writer, index=False, sheet_name="Predicție ML")
            if not combo_df.empty:
                combo_df.to_excel(writer, index=False, sheet_name="Top Combinații")
            extract_df.to_excel(writer, index=False, sheet_name="Analiză Extrageri")
            pd.DataFrame([total_row]).to_excel(writer, index=False, sheet_name="Tendințe Generale")
            number_df.to_excel(writer, index=False, sheet_name="Numere Individuale")
            if not bt_df.empty:
                bt_df.to_excel(writer, index=False, sheet_name="Backtest")

            # Auto-width coloane
            for sheet_name, sheet_df in [
                ("Predicție ML", pred_df),
                ("Analiză Extrageri", extract_df),
                ("Numere Individuale", number_df),
            ]:
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(sheet_df.columns):
                    width = max(len(str(col)), sheet_df[col].astype(str).map(len).max()) + 2
                    worksheet.set_column(i, i, min(width, 40))

        st.download_button(
            "📥 Descarcă Excel complet",
            data=output.getvalue(),
            file_name="analiza_loto_extinsa_pro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ Fișierul conține 6 sheet-uri: Predicție ML, Top Combinații, Analiză Extrageri, Tendințe Generale, Numere Individuale, Backtest.")

else:
    st.info("🔼 Încarcă un fișier .csv sau .xlsx pentru a începe analiza.")
