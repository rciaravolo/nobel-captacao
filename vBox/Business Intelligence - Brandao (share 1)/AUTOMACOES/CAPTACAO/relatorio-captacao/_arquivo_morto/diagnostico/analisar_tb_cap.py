import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("ANALISE DETALHADA DA TB_CAP")
print("=" * 60)

df = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_BASE1, engine='openpyxl')
df.columns = [str(c).strip() for c in df.columns]

print(f"\n1. ESTRUTURA:")
print(f"   Total de linhas: {len(df)}")
print(f"   Colunas: {list(df.columns)}")

print(f"\n2. DATAS:")
print(f"   Datas unicas: {sorted(df['Data'].dropna().unique())}")
print(f"   Registros por data:")
print(df['Data'].value_counts().sort_index())

print(f"\n3. FABIO GALDINO:")
fabio = df[df['Assessor'].astype(str).str.contains('FABIO GALDINO', case=False, na=False)]
if len(fabio) > 0:
    print(f"   Total de registros: {len(fabio)}")
    print(f"   Captacao total: R$ {fabio['Captação'].sum():,.2f}")
    print("\n   Detalhes:")
    print(fabio[['Data', 'Assessor', 'Núcleo', 'Captação', 'Tipo de Captação']].to_string(index=False))
else:
    print("   NAO ENCONTRADO")

print(f"\n4. MARCELO ALMEIDA:")
marcelo = df[df['Assessor'].astype(str).str.contains('MARCELO ALMEIDA', case=False, na=False)]
if len(marcelo) > 0:
    print(f"   Total de registros: {len(marcelo)}")
    print(f"   Captacao total: R$ {marcelo['Captação'].sum():,.2f}")
    print("\n   Detalhes:")
    print(marcelo[['Data', 'Assessor', 'Núcleo', 'Captação', 'Tipo de Captação']].to_string(index=False))
else:
    print("   NAO ENCONTRADO")

print(f"\n5. ALEXANDRE FRANCA:")
alexandre = df[df['Assessor'].astype(str).str.contains('ALEXANDRE FRAN', case=False, na=False)]
if len(alexandre) > 0:
    print(f"   Total de registros: {len(alexandre)}")
    print(f"   Captacao total: R$ {alexandre['Captação'].sum():,.2f}")
    print("\n   Detalhes:")
    print(alexandre[['Data', 'Assessor', 'Núcleo', 'Captação']].to_string(index=False))
else:
    print("   NAO ENCONTRADO")

print("\n" + "=" * 60)
print("CONCLUSAO:")
print("A TB_CAP contem apenas transacoes do dia 02/03/2026.")
print("Se os valores esperados sao maiores (ex: Fabio 2.310.234),")
print("a planilha precisa ser atualizada com dados acumulados do mes.")
