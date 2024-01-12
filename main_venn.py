import pandas as pd
from itertools import combinations

# Charger le fichier CSV
csv_file = 'PERSO/MCI.csv'
df = pd.read_csv(csv_file, delimiter=';')

# Liste des noms de patients
lists = df.columns.tolist()

# Dictionnaire pour stocker les occurrences de chaque protéine par patient
items_occurrence = {per_list: set(df[per_list].dropna()) for per_list in lists}

# Créer des fichiers texte pour chaque patient (exclusif)
for current_list, items_current_list in items_occurrence.items():
    output_file = f"1_{current_list}.txt"

    # Protéines exclusives au patient courant
    exclusive_items = items_current_list.copy()

    # Comparer avec les autres patients
    for other_list, items_other_list in items_occurrence.items():
        if other_list != current_list:
            exclusive_items -= items_other_list

    # Écrire les résultats dans le fichier texte
    with open(output_file, 'w') as file:
        for item in exclusive_items:
            file.write(f"{item}\n")

# Créer des fichiers texte pour chaque combinaison de patients (partagé)
for combination_size in range(2, len(lists) + 1):
    for lists_combination in combinations(lists, combination_size):
        output_file = f"{len(lists_combination)}_{'_'.join(sorted(lists_combination))}.txt"

        # Protéines partagées entre les patients de la combinaison
        shared_items = set.intersection(*(items_occurrence[item] for item in lists_combination))

        # Protéines exclusives à cette combinaison
        items_exclusive_to_combination = shared_items.copy()
        for other_list, items_other_list in items_occurrence.items():
            if other_list not in lists_combination:
                items_exclusive_to_combination -= items_other_list

        # Écrire les résultats dans le fichier texte
        with open(output_file, 'w') as file:
            for item in items_exclusive_to_combination:
                file.write(f"{item}\n")

print("Les résultats ont été enregistrés dans des fichiers texte.")
