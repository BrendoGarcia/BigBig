# check_data_distribution.py

import pandas as pd

processed_data_path = "BigBig/processed_data.csv"
df = pd.read_csv(processed_data_path)

print("Distribuição da variável alvo 'alta_evasao':")
print(df["alta_evasao"].value_counts())

print("Número de valores únicos na variável alvo 'alta_evasao':")
print(df["alta_evasao"].nunique())


