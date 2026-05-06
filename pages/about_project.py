import streamlit as st

st.title("LOTTO PROJECT 2026")
st.subheader("Despre proiect")

st.html("""
<style>
.premium-about {
    position: relative;
    overflow: hidden;
    padding: 34px 30px;
    border-radius: 24px;
    background:
        radial-gradient(circle at top right, rgba(255, 215, 0, 0.18), transparent 24%),
        radial-gradient(circle at bottom left, rgba(57, 255, 20, 0.08), transparent 22%),
        linear-gradient(135deg, #0b0d12 0%, #121722 45%, #0f1117 100%);
    border: 1px solid rgba(255, 215, 0, 0.20);
    box-shadow: 0 0 35px rgba(255, 215, 0, 0.08);
    margin-top: 10px;
    margin-bottom: 18px;
}

.premium-about::before {
    content: "";
    position: absolute;
    top: -50px;
    right: -40px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,215,0,0.20) 0%, rgba(255,215,0,0.00) 70%);
    pointer-events: none;
}

.premium-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(255, 215, 0, 0.10);
    border: 1px solid rgba(255, 215, 0, 0.20);
    color: #FFD700;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.premium-title {
    font-size: 34px;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 14px;
    color: #FFFFFF;
}

.gold-text {
    color: #FFD700;
    text-shadow: 0 0 16px rgba(255, 215, 0, 0.18);
}

.premium-subtitle {
    font-size: 18px;
    line-height: 1.85;
    color: #E6E6E6;
    margin-bottom: 18px;
}

.premium-question {
    color: #FFF176;
    font-size: 19px;
    font-weight: 800;
    margin-top: 8px;
    margin-bottom: 12px;
}

.premium-note {
    color: #CFCFCF;
    font-size: 16px;
    line-height: 1.8;
    margin-bottom: 20px;
}

.highlight-green {
    color: #39FF14;
    font-weight: 800;
}

.feature-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-top: 24px;
    margin-bottom: 24px;
}

.feature-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(4px);
}

.feature-title {
    color: #FFD700;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 8px;
}

.feature-text {
    color: #D8D8D8;
    font-size: 14px;
    line-height: 1.7;
}

.lotto-banner {
    text-align: center;
    margin-top: 8px;
    padding: 20px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,215,0,0.10), rgba(57,255,20,0.10));
    border: 1px solid rgba(255,255,255,0.08);
}

.lotto-banner-title {
    font-size: 38px;
    font-weight: 900;
    color: #39FF14;
    letter-spacing: 0.05em;
    text-shadow: 0 0 15px rgba(57,255,20,0.30);
}

.lotto-banner-sub {
    margin-top: 6px;
    color: #F4F4F4;
    font-size: 14px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

@media (max-width: 900px) {
    .feature-row {
        grid-template-columns: 1fr;
    }
    .premium-title {
        font-size: 27px;
    }
    .lotto-banner-title {
        font-size: 30px;
    }
}
</style>

<div class="premium-about">
    <div class="premium-badge">Lotto AI Experience 2026</div>

    <div class="premium-title">
        Analizează trecutul. <span class="gold-text">Alege mai inteligent.</span> Joacă mai informat.
    </div>

    <div class="premium-subtitle">
        Acest proiect folosește <span class="highlight-green">Machine Learning</span>,
        analiză statistică și date istorice pentru a genera combinații finale de numere
        într-un mod mai modern, mai captivant și mai bine fundamentat.
    </div>

    <div class="premium-note">
        Nu promitem câștiguri garantate. În schimb, îți oferim o experiență mai interesantă,
        mai structurată și mai „smart” atunci când alegi numerele pentru următoarea tragere.
    </div>

    <div class="premium-question">
        ❓ De ce unele numere apar mai des, iar altele mai rar?
    </div>

    <div class="premium-note">
        Pentru că în spatele fiecărei extrageri există un istoric care poate fi explorat,
        comparat și interpretat. Iar exact aici, analiza datelor transformă jocul
        într-o experiență mai distractivă și mai informată.
    </div>

    <div class="feature-row">
        <div class="feature-box">
            <div class="feature-title">📊 Date istorice</div>
            <div class="feature-text">
                Analizăm extragerile anterioare pentru a identifica frecvențe, variații și distribuții relevante.
            </div>
        </div>

        <div class="feature-box">
            <div class="feature-title">🤖 Modele AI</div>
            <div class="feature-text">
                Folosim algoritmi de Machine Learning pentru a genera combinații bazate pe tipare observabile în date.
            </div>
        </div>

        <div class="feature-box">
            <div class="feature-title">🎯 Selecții finale</div>
            <div class="feature-text">
                Rezultatul este o alegere de numere mai bine structurată, cu un plus de logică și experiență vizuală.
            </div>
        </div>
    </div>

    <div class="lotto-banner">
        <div class="lotto-banner-title">MULT NOROC!</div>
        <div class="lotto-banner-sub">joacă informat • joacă responsabil</div>
    </div>
</div>
""")

if st.button("🎯 Intră în Generator + Calcule + Backtest", type="primary", width="stretch"):
    st.switch_page("pages/SelectLotto.py")

st.info("Jucați responsabil!")
st.info("Accesul recomandat doar persoanelor peste 18 ani!")