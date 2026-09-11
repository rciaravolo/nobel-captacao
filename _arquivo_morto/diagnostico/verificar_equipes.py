"""Verifica as equipes no Excel"""
import pandas as pd
import glob
import os

# Encontrar arquivo
arquivos = [f for f in glob.glob(r'C:\Users\Usuário\vBox\ONE PAGE\*BASES ONE PAGE*.xlsx') 
            if not os.path.basename(f).startswith('~$')]
arquivo = arquivos[0] if arquivos else None

print(f"Arquivo: {arquivo}")
print("=" * 70)

# Ler Excel
df = pd.read_excel(arquivo, sheet_name='TB_CAP')

# Normalizar colunas
df.columns = [str(c).strip() for c in df.columns]

print(f"\nTotal de linhas: {len(df)}")
print(f"\nEquipes únicas e contagem:")
print(df['Núcleo'].value_counts())

print("\n" + "=" * 70)
print("Equipes configuradas no config.py:")
equipes_config = ['PRIVATE', 'BRAVO', 'RIO PRETO', 'SMART-GLOBAL', 'SMART-UNIQUE', 'SMART-ALFA']
for eq in equipes_config:
    count = len(df[df['Núcleo'].str.upper() == eq.upper()])
    print(f"  {eq}: {count} linhas")

print("\n" + "=" * 70)
total_filtrado = len(df[df['Núcleo'].str.upper().isin([e.upper() for e in equipes_config])])
print(f"Total após filtro de equipes: {total_filtrado}")
