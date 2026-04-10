import logging
import os
import sys
from datetime import datetime

# ── CONFIGURAÇÃO DE LOG ───────────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)
log_filename = f"logs/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s — %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

# ── IMPORTS DO PROJETO ────────────────────────────────────────────────────────
import config
from etl_bases import executar_etl, executar_etl_custodia, carregar_assessores_ativos, executar_etl_escritorio, executar_etl_custodia_escritorio
from consolidacao import calcular_resumo, calcular_resumo_custodia
from ranking_generator import (
    gerar_ranking_times,
    gerar_ranking_assessores_positivos,
    gerar_ranking_assessores_negativos,
    gerar_ranking_custodia_times,
    gerar_ranking_custodia_assessores,
)
from email_sender import enviar_relatorio
from chart_generator import preparar_dados_diarios, gerar_grafico_captacao


def main():
    logger.info("=" * 60)
    logger.info("  RELATÓRIO DE CAPTAÇÃO DIÁRIO — Nobel Capital")
    logger.info(f"  Execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 1️⃣  ETL — Leitura e merge das bases
        # 1️⃣  Carrega assessores ativos das 6 equipes (uma unica vez)
        assessores_ativos = carregar_assessores_ativos()

        df = executar_etl(assessores_ativos)

        if df.empty:
            logger.warning("DataFrame vazio após ETL. Nenhum registro CONVERTIDO encontrado.")
            logger.warning("Verifique os arquivos de entrada e o filtro de status.")
            sys.exit(1)

        # 2️⃣  Totais do escritório (sem filtro de equipe — todos os assessores da planilha)
        df_escritorio, data_atualizacao = executar_etl_escritorio()
        resumo = calcular_resumo(df, df_escritorio)

        # 3️⃣  Rankings de captacao
        rank_times      = gerar_ranking_times(df)
        rank_positivos  = gerar_ranking_assessores_positivos(df)
        rank_negativos  = gerar_ranking_assessores_negativos(df)

        # 4️⃣  Grafico de captacao diaria (mes atual)
        logger.info("Gerando grafico de captacao diaria...")
        df_diario = preparar_dados_diarios(df_escritorio)
        grafico_captacao_b64 = gerar_grafico_captacao(df_diario)

        # 5️⃣  ETL e rankings de custodia
        df_cust             = executar_etl_custodia(assessores_ativos)
        df_cust_escritorio  = executar_etl_custodia_escritorio()
        resumo_cust         = calcular_resumo_custodia(df_cust, df_cust_escritorio)
        rank_cust_times     = gerar_ranking_custodia_times(df_cust, df_cust_escritorio)
        rank_cust_grande, rank_cust_pequeno = gerar_ranking_custodia_assessores(df_cust)

        # 6️⃣  E-mail — Geração do HTML + Envio
        enviar_relatorio(
            resumo, rank_times, rank_positivos, rank_negativos,
            resumo_cust, rank_cust_times, rank_cust_grande, rank_cust_pequeno,
            data_atualizacao=data_atualizacao,
            grafico_captacao_b64=grafico_captacao_b64,
        )


        logger.info("=" * 60)
        logger.info("  ✅ RELATÓRIO CONCLUÍDO COM SUCESSO")
        logger.info(f"  Log salvo em: {log_filename}")
        logger.info("=" * 60)

    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        logger.error("Verifique os caminhos em config.py (ARQUIVO_1 e ARQUIVO_2).")
        sys.exit(1)

    except KeyError as e:
        logger.error(f"Coluna não encontrada: {e}")
        logger.error("Verifique os nomes das colunas em config.py.")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
