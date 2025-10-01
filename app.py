import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# ------------------------------------------------------
# HLAVNÍ APLIKACE
# ------------------------------------------------------
st.set_page_config(page_title="Body na kružnici", layout="wide")

st.title("📐 Body na kružnici")

# --- VSTUPY ---
st.sidebar.header("Parametry kružnice")
x0 = st.sidebar.number_input("Souřadnice středu X", value=0.0)
y0 = st.sidebar.number_input("Souřadnice středu Y", value=0.0)
r = st.sidebar.number_input("Poloměr kružnice", value=5.0, min_value=0.1)
n = st.sidebar.number_input("Počet bodů", value=8, min_value=1, step=1)
color = st.sidebar.color_picker("Barva bodů", "#ff0000")

# --- VÝPOČET BODŮ ---
theta = np.linspace(0, 2*np.pi, int(n), endpoint=False)
x = x0 + r * np.cos(theta)
y = y0 + r * np.sin(theta)

# --- GRAF ---
fig, ax = plt.subplots()
ax.set_aspect("equal", adjustable="datalim")
ax.scatter(x, y, c=color, label="Body")
ax.add_artist(plt.Circle((x0, y0), r, fill=False, linestyle="--"))
ax.axhline(0, color="black", linewidth=0.5)
ax.axvline(0, color="black", linewidth=0.5)

# popisky os
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")
ax.legend()
st.pyplot(fig)

# --- INFORMACE ---
st.subheader("ℹ️ Informace o autorovi a projektu")
st.write("""
**Autor:** Jan Novák  
**Kontakt:** jan.novak@vut.cz  
**Použité technologie:** Python, Streamlit, matplotlib, fpdf  
""")

# --- PDF EXPORT ---
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Body na kruznici - VUT FAST", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, f"Stred: ({x0}, {y0})", ln=True)
    pdf.cell(200, 10, f"Polomer: {r} m", ln=True)
    pdf.cell(200, 10, f"Pocet bodu: {n}", ln=True)
    pdf.cell(200, 10, f"Barva bodu: {color}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Autor: Jan Novák", ln=True)
    pdf.cell(200, 10, "Kontakt: jan.novak@vut.cz", ln=True)

    return pdf.output(dest="S").encode("latin-1")

if st.button("📄 Exportovat do PDF"):
    pdf_bytes = export_pdf()
    st.download_button("Stáhnout PDF", data=pdf_bytes, file_name="kruznice.pdf")

