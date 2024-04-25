import streamlit as st
from fpdf import FPDF

def create_pdf(cards):
    pdf = FPDF(unit='mm', format='A4')

    # Calculate card dimensions and margins
    card_width = (pdf.w - 4) / 2  # 2 cards per row, 2mm margin on each side
    card_height = (pdf.h - 10) / 4  # 4 rows of cards, 2mm margin on top and bottom, and 1mm between rows
    margin = 2

    logo_width = 15
    logo_path = 'images/logo1.png'

    # Create a page for questions
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Draw the vertical separator line
    pdf.line(pdf.w / 2, margin, pdf.w / 2, pdf.h - margin)

    for index in range(min(8, len(cards))):  # Generate up to 8 cards
        question = cards[index][0]
        x = margin + (index % 2) * (card_width + margin)
        y = margin + (index // 2 % 4) * (card_height + margin)
        pdf.set_xy(x, y)

        # Add the logo to the card
        logo_x = x + (card_width - logo_width) / 2
        logo_y = y + card_height - logo_width - margin
        pdf.image(logo_path, logo_x, logo_y, logo_width)

        pdf.set_font("Arial", size=8)
        pdf.set_xy(x + 5, y + 5)
        pdf.cell(card_width - 10, 10, f"Q {index + 1}:", ln=True)
        pdf.set_font("Arial", size=8)
        pdf.set_xy(x + 5, y + 10)
        pdf.multi_cell(card_width - 10, 5, question, align='J')

        # Draw horizontal separator lines between the cards
        if (index + 1) % 2 == 0 and index < 7:
            separator_y = y + card_height
            pdf.line(margin, separator_y, pdf.w - margin, separator_y)

    # Create a page for answers, swap positions as specified
    pdf.add_page()
    swap_map = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6}  # Swap mapping

    # Draw the vertical separator line
    pdf.line(pdf.w / 2, margin, pdf.w / 2, pdf.h - margin)

    for index in range(min(8, len(cards))):
        swapped_index = swap_map[index]
        answer = cards[swapped_index][1]
        x = margin + (index % 2) * (card_width + margin)
        y = margin + (index // 2 % 4) * (card_height + margin)
        pdf.set_xy(x, y)

        # Add the logo to the card
        logo_x = x + (card_width - logo_width) / 2
        logo_y = y + card_height - logo_width - margin
        pdf.image(logo_path, logo_x, logo_y, logo_width)

        pdf.set_font("Arial", size=8)
        pdf.set_xy(x + 5, y + 5)
        pdf.cell(card_width - 10, 10, f"R {swapped_index + 1}:", ln=True)
        pdf.set_font("Arial", size=8)
        pdf.set_xy(x + 5, y + 10)
        pdf.multi_cell(card_width - 10, 5, answer, align='J')

        # Draw horizontal separator lines between the cards
        if (index + 1) % 2 == 0 and index < 7:
            separator_y = y + card_height
            pdf.line(margin, separator_y, pdf.w - margin, separator_y)

    pdf_bytes = pdf.output(dest='S')
    return pdf_bytes



import tempfile
import os

def main():
    st.title("Générateur de cartes flash Anki")
    st.subheader("Entrez 8 questions et 8 réponses pour générer des cartes flash.")

    with st.form(key='cards_form'):
        # Create a list to store questions and answers
        questions = []
        answers = []

        # Use columns to place questions and answers side by side
        for i in range(8):
            col1, col2 = st.columns(2)
            with col1:
                question = st.text_input(f"Question {i+1}:", key=f"q{i}")
            with col2:
                answer = st.text_input(f"Réponse {i+1}:", key=f"a{i}")
            questions.append(question)
            answers.append(answer)

        submitted = st.form_submit_button("Ajouter les cartes")
        if submitted:
            # Store pairs of questions and answers in session state
            if 'cards' not in st.session_state:
                st.session_state['cards'] = []
            for q, a in zip(questions, answers):
                st.session_state['cards'].append((q, a))
            st.success("Cartes ajoutées! Vous pouvez générer le PDF maintenant.")

    if st.button("Générer le PDF"):
        if 'cards' in st.session_state and len(st.session_state['cards']) >= 8:
            pdf_bytes = create_pdf(st.session_state['cards'])
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp.seek(0)
                file_size = os.path.getsize(tmp.name)
                with open(tmp.name, 'rb') as f:
                    pdf_content = f.read()
                st.success("PDF généré! Vous pouvez maintenant le télécharger.")
                st.download_button(label="Télécharger le PDF",
                                   data=pdf_content,
                                   file_name="cartes_flash_anki.pdf",
                                   mime='application/pdf')
                os.remove(tmp.name)
        else:
            st.error("Veuillez ajouter suffisamment de cartes pour générer un PDF (au moins 8).")



if __name__ == "__main__":
    main()
