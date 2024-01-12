import pandas as pd
import streamlit as st


# Charger les fichiers CSV
lps_df = pd.read_csv('LPS.csv', sep=';')
free_df = pd.read_csv('FREE.csv', sep=';')

# Filtrer les gènes de LPS avec FC supérieur à 0 et non présents dans Free
lps_genes_pos_not_in_free_df = lps_df[(lps_df['FC'] > 0) & (~lps_df['Gene names'].isin(free_df['Gene names']))]

# Filtrer les gènes de LPS avec FC inférieur à 0 et non présents dans Free
lps_genes_neg_not_in_free_df = lps_df[(lps_df['FC'] < 0) & (~lps_df['Gene names'].isin(free_df['Gene names']))]

# Filtrer les gènes de LPS avec FC supérieur à 0 et non présents dans Free
free_genes_pos_not_in_lps_df = free_df[(free_df['FC'] > 0) & (~free_df['Gene names'].isin(lps_df['Gene names']))]

# Filtrer les gènes de LPS avec FC inférieur à 0 et non présents dans Free
free_genes_neg_not_in_lps_df = free_df[(free_df['FC'] < 0) & (~free_df['Gene names'].isin(lps_df['Gene names']))]

lps_genes_pos_not_in_free_df.to_csv('lps_genes_pos_not_in_free.csv', index=False)
lps_genes_neg_not_in_free_df.to_csv('lps_genes_neg_not_in_free.csv', index=False)
free_genes_pos_not_in_lps_df.to_csv('free_genes_pos_not_in_lps.csv', index=False)
free_genes_neg_not_in_lps_df.to_csv('free_genes_neg_not_in_lps.csv', index=False)

# Fusionner les deux dataframes sur la colonne 'Gene names'
merged_df = pd.merge(lps_df, free_df, on='Gene names', suffixes=('_LPS', '_Free'), how='outer')

# Filtrer les gènes communs
common_genes_df = merged_df[['Gene names', 'FC_LPS', 'FC_Free']].copy()  # Utilise .copy() pour éviter le SettingWithCopyWarning

# Ajouter une colonne pour la comparaison des FC
common_genes_df['FC_Comparison FREE - LPS'] = common_genes_df['FC_Free'] - common_genes_df['FC_LPS']

# Filtrer les gènes communs avec FC supérieur à 0
common_genes_pos_df = common_genes_df[(common_genes_df['FC_LPS'] > 0) & (common_genes_df['FC_Free'] > 0)]

# Filtrer les gènes communs avec FC inférieur à 0
common_genes_neg_df = common_genes_df[(common_genes_df['FC_LPS'] < 0) & (common_genes_df['FC_Free'] < 0)]

# Filtrer les gènes de Free avec FC négatif mais FC positif dans LPS
free_neg_lps_pos_df = common_genes_df[(common_genes_df['FC_Free'] < 0) & (common_genes_df['FC_LPS'] > 0)]

# Filtrer les gènes de Free avec FC positif mais FC négatif dans LPS
free_pos_lps_neg_df = common_genes_df[(common_genes_df['FC_Free'] > 0) & (common_genes_df['FC_LPS'] < 0)]

# Enregistrer les résultats dans des fichiers CSV
common_genes_pos_df.to_csv('common_genes_pos.csv', index=False)
common_genes_neg_df.to_csv('common_genes_neg.csv', index=False)
free_neg_lps_pos_df.to_csv('free_genes_neg_lps_pos.csv', index=False)
free_pos_lps_neg_df.to_csv('free_genes_pos_lps_neg.csv', index=False)
