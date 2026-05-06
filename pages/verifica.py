import streamlit as st
import pandas as pd

st.title("Verificare Numere Extrase - Generalizat")

# Încărcarea fișierului
uploaded = st.file_uploader("Încarcă fișierul (.csv sau .xlsx)", type=["csv", "xlsx"])

if uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
            st.success("Fișier CSV încărcat cu succes")
        elif uploaded.name.endswith(".xlsx"):
            xls = pd.ExcelFile(uploaded, engine='openpyxl')
            sheet = st.selectbox("Alege sheet-ul", xls.sheet_names)
            df = pd.read_excel(xls, sheet_name=sheet)
            st.success(f"Fișier Excel încărcat, sheet selectat: {sheet}")
    
        st.dataframe(df.tail(20))

        # Detectarea automată a coloanelor cu numere (excludem "Round")
        columns = [col for col in df.columns if col.lower() != "round"]

        if columns:
            # Afișarea coloanelor detectate automat
            #st.write("Coloane detectate automat:", ", ".join(columns))

            # Introducerea numerelor utilizatorului
            user_numbers = st.text_input("Introdu numerele separate prin virgulă:")

            # Setarea intervalului pentru potriviri
            min_matches = st.slider("Alege numărul minim de potriviri:", 1, 12, 4)
            max_matches = st.slider("Alege numărul maxim de potriviri:", min_matches, 12, 5)

            if user_numbers:
                try:
                    # Transformarea numerelor într-o listă de întregi
                    user_numbers = list(map(int, user_numbers.split(",")))

                    # Verificarea potrivirilor
                    matches = {i: 0 for i in range(min_matches, max_matches + 1)}
                    for _, row in df.iterrows():
                        extracted_numbers = row[columns].tolist()
                        match_count = len(set(user_numbers) & set(extracted_numbers))
                        if min_matches <= match_count <= max_matches:
                            matches[match_count] += 1

                    # Afișarea rezultatelor
                    st.write("## Rezultate")
                    for i in range(max_matches, min_matches - 1, -1):
                        st.write(f"{i} numere potrivite: {matches[i]} ori")
                except ValueError:
                    st.error("Asigură-te că ai introdus doar numere separate prin virgulă!")
        else:
            st.info("Nu au fost detectate coloane cu numere.")
    except Exception as e:
        st.error(f"Eroare la citirea fișierului: {e}")
else:
    st.info("Încarcă un fișier pentru a începe.")
