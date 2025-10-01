# app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os
import unicodedata

st.set_page_config(page_title="Body na kružnici", layout="wide")
st.title("📐 Body na kružnici")

# --- Uživatelské vstupy ---
st.sidebar.header("Parametry kružnice")
x0 = st.sidebar.number_input("Souřadnice středu X", value=0.0)
y0 = st.sidebar.number_input("Souřadnice středu Y", value=0.0)
r = st.sidebar.number_input("Poloměr kružnice (m)", value=5.0, min_value=0.01, format="%.3f")
n = st.sidebar.number_input("Počet bodů", value=8, min_value=1, step=1)
point_color = st.sidebar.color_picker("Barva bodů", "#ff0000")
center_color = st.sidebar.color_picker("Barva středu", "#0000ff")

st.sidebar.markdown("---")
st.sidebar.header("Informace o autorovi")
author_name = st.sidebar.text_input("Jméno (bude v PDF)", value="Jan Novak")
author_contact = st.sidebar.text_input("Kontakt (email)", value="jan.novak@example.com")

# Volitelné: popisky bodů
label_points = st.sidebar.checkbox("Zobrazit indexy bodů u bodů", value=True)

# --- Funkce: transliterace (pro bezpečný text do PDF) ---
def translit_ascii(s: str) -> str:
    # odstraní diakritiku (převede do ASCII podobné podoby)
    nfkd = unicodedata.normalize('NFKD', s)
    result = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # nahraď znaky neobsažené v latin-1 bezpečným znakem
    try:
        result.encode('latin-1')
    except Exception:
        result = result.encode('latin-1', errors='replace').decode('latin-1')
    return result

# --- Funkce: vytvořit matplotlib fig ---
def create_figure(x0, y0, r, n, point_color, center_color, label_points):
    theta = np.linspace(0, 2*np.pi, int(n), endpoint=False)
    xs = x0 + r * np.cos(theta)
    ys = y0 + r * np.sin(theta)

    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_aspect("equal", adjustable="datalim")

    # kruh (obrys)
    circle = plt.Circle((x0, y0), r, fill=False, linestyle="--", linewidth=1)
    ax.add_patch(circle)

    # body na kružnici
    ax.scatter(xs, ys, c=point_color, s=50, zorder=3, label="body")

    # střed (viditelný)
    ax.scatter([x0], [y0], c=center_color, marker='X', s=120, zorder=4, label="střed")
    ax.annotate(f"({x0:.2f}, {y0:.2f})", xy=(x0, y0), xytext=(6,6), textcoords="offset points", fontsize=9)

    # popisky indexů bodů
    if label_points:
        for i, (xi, yi) in enumerate(zip(xs, ys), start=1):
            ax.text(xi, yi, str(i), fontsize=8, ha='right', va='bottom')

    # osy, grid, popisky s jednotkami
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)
    ax.axvline(0, color="black", linewidth=0.6, zorder=1)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid(True, linestyle=":", linewidth=0.5)

    # rozsah os s rezervou
    margin = max(r * 0.3, 1.0)
    ax.set_xlim(x0 - r - margin, x0 + r + margin)
    ax.set_ylim(y0 - r - margin, y0 + r + margin)

    ax.legend(loc="upper right")
    fig.tight_layout()
    return fig, xs, ys

# --- Vygeneruj graf a tabulku souřadnic ---
fig, xs, ys = create_figure(x0, y0, r, n, point_color, center_color, label_points)
st.pyplot(fig)

coords = [{"#": i+1, "x [m]": round(float(xi), 4), "y [m]": round(float(yi), 4)} for i, (xi, yi) in enumerate(zip(xs, ys))]
st.subheader("Souřadnice bodů")
st.table(coords)

# --- Funkce pro export do PDF (uloží fig do dočasného PNG -> vloží do PDF) ---
def export_pdf_with_image(fig, author_name, author_contact, x0, y0, r, n, point_color, center_color):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    try:
        # uložení obrázku s vyšším DPI, aby v PDF byl ostrý
        fig.savefig(tmp.name, dpi=200, bbox_inches='tight')
        tmp.close()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Body na kruznici - VUT FAST", ln=1, align="C")
        pdf.ln(4)

        pdf.cell(0, 8, f"Autor: {translit_ascii(author_name)}", ln=1)
        pdf.cell(0, 8, f"Kontakt: {translit_ascii(author_contact)}", ln=1)
        pdf.ln(3)

        pdf.cell(0, 8, f"Střed: ({x0}, {y0})", ln=1)
        pdf.cell(0, 8, f"Poloměr: {r} m", ln=1)
        pdf.cell(0, 8, f"Počet bodů: {n}", ln=1)
        pdf.cell(0, 8, f"Barva bodů: {point_color}", ln=1)
        pdf.cell(0, 8, f"Barva středu: {center_color}", ln=1)

        pdf.ln(6)
        # vložíme obrázek (umístíme na střed stránky, šířka 150)
        try:
            pdf.image(tmp.name, x=30, w=150)
        except Exception as e_img:
            # pokud by vložení obrázku selhalo, do PDF napíšeme poznámku
            pdf.ln(4)
            pdf.cell(0, 8, "Chyba při vložení obrázku do PDF.", ln=1)

        # vrátíme PDF jako bytes (bez chybového ukončení)
        pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="replace")
        return pdf_bytes
    finally:
        # bezpečně smažeme dočasný soubor
        try:
            os.remove(tmp.name)
        except Exception:
            pass

# --- Tlačítko pro vygenerování PDF ---
if st.button("📄 Vygenerovat PDF (včetně grafu)"):
    pdf_data = export_pdf_with_image(fig, author_name, author_contact, x0, y0, r, n, point_color, center_color)
    st.download_button("🔽 Stáhnout PDF", data=pdf_data, file_name="kruznice.pdf", mime="application/pdf")
