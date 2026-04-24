/**
 * Seed via API — cria o primeiro usuário financeiro usando o endpoint /api/auth/setup.
 * Só funciona quando o banco está vazio (sem usuários cadastrados).
 *
 * Uso:
 *   node scripts/seed.js https://reembolsos-api.SEU_SUBDOMINIO.workers.dev
 *
 * (Sem argumento, usa localhost:8787)
 */

const API_URL = process.argv[2] || 'http://localhost:8787';

const FINANCEIRO = {
  name: 'Financeiro Nobel',
  email: 'financeiro@nobelcapital.com.br',
  password: 'Nobel@2025!',  // TROQUE ANTES DE USAR EM PRODUÇÃO
};

async function main() {
  console.log(`Conectando em: ${API_URL}`);

  const res = await fetch(`${API_URL}/api/auth/setup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(FINANCEIRO),
  });

  const data = await res.json();

  if (res.ok) {
    console.log('');
    console.log('Usuário financeiro criado com sucesso!');
    console.log(`  Email: ${FINANCEIRO.email}`);
    console.log(`  Senha: ${FINANCEIRO.password}`);
    console.log('');
    console.log('IMPORTANTE: Troque a senha apos o primeiro login via admin-usuarios.html');
  } else {
    console.error('Erro:', data.error || JSON.stringify(data));
    if (data.error?.includes('Setup ja realizado')) {
      console.log('O banco ja tem usuarios. Use admin-usuarios.html para adicionar mais.');
    }
  }
}

main().catch(err => { console.error('Erro de conexao:', err.message); process.exit(1); });
