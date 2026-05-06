import streamlit as st


# --- PAGE SETUP ---
about_page = st.Page(
    "pages/about_project.py",
    title="About Project",
    icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    "pages/WinForLife.py",
    title="Italia WinforLife",
    icon=":material/flag:",
)
project_2_page = st.Page(
    "pages/Kaskada.py",
    title="Polonia Kaskada",
    icon=":material/flag:",
)
project_4_page = st.Page(
    "pages/UngariaPutto.py",
    title="UngariaPutto",
    icon=":material/flag:",
)
project_5_page = st.Page(
    "pages/genloto5.py",
    title="Generare variante",
    icon=":material/rule:",
) 
project_6_page = st.Page(
    "pages/convert.py",
    title="Convertire variante",
    icon=":material/rule:",
)
project_7_page = st.Page(
    "pages/verifica.py",
    title="Verificare castiguri",
    icon=":material/rule:",
)
project_8_page = st.Page(
    "pages/analiza_loto_extinsa_pro.py",
    title="Analiza Loto Extinsă",
    icon=":material/rule:",
)
final_page = st.Page(
    "pages/SelectLotto.py",
    title="Final Project",
    icon=":material/insights:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "INFO": [about_page],
        "PROJECTS(BETA)": [project_1_page, project_2_page, project_4_page],
        "TOOLS": [project_5_page, project_6_page, project_7_page, project_8_page],
        "FINAL": [final_page]
    }
)

# --- SHARED ON ALL PAGES ---
st.logo("assets/lotto.png")
st.sidebar.markdown("This is one of Georgeo07's projects. ❤️")


# --- RUN NAVIGATION ---
pg.run()