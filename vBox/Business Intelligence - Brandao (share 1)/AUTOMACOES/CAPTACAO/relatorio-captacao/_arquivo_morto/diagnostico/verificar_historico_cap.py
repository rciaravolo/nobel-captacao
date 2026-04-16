import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("VERIFICANDO HISTORICO CAP (dados acumulados)")
print("=" * 60)

df_hist = pd.read_excel(config.ARQUIVO_2, sheet_name='HISTÓRICO CAP', engine='openpyxl')
print(f"Total registros: {len(df_hist)}")
print(f"\nColunas: {list(df_hist.columns)}")
print(f"\nPrimeiras 10 linhas:")
print(df_hist.head(10).to_string())

print("\n\nPeriodos unicos:")
if 'Período' in df_hist.columns:
    print(df_hist['Período'].value_counts().sort_index(ascending=False).head(10))

print("\n\nTop 15 captacoes (se for marco 2026):")
# Filtra apenas marco 2026
if 'Período' in df_hist.columns:
    marco_2026 = df_hist[df_hist['Período'].astype(str).str.contains('03/2026|mar/26|março/26|MAR/26', case=False, na=False)]
    if len(marco_2026) > 0:
        print(f"\nRegistros de marco/2026: {len(marco_2026)}")
        top15 = marco_2026.nlargest(15, 'Capitação Líquida')[['Nome Assessor', 'Núcleo', 'Capitação Líquida', 'Período']]
        print(top15.to_string(index=False))
    else:
        print("Nenhum registro de marco/2026 encontrado")
        print("\nMostrando top 15 geral:")
        top15 = df_hist.nlargest(15, 'Capitação Líquida')[['Nome Assessor', 'Núcleo', 'Capitação Líquida', 'Período']]
        print(top15.to_string(index=False))
