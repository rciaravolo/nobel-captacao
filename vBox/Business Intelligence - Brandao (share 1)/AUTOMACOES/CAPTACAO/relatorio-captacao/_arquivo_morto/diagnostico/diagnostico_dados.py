"""
Script de diagnóstico para verificar discrepâncias nos dados
"""
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import *
from etl_bases import executar_etl, carregar_assessores_ativos

def diagnostico_completo():
    print("=" * 70)
    print("DIAGNÓSTICO DE DADOS - RELATÓRIO CAPTAÇÃO")
    print("=" * 70)
    
    # 1. Carregar arquivo bruto
    print("\n1. DADOS BRUTOS DO EXCEL")
    print("-" * 70)
    df_bruto = pd.read_excel(ARQUIVO_1, sheet_name=SHEET_BASE1)
    print(f"Total de linhas: {len(df_bruto)}")
    print(f"Colunas: {list(df_bruto.columns)}")
    
    # Verificar coluna Assessor
    col_assessor_real = [c for c in df_bruto.columns if 'Assessor' in c][0]
    print(f"\nColuna Assessor encontrada: '{col_assessor_real}'")
    print(f"Caracteres especiais: {repr(col_assessor_real)}")
    
    # Soma total bruta
    soma_bruta = df_bruto['Captação'].sum()
    print(f"\nSOMA TOTAL BRUTA (todas as linhas): R$ {soma_bruta:,.2f}")
    
    # 2. Filtros aplicados
    print("\n2. FILTROS APLICADOS")
    print("-" * 70)
    
    # Filtro de equipes
    df_filtrado = df_bruto[df_bruto['Núcleo'].isin(EQUIPES_PERMITIDAS)].copy()
    soma_apos_equipes = df_filtrado['Captação'].sum()
    print(f"Após filtro de equipes ({EQUIPES_PERMITIDAS}):")
    print(f"  Linhas: {len(df_bruto)} → {len(df_filtrado)}")
    print(f"  Soma: R$ {soma_bruta:,.2f} → R$ {soma_apos_equipes:,.2f}")
    
    # Filtro de zeros
    if not CONSIDERAR_ZERADOS:
        df_sem_zeros = df_filtrado[df_filtrado['Captação'] != 0].copy()
        soma_sem_zeros = df_sem_zeros['Captação'].sum()
        print(f"\nApós remover zeros:")
        print(f"  Linhas: {len(df_filtrado)} → {len(df_sem_zeros)}")
        print(f"  Soma: R$ {soma_apos_equipes:,.2f} → R$ {soma_sem_zeros:,.2f}")
        df_final = df_sem_zeros
    else:
        df_final = df_filtrado
    
    # 3. Dados processados pelo ETL
    print("\n3. DADOS PROCESSADOS PELO ETL")
    print("-" * 70)
    assessores = carregar_assessores_ativos()
    df_etl = executar_etl(assessores)
    soma_etl = df_etl[COLUNA_VALOR].sum()
    print(f"Linhas após ETL: {len(df_etl)}")
    print(f"Soma após ETL: R$ {soma_etl:,.2f}")
    
    # 4. Comparação por equipe
    print("\n4. COMPARAÇÃO POR EQUIPE")
    print("-" * 70)
    print(f"{'Equipe':<15} {'Excel (bruto)':<20} {'ETL (processado)':<20} {'Diferença':<15}")
    print("-" * 70)
    
    for equipe in EQUIPES_PERMITIDAS:
        soma_excel = df_final[df_final['Núcleo'] == equipe]['Captação'].sum()
        soma_etl_equipe = df_etl[df_etl[COLUNA_TIME] == equipe][COLUNA_VALOR].sum()
        diferenca = soma_etl_equipe - soma_excel
        
        print(f"{equipe:<15} R$ {soma_excel:>15,.2f}  R$ {soma_etl_equipe:>15,.2f}  R$ {diferenca:>12,.2f}")
    
    # 5. Verificar assessores ativos
    print("\n5. FILTRO DE ASSESSORES ATIVOS")
    print("-" * 70)
    assessores_ativos = carregar_assessores_ativos()
    print(f"Assessores ativos no JSON: {len(assessores_ativos)}")
    
    # Assessores únicos no Excel
    assessores_excel = set(df_final[col_assessor_real].dropna().unique())
    print(f"Assessores únicos no Excel (após filtros): {len(assessores_excel)}")
    
    # Assessores no ETL
    assessores_etl = set(df_etl[COLUNA_ASSESSOR].dropna().unique())
    print(f"Assessores únicos no ETL: {len(assessores_etl)}")
    
    # Assessores que foram removidos
    removidos = assessores_excel - assessores_etl
    if removidos:
        print(f"\nAssessores REMOVIDOS pelo filtro de ativos ({len(removidos)}):")
        for ass in sorted(removidos):
            valor = df_final[df_final[col_assessor_real] == ass]['Captação'].sum()
            print(f"  - {ass}: R$ {valor:,.2f}")
    
    # 6. Resumo final
    print("\n6. RESUMO FINAL")
    print("=" * 70)
    print(f"Soma Excel (bruto, todas linhas):     R$ {soma_bruta:>15,.2f}")
    print(f"Soma Excel (após filtros):            R$ {df_final['Captação'].sum():>15,.2f}")
    print(f"Soma ETL (processado):                R$ {soma_etl:>15,.2f}")
    print(f"Diferença:                            R$ {soma_etl - df_final['Captação'].sum():>15,.2f}")
    print("=" * 70)
    
    # 7. Detalhes das datas
    print("\n7. DISTRIBUIÇÃO POR DATA")
    print("-" * 70)
    df_por_data = df_final.groupby('Data')['Captação'].sum().sort_index()
    print("Data         | Valor")
    print("-" * 70)
    for data, valor in df_por_data.items():
        print(f"{data.strftime('%d/%m/%Y')} | R$ {valor:>15,.2f}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    diagnostico_completo()
