import glob, os
import pandas as pd

BASE = r'C:\Users\Usuário\vBox\ONE PAGE'

def g(pasta, padrao):
    r = [f for f in glob.glob(os.path.join(pasta, padrao)) if not os.path.basename(f).startswith('~$')]
    return r[0] if r else None

df1 = pd.read_excel(g(BASE, '*BASES ONE PAGE*.xlsx'), sheet_name='TB_CAP', engine='openpyxl')
df2 = pd.read_excel(g(BASE, 'ONE PAGE - ATUAL_V2.xlsm'), sheet_name='CAPTAÇÃO ATUAL', engine='openpyxl')

df1.columns = [str(c).strip() for c in df1.columns]
df2.columns = [str(c).strip() for c in df2.columns]

print(f"Base1 (TB_CAP):         {df1.shape[0]} linhas | Colunas: {list(df1.columns)}")
print(f"Base2 (CAPTAÇÃO ATUAL): {df2.shape[0]} linhas | Colunas: {list(df2.columns)}")
print()
print(f"Base1 - range de datas: {df1['Data'].min()} até {df1['Data'].max()}")
print(f"Base2 - range de datas: {df2['Data'].min()} até {df2['Data'].max()}")
print()

# Verifica sobreposição por chave (Data + Assessor + Captação)
chave1 = set(zip(df1['Data'].astype(str), df1['Assessor '].astype(str).str.strip(), df1['Captação'].astype(str)))
chave2 = set(zip(df2['Data'].astype(str), df2['Assessor'].astype(str).str.strip(), df2['Captação'].astype(str)))

sobreposicao = chave1 & chave2
print(f"Registros em comum (Data+Assessor+Captação): {len(sobreposicao)}")
print(f"Exclusivos na Base1: {len(chave1 - chave2)}")
print(f"Exclusivos na Base2: {len(chave2 - chave1)}")
