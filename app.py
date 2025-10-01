import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os
import unicodedata

# ------------------------------------------------------
# KONFIGURACE APP
# ------------------------------------------------------
st.set_page_config(page_title="Body na kružnici", layout="wide")
st.title("📐 Body na kružnici")

# --- VSTUPY ---
st.sidebar.header("Parametry kružnice")
x0 = st.sidebar.number_input("Souřadnice středu X", value=0.0)
y0 = st.sidebar.number_input("Souřadnice středu Y", value=0.0)
r = st.sidebar.number_input("Poloměr kružnice (m)", value=5.0, min_value=0.01, format="%.3f")
n = st.sidebar.number_input("Počet bodů", value=8, min_value=1, step=1)
point_color = st.sidebar.color_picker("Barva bodů", "#ff0000")
center_color = st.sidebar.color_picker("Barva středu", "#0000ff")

st.sidebar.markdown("---")
st.sidebar.header("Informace o autorovi")
author_name = st.sidebar.text_input("Jméno (do PDF)", value="Jan Jemelka")
author_contact = st.sidebar.text_input("Kontakt (email)", value="277926@vutbr.cz")

# --- POMOCNÁ FUNKCE: transliterace textu (bez diakritiky, bezpečné do PDF) ---
def translit_ascii(s: str) -> str:
    nfkd = unicodedata.normalize('NFKD', s)
    result = "".join([c for c in nfkd if not unicodedata.combining(c)])
    try:
        result.encode('latin-1')
    except Exception:
        result = result.encode('latin-1', errors='replace').decode('latin-1')
    return result

# --- VÝPOČET A GRAF ---
theta = np.linspace(0, 2*np.pi, int(n), endpoint=False)
x = x0 + r * np.cos(theta)
y = y0 + r * np.sin(theta)

fig, ax = plt.subplots(figsize=(6,6))
ax.set_aspect("equal", adjustable="datalim")

# kružnice
ax.add_patch(plt.Circle((x0, y0), r, fill=False, linestyle="--", linewidth=1))

# body
ax.scatter(x, y, c=point_color, s=50, zorder=3, label="body")

# střed
ax.scatter([x0], [y0], c=center_color, marker="X", s=120, zorder=4, label="střed")
ax.annotate(f"({x0:.2f}, {y0:.2f})", xy=(x0, y0), xytext=(6,6), textcoords="offset points", fontsize=9)

# osy
ax.axhline(0, color="black", linewidth=0.6)
ax.axvline(0, color="black", linewidth=0.6)
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")
ax.grid(True, linestyle=":", linewidth=0.5)

margin = max(r * 0.3, 1.0)
ax.set_xlim(x0 - r - margin, x0 + r + margin)
ax.set_ylim(y0 - r - margin, y0 + r + margin)
ax.legend(loc="upper right")
fig.tight_layout()

st.pyplot(fig)

# --- INFORMACE DOLE ---
st.subheader("ℹ️ Informace o autorovi a projektu")
st.write(f"""
**Autor:** {author_name}  
**Kontakt:** {author_contact}  
**Použité technologie:** Python, Streamlit, matplotlib, fpdf  
""")

# --- FUNKCE: EXPORT DO PDF ---
def export_pdf(fig, author_name, author_contact):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    try:
        fig.savefig(tmp.name, dpi=200, bbox_inches="tight")
        tmp.close()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Body na kruznici - VUT FAST", ln=1, align="C")
        pdf.ln(4)

        pdf.cell(0, 8, f"Autor: {translit_ascii(author_name)}", ln=1)
        pdf.cell(0, 8, f"Kontakt: {translit_ascii(author_contact)}", ln=1)
        pdf.ln(3)

        pdf.cell(0, 8, f"Stred: ({x0}, {y0})", ln=1)
        pdf.cell(0, 8, f"Polomer: {r} m", ln=1)
        pdf.cell(0, 8, f"Pocet bodu: {n}", ln=1)


        pdf.ln(6)
        pdf.image(tmp.name, x=30, w=150)

        pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="replace")
        return pdf_bytes
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

# --- TLAČÍTKO ---
if st.button("📄 Vygenerovat PDF (včetně grafu)"):
    pdf_data = export_pdf(fig, author_name, author_contact)
    st.download_button("🔽 Stáhnout PDF", data=pdf_data, file_name="kruznice.pdf", mime="application/pdf")
