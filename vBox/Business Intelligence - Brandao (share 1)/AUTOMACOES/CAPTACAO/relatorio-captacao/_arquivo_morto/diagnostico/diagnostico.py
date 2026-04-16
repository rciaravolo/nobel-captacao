import sys
sys.path.insert(0, '.')
import config
import pandas as pd
from etl_bases import executar_etl, carregar_assessores_ativos
from datetime import datetime
import os

print("=" * 60)
print("DIAGNOSTICO - PLANILHAS E ETL")
print("=" * 60)

# 1. Verifica arquivos
print("\n1. ARQUIVOS:")
print(f"Base1: {config.ARQUIVO_1}")
if os.path.exists(config.ARQUIVO_1):
    mod_time = datetime.fromtimestamp(os.path.getmtime(config.ARQUIVO_1))
    print(f"   Modificado: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    print("   NAO ENCONTRADO!")

print(f"\nBase2: {config.ARQUIVO_2}")
if os.path.exists(config.ARQUIVO_2):
    mod_time = datetime.fromtimestamp(os.path.getmtime(config.ARQUIVO_2))
    print(f"   Modificado: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    print("   NAO ENCONTRADO!")

# 2. Verifica Base2 (fonte atual)
print("\n2. BASE2 (CAPTACAO ATUAL) - DADOS BRUTOS:")
df2 = pd.read_excel(config.ARQUIVO_2, sheet_name=config.SHEET_BASE2, engine='openpyxl')
df2.columns = [str(c).strip() for c in df2.columns]
df2 = df2[df2['Assessor'].astype(str).str.strip() != 'Assessor']
print(f"   Total registros: {len(df2)}")
print(f"   Periodo: {df2['Data'].min()} a {df2['Data'].max()}")
print(f"   Datas unicas: {sorted(df2['Data'].unique())}")

# 3. Verifica ETL processado
print("\n3. ETL PROCESSADO:")
ativos = carregar_assessores_ativos()
df = executar_etl(ativos)
print(f"   Total registros apos ETL: {len(df)}")
print(f"   Colunas: {list(df.columns)}")
print(f"   Periodo: {df['Data'].min()} a {df['Data'].max()}")

# 4. Top 10 captacoes
print("\n4. TOP 10 CAPTACOES (VALORES PROCESSADOS):")
col_valor = config.COLUNA_VALOR
agrupado = df.groupby('Assessor')[col_valor].sum().sort_values(ascending=False).head(10)
for assessor, valor in agrupado.items():
    print(f"   {assessor}: R$ {valor:,.2f}")

# 5. Valores negativos
print("\n5. TOP 10 CAPTACOES NEGATIVAS:")
negativos = df.groupby('Assessor')[col_valor].sum().sort_values(ascending=True).head(10)
for assessor, valor in negativos.items():
    print(f"   {assessor}: R$ {valor:,.2f}")

print("\n" + "=" * 60)
print("FIM DO DIAGNOSTICO")
print("=" * 60)
