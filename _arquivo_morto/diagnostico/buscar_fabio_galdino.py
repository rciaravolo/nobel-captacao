import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("BUSCANDO FABIO GALDINO NAS PLANILHAS")
print("=" * 60)

# Base1 - TB_CAP
print("\n1. BASE1 (TB_CAP):")
df1 = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_BASE1, engine='openpyxl')
df1.columns = [str(c).strip() for c in df1.columns]
fabio1 = df1[df1['Assessor'].astype(str).str.contains('FABIO GALDINO', case=False, na=False)]
if len(fabio1) > 0:
    print(f"   Encontrado {len(fabio1)} registros")
    print(f"   Captacao total: R$ {fabio1['Captação'].sum():,.2f}")
    print(fabio1[['Data', 'Assessor', 'Captação']].to_string(index=False))
else:
    print("   NAO ENCONTRADO")

# Base2 - CAPTACAO ATUAL
print("\n2. BASE2 (CAPTACAO ATUAL):")
df2 = pd.read_excel(config.ARQUIVO_2, sheet_name=config.SHEET_BASE2, engine='openpyxl')
df2.columns = [str(c).strip() for c in df2.columns]
fabio2 = df2[df2['Assessor'].astype(str).str.contains('FABIO GALDINO', case=False, na=False)]
if len(fabio2) > 0:
    print(f"   Encontrado {len(fabio2)} registros")
    print(f"   Captacao total: R$ {fabio2['Captação'].sum():,.2f}")
    print(fabio2[['Data', 'Assessor', 'Captação']].head(10).to_string(index=False))
else:
    print("   NAO ENCONTRADO")

# HISTORICO CAP
print("\n3. HISTORICO CAP (dados mensais):")
df_hist = pd.read_excel(config.ARQUIVO_2, sheet_name='HISTÓRICO CAP', engine='openpyxl')
fabio_hist = df_hist[df_hist['Nome Assessor'].astype(str).str.contains('FABIO GALDINO', case=False, na=False)]
if len(fabio_hist) > 0:
    print(f"   Encontrado {len(fabio_hist)} registros")
    print(fabio_hist[['Período', 'Nome Assessor', 'Núcleo', 'Capitação Líquida']].tail(10).to_string(index=False))
    
    # Verifica fevereiro 2026
    fev_2026 = fabio_hist[fabio_hist['Período'] == '2026-02-01']
    if len(fev_2026) > 0:
        print(f"\n   FEVEREIRO 2026: R$ {fev_2026['Capitação Líquida'].sum():,.2f}")
else:
    print("   NAO ENCONTRADO")

print("\n" + "=" * 60)
print("CONCLUSAO:")
print("Se o valor de Fabio Galdino for 2.310.234, isso representa")
print("a captacao ACUMULADA do mes, nao apenas do dia 02/03.")
print("As planilhas precisam ser atualizadas com dados completos.")
