import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("VERIFICANDO SHEETS DE HISTORICO")
print("=" * 60)

# Verifica HISTORICO CAP
print("\n1. HISTORICO CAP:")
try:
    df_hist = pd.read_excel(config.ARQUIVO_2, sheet_name='HISTÓRICO CAP', engine='openpyxl')
    print(f"   Total registros: {len(df_hist)}")
    print(f"   Colunas: {list(df_hist.columns[:10])}")
    if 'Data' in df_hist.columns:
        print(f"   Periodo: {df_hist['Data'].min()} a {df_hist['Data'].max()}")
        print(f"   Datas unicas: {df_hist['Data'].nunique()}")
except Exception as e:
    print(f"   ERRO: {e}")

# Verifica HISTORICO CAP 2025
print("\n2. HISTORICO CAP 2025:")
try:
    df_hist25 = pd.read_excel(config.ARQUIVO_2, sheet_name='HISTÓRICO CAP 2025', engine='openpyxl')
    print(f"   Total registros: {len(df_hist25)}")
    print(f"   Colunas: {list(df_hist25.columns[:10])}")
    if 'Data' in df_hist25.columns:
        print(f"   Periodo: {df_hist25['Data'].min()} a {df_hist25['Data'].max()}")
        print(f"   Datas unicas: {df_hist25['Data'].nunique()}")
except Exception as e:
    print(f"   ERRO: {e}")

# Verifica CAPTACAO ATUAL (atual)
print("\n3. CAPTACAO ATUAL (atual):")
df_atual = pd.read_excel(config.ARQUIVO_2, sheet_name='CAPTAÇÃO ATUAL', engine='openpyxl')
df_atual.columns = [str(c).strip() for c in df_atual.columns]
df_atual = df_atual[df_atual['Assessor'].astype(str).str.strip() != 'Assessor']
print(f"   Total registros: {len(df_atual)}")
print(f"   Periodo: {df_atual['Data'].min()} a {df_atual['Data'].max()}")
print(f"   Datas unicas: {sorted(df_atual['Data'].dropna().unique())}")

# Verifica se tem dados de marco
print("\n4. VERIFICANDO DADOS DE MARCO 2026:")
if 'Data' in df_atual.columns:
    marco_2026 = df_atual[df_atual['Data'] >= '2026-03-01']
    print(f"   Registros em marco/2026: {len(marco_2026)}")
    if len(marco_2026) > 0:
        print(f"   Datas: {sorted(marco_2026['Data'].unique())}")
        print("\n   Top 5 captacoes em marco:")
        top5 = marco_2026.nlargest(5, 'Captação')[['Assessor', 'Captação', 'Data']]
        print(top5.to_string(index=False))
