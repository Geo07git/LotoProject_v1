import streamlit as st
from itertools import combinations
import time

def generate_optimized_variants(total_numbers=20, variant_size=4, required_common=2):
    all_numbers = list(range(1, total_numbers + 1))
    all_variants = list(combinations(all_numbers, variant_size))

    selected_variants = []
    covered_combinations = set()

    for variant in all_variants:
        variant_set = set(variant)

        if not any(len(variant_set.intersection(existing)) >= required_common for existing in selected_variants):
            selected_variants.append(variant)

            for combination in combinations(variant, required_common):
                covered_combinations.add(frozenset(combination))

        if len(covered_combinations) == len(list(combinations(all_numbers, required_common))):
            break

    return selected_variants

def replace_numbers_with_user_selection(variants, user_numbers):
    """ Înlocuiește numerele generice din variante cu numerele reale selectate de utilizator """
    number_map = {i+1: num for i, num in enumerate(user_numbers)}
    converted_variants = [[number_map[num] for num in variant] for variant in variants]
    return converted_variants

def main():
    st.title('Loto Variants Generator')

    total_numbers = st.number_input('Numărul total de numere (ex: 20)', min_value=5, max_value=50, value=20)
    variant_size = st.number_input('Dimensiunea variantei (ex: 10)', min_value=3, max_value=20, value=4)
    required_common = st.number_input('Numărul minim de numere comune (ex: 8)', min_value=2, max_value=variant_size, value=2)

    st.subheader("Alege numerele dorite")
    
    # Generăm o grilă cu numere pe care utilizatorul le poate selecta
    available_numbers = list(range(1, 50))
    selected_numbers = []
    
    cols = st.columns(5)  # Creăm 5 coloane pentru a forma o grilă de selecție
    for i, num in enumerate(available_numbers):
        if cols[i % 5].checkbox(str(num)):
            selected_numbers.append(num)
    
    if len(selected_numbers) < total_numbers:
        st.warning(f"Selectează exact {total_numbers} numere.")

    # Inițializare variabile în session_state
    if 'variants' not in st.session_state:
        st.session_state['variants'] = []
    if 'converted_variants' not in st.session_state:
        st.session_state['converted_variants'] = []

    if st.button('Generează variante'):
        start_time = time.time()
        variants = generate_optimized_variants(total_numbers=total_numbers, variant_size=variant_size, required_common=required_common)
        st.session_state['variants'] = variants
        total_time = time.time() - start_time
        st.write(f"Număr total de variante generate: {len(variants)}")
        st.write(f"Timp total de generare: {total_time:.2f} secunde")

    if st.button('Înlocuiește numerele generice'):
        if 'variants' in st.session_state and st.session_state['variants']:
            converted_variants = replace_numbers_with_user_selection(st.session_state['variants'], selected_numbers)
            st.session_state['converted_variants'] = converted_variants
            st.write("Variantele convertite:")
            for i, variant in enumerate(converted_variants, 1):  
                st.write(f"Varianta {i}: {variant}")

    extracted_numbers_input = st.text_area('Introduceți numerele extrase (separate prin virgulă)', '')

    if st.button('Verifică variantele') and extracted_numbers_input:
        try:
            extracted_numbers = list(map(int, extracted_numbers_input.split(',')))
        except ValueError:
            st.error("Asigură-te că ai introdus doar numere separate prin virgulă!")
            return
        
        valid_variants = [variant for variant in st.session_state['variants'] if len(set(variant).intersection(extracted_numbers)) >= required_common]
        
        st.write(f'Numărul de variante valide: {len(valid_variants)}')
        for i, variant in enumerate(valid_variants, 1):
            st.write(f'VariantA validă {i}: {variant}')

# Apelarea directă a funcției main() pentru Streamlit
main()
