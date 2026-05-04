import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("VERIFICANDO DADOS DE MARCO 2026 NA TB_CAP")
print("=" * 60)

df = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_BASE1, engine='openpyxl')
df.columns = [str(c).strip() for c in df.columns]

# Filtra apenas março 2026
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
marco = df[df['Data'] >= '2026-03-01']

print(f"\nTotal de registros em marco/2026: {len(marco)}")
print(f"Datas em marco: {sorted(marco['Data'].dropna().unique())}")
print(f"\nDistribuicao por data:")
print(marco['Data'].value_counts().sort_index())

print(f"\n\nTOP 10 CAPTACOES ACUMULADAS EM MARCO:")
marco_clean = marco[marco['Assessor'].astype(str).str.strip() != 'Assessor']
agrupado = marco_clean.groupby('Assessor')['Captação'].sum().sort_values(ascending=False).head(10)
for assessor, valor in agrupado.items():
    print(f"  {assessor}: R$ {valor:,.2f}")

print(f"\n\nTOP 10 CAPTACOES NEGATIVAS EM MARCO:")
negativos = marco_clean.groupby('Assessor')['Captação'].sum().sort_values(ascending=True).head(10)
for assessor, valor in negativos.items():
    print(f"  {assessor}: R$ {valor:,.2f}")

print("\n" + "=" * 60)
print("Se a planilha tiver apenas dados de 02/03, ela precisa ser")
print("atualizada com as transacoes de 01/03, 03/03, 04/03, etc.")
