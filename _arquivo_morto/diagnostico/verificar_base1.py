import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("VERIFICANDO BASE1 (TB_CAP)")
print("=" * 60)

df1 = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_BASE1, engine='openpyxl')
df1.columns = [str(c).strip() for c in df1.columns]
df1 = df1[df1['Assessor'].astype(str).str.strip() != 'Assessor']

print(f"Total registros: {len(df1)}")
print(f"Periodo: {df1['Data'].min()} a {df1['Data'].max()}")
print(f"\nColunas: {list(df1.columns)}")

print("\nTop 10 captacoes acumuladas:")
agrupado = df1.groupby('Assessor')['Captação'].sum().sort_values(ascending=False).head(10)
for assessor, valor in agrupado.items():
    print(f"  {assessor}: R$ {valor:,.2f}")

print("\nTop 10 captacoes negativas:")
negativos = df1.groupby('Assessor')['Captação'].sum().sort_values(ascending=True).head(10)
for assessor, valor in negativos.items():
    print(f"  {assessor}: R$ {valor:,.2f}")
