import sys
sys.path.insert(0, '.')
import config
import pandas as pd

print("SHEETS DISPONIVEIS NAS PLANILHAS")
print("=" * 60)

print("\nBase1 (ATUALIZACAO - BASES ONE PAGE.xlsx):")
xl1 = pd.ExcelFile(config.ARQUIVO_1, engine='openpyxl')
for i, sheet in enumerate(xl1.sheet_names, 1):
    print(f"  {i}. {sheet}")

print("\nBase2 (ONE PAGE - ATUAL_V2.xlsm):")
xl2 = pd.ExcelFile(config.ARQUIVO_2, engine='openpyxl')
for i, sheet in enumerate(xl2.sheet_names, 1):
    print(f"  {i}. {sheet}")
