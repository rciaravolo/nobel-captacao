export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  };

  if (url.pathname !== '/api/dados') {
    return new Response(JSON.stringify({ error: 'Not found' }), { status: 404, headers });
  }

  try {
    const [[capTotal, capEquipe, capTipo, custTotal, custEquipe, custTipoPessoa, custEquipePfPj, capPorAssessor, custPorAssessor],
           [recRf, recRv, recCoe, recSeguros, recDominion, recCambio, recConsorcio, recFeeFixo, recOfertaFundos, recFundos, recPrev]] =
      await Promise.all([
        Promise.all([
      env.DB.prepare(`
        SELECT
          SUM(captacao) as total,
          SUM(CASE WHEN captacao > 0 THEN captacao ELSE 0 END) as positivo,
          SUM(CASE WHEN captacao < 0 THEN captacao ELSE 0 END) as negativo,
          MAX(data) as data_ref,
          MAX(data_atualizacao) as data_atualizacao
        FROM tb_cap
      `).first(),

      env.DB.prepare(`
        SELECT equipe,
          SUM(captacao) as total,
          SUM(CASE WHEN captacao > 0 THEN captacao ELSE 0 END) as positivo,
          SUM(CASE WHEN captacao < 0 THEN captacao ELSE 0 END) as negativo
        FROM tb_cap
        WHERE equipe != 'OPS'
        GROUP BY equipe ORDER BY total DESC
      `).all(),

      env.DB.prepare(`
        SELECT tipo,
          SUM(captacao) as liquido,
          SUM(CASE WHEN captacao > 0 THEN captacao ELSE 0 END) as entrada,
          SUM(CASE WHEN captacao < 0 THEN captacao ELSE 0 END) as saida
        FROM tb_cap
        GROUP BY tipo
        ORDER BY ABS(SUM(captacao)) DESC
      `).all(),

      env.DB.prepare(`
        SELECT SUM(net_em_m) as total,
          COUNT(DISTINCT id_cliente) as clientes,
          MAX(data_posicao) as data_posicao
        FROM tb_positivador
      `).first(),

      env.DB.prepare(`
        SELECT equipe, SUM(net_em_m) as custodia,
          COUNT(DISTINCT id_cliente) as clientes
        FROM tb_positivador
        WHERE equipe IN ('SMART','RIO PRETO','BRAVO','PRIVATE')
        GROUP BY equipe ORDER BY custodia DESC
      `).all(),

      env.DB.prepare(`
        SELECT tipo_pessoa,
          SUM(net_em_m) as custodia,
          COUNT(DISTINCT id_cliente) as clientes
        FROM tb_positivador
        WHERE equipe IN ('SMART','RIO PRETO','BRAVO','PRIVATE')
        GROUP BY tipo_pessoa ORDER BY custodia DESC
      `).all(),

      env.DB.prepare(`
        SELECT equipe,
          SUM(CASE WHEN tipo_pessoa = 'PF' THEN net_em_m ELSE 0 END) as pf,
          COUNT(DISTINCT CASE WHEN tipo_pessoa = 'PF' THEN id_cliente END) as clientes_pf,
          SUM(CASE WHEN tipo_pessoa = 'PJ' THEN net_em_m ELSE 0 END) as pj,
          COUNT(DISTINCT CASE WHEN tipo_pessoa = 'PJ' THEN id_cliente END) as clientes_pj
        FROM tb_positivador
        WHERE equipe IN ('SMART','RIO PRETO','BRAVO','PRIVATE')
        GROUP BY equipe
        ORDER BY (SUM(net_em_m)) DESC
      `).all(),

      env.DB.prepare(`
        SELECT
          nome_assessor,
          equipe,
          SUM(captacao) as total,
          SUM(CASE WHEN captacao > 0 THEN captacao ELSE 0 END) as positivo,
          SUM(CASE WHEN captacao < 0 THEN captacao ELSE 0 END) as negativo
        FROM tb_cap
        WHERE equipe != 'OPS'
          AND nome_assessor IS NOT NULL AND nome_assessor != ''
          AND id_assessor NOT IN ('A69243','PRECAS','A72441','A26496','A20345','A26085','FINDER01','A51250')
        GROUP BY nome_assessor, equipe
        ORDER BY total DESC
      `).all(),

      env.DB.prepare(`
        SELECT
          nome_assessor,
          equipe,
          SUM(net_em_m) as custodia
        FROM tb_positivador
        WHERE equipe IN ('SMART','RIO PRETO','BRAVO','PRIVATE')
          AND nome_assessor IS NOT NULL AND nome_assessor != ''
          AND id_assessor NOT IN ('A69243','PRECAS','A72441','A26496','A20345','A26085','FINDER01','A51250')
        GROUP BY nome_assessor, equipe
        ORDER BY custodia DESC
      `).all(),
        ]),
        Promise.all([
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_rf`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_rv`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_coe`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_seguros`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_dominion`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_cambio`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_consorcio`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_feefixo`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_oferta_fundos`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_fundos`).first(),
          env.DB.prepare(`SELECT SUM(receita) as total FROM receita_prev`).first(),
        ]),
      ]);

    const receitaClasses = [
      { classe: 'RF',            total: recRf?.total ?? 0 },
      { classe: 'RV',            total: recRv?.total ?? 0 },
      { classe: 'COE',           total: recCoe?.total ?? 0 },
      { classe: 'Seguros',       total: recSeguros?.total ?? 0 },
      { classe: 'Dominion',      total: recDominion?.total ?? 0 },
      { classe: 'Câmbio',        total: recCambio?.total ?? 0 },
      { classe: 'Consórcio',     total: recConsorcio?.total ?? 0 },
      { classe: 'Fee Fixo',      total: recFeeFixo?.total ?? 0 },
      { classe: 'Oferta Fundos', total: recOfertaFundos?.total ?? 0 },
      { classe: 'Fundos',        total: recFundos?.total ?? 0 },
      { classe: 'Previdência',   total: recPrev?.total ?? 0 },
    ].filter(r => r.total > 0).sort((a, b) => b.total - a.total);

    const receitaTotal = receitaClasses.reduce((s, r) => s + r.total, 0);

    const body = JSON.stringify({
      captacao: {
        total: capTotal.total,
        positivo: capTotal.positivo,
        negativo: capTotal.negativo,
        data_ref: capTotal.data_ref,
        data_atualizacao: capTotal.data_atualizacao,
        por_equipe: capEquipe.results,
        por_tipo: capTipo.results,
        por_assessor: capPorAssessor.results,
      },
      custodia: {
        total: custTotal.total,
        clientes: custTotal.clientes,
        data_posicao: custTotal.data_posicao,
        por_equipe: custEquipe.results,
        por_tipo_pessoa: custTipoPessoa.results,
        equipe_pfpj: custEquipePfPj.results,
        por_assessor: custPorAssessor.results,
      },
      receita: {
        total: receitaTotal,
        por_classe: receitaClasses,
      },
    });

    return new Response(body, { headers });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
  }
}
