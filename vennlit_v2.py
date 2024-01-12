import pandas as pd
from itertools import combinations
import streamlit as st
from matplotlib_venn import venn2, venn3, venn2_circles, venn3_circles
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import venn
import openpyxl


# Charger le fichier CSV
csv_file = 'example/example.csv'
df = pd.read_csv(csv_file, delimiter=';')

# items_occurrence = {per_list: set(df[per_list].dropna()) for per_list in lists}
# for current_list, items_current_list in items_occurrence.items():
#     output_file = f"1_{current_list}.txt"
#
#     # Protéines exclusives au patient courant
#     exclusive_items = items_current_list.copy()
#
#     # Comparer avec les autres patients
#     for other_list, items_other_list in items_occurrence.items():
#         if other_list != current_list:
#             exclusive_items -= items_other_list
#
#     # # Écrire les résultats dans le fichier texte
#     # with open(output_file, 'w') as file:
#     #     for item in exclusive_items:
#     #         file.write(f"{item}\n")
#
# # Créer des fichiers texte pour chaque combinaison de patients (partagé)
# for combination_size in range(2, len(lists) + 1):
#     for lists_combination in combinations(lists, combination_size):
#         output_file = f"{len(lists_combination)}_{'_'.join(sorted(lists_combination))}.txt"
#
#         # Protéines partagées entre les patients de la combinaison
#         shared_items = set.intersection(*(items_occurrence[item] for item in lists_combination))
#
#         # Protéines exclusives à cette combinaison
#         items_exclusive_to_combination = shared_items.copy()
#         for other_list, items_other_list in items_occurrence.items():
#             if other_list not in lists_combination:
#                 items_exclusive_to_combination -= items_other_list
#
#         # # Écrire les résultats dans le fichier texte
#         # with open(output_file, 'w') as file:
#         #     for item in items_exclusive_to_combination:
#         #         file.write(f"{item}\n")

# Diagramme de Venn
st.title('Diagramme de Venn avec Streamlit')

uploaded_files = st.file_uploader("Upload one or more .csv files", type=["csv", "xlsx"], accept_multiple_files=True)
if uploaded_files is not None:
    if len(uploaded_files) > 0:
        dfs = []
        for file in uploaded_files:
            if file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter=';')

            dfs.append(df)

        all_columns = [col for df in dfs for col in df.columns]
        duplicate_columns = [col for col in set(all_columns) if all_columns.count(col) > 1]
        if duplicate_columns:
            st.warning(f"Les noms de colonnes suivants sont en double : {', '.join(duplicate_columns)}")
            filtered_dfs = []
            included_columns = set()
            for df in dfs:
                filtered_columns = [col for col in df.columns if col not in duplicate_columns]
                included_columns.update(filtered_columns)
                filtered_df = df[filtered_columns]
                filtered_dfs.append(filtered_df)
            df = pd.concat(filtered_dfs, axis=1)

        else:
            df = pd.concat(dfs, axis=1)


st.dataframe(df.head())
lists = df.columns.tolist()

# Create a checkbox for each list
items_occurrence = {per_list: set(df[per_list].dropna()) for per_list in lists}
selection_lists = st.multiselect('Lists selection', lists, default=lists[:2], max_selections=6,
                                 placeholder="Choose 2-6 lists", disabled=False)

num_sets = len(selection_lists)

plt.figure(figsize=(8, 8))

if 1 < len(selection_lists) <= 6:
    # Calculer les labels uniquement pour les listes sélectionnées
    selected_data = [set(df[selected_list].dropna()) for selected_list in selection_lists]
    labels = venn.get_labels(selected_data, fill=['number'])

    # Dictionnaire des fonctions venn
    venn_functions = {
        2: venn.venn2,
        3: venn.venn3,
        4: venn.venn4,
        5: venn.venn5,
        6: venn.venn6
    }

    # Sélectionner la fonction venn appropriée en fonction du nombre de listes sélectionnées
    venn_function = venn_functions.get(len(selection_lists), None)

    if venn_function:
        venn_function(labels, names=selection_lists)
        st.pyplot(plt)

if len(selection_lists) == 6:
    dataset_dict = {
        name: set(items_occurrence[selection_lists[i]]) for i, (name, items) in enumerate(items_occurrence.items())
    }
    venn.pseudovenn(dataset_dict, hint_hidden=False)
    # fig.savefig('venn6.png', bbox_inches='tight')
    st.pyplot(plt)

