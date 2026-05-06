import streamlit as st
from itertools import combinations
import time

def generate_optimized_variants(total_numbers, variant_size, required_common, max_valid_variants, progress_bar=None):
    all_numbers = list(range(1, total_numbers + 1))
    all_variants = list(combinations(all_numbers, variant_size))
    
    selected_variants = []
    covered_combinations = set()
    
    total_variants = len(all_variants)
    for i, variant in enumerate(all_variants):
        variant_set = set(variant)
        
        if not any(len(variant_set.intersection(existing)) >= required_common for existing in selected_variants):
            selected_variants.append(variant)
            
            for combination in combinations(variant, required_common):
                covered_combinations.add(frozenset(combination))
            
            if len(selected_variants) >= max_valid_variants:
                break
        
        if progress_bar:
            progress_bar.progress((i + 1) / total_variants)
            
    return selected_variants

def main():
    st.title('Loto Variants Generator')

    total_numbers = st.number_input('Numărul total de numere', min_value=10, max_value=50, value=20)
    variant_size = st.number_input('Dimensiunea variantei', min_value=3, max_value=20, value=6)
    required_common = st.number_input('Numărul minim de numere comune', min_value=3, max_value=variant_size, value=5)
    max_valid_variants = st.number_input('Numărul maxim de variante', min_value=1, max_value=1000, value=1000)

    user_numbers_input = st.text_area('Introduceți numerele disponibile (separate prin virgulă)', '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20')
    
    try:
        user_numbers = list(map(int, user_numbers_input.split(',')))
    except ValueError:
        st.error("Asigură-te că ai introdus doar numere separate prin virgulă!")
        return
    
    if 'variants' not in st.session_state:
        st.session_state['variants'] = []
    
    if st.button('Generează variante'):
        if len(user_numbers) == total_numbers:
            progress_bar = st.progress(0)
            start_time = time.time()

            variants = generate_optimized_variants(total_numbers, variant_size, required_common, max_valid_variants, progress_bar)
            
            st.session_state['variants'] = variants
            
            st.write(f'Număr total de variante generate: {len(variants)}')
            for i, variant in enumerate(variants, 1):
                st.write(f'Variant {i}: {variant}')
            
            total_time = time.time() - start_time
            st.write(f'Timp total de generare: {total_time:.2f} secunde')
        else:
            st.error(f'Trebuie să introduci exact {total_numbers} numere!')

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
            st.write(f'Variant validă {i}: {variant}')

main()