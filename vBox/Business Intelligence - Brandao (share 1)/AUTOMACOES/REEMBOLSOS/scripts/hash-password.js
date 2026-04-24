/**
 * Gera hash de senha compatível com o sistema de reembolsos.
 * Usa PBKDF2-HMAC-SHA256 com 100.000 iterações (mesmo algoritmo do Worker).
 *
 * Uso:
 *   node scripts/hash-password.js "MinhaSenh@123"
 *
 * Cole o hash gerado diretamente no SQL de seed.
 */
const crypto = require('crypto');

const password = process.argv[2];
if (!password) {
  console.error('Uso: node scripts/hash-password.js "sua_senha"');
  process.exit(1);
}

const salt = crypto.randomBytes(16);
const saltHex = salt.toString('hex');

crypto.pbkdf2(password, salt, 100000, 32, 'sha256', (err, derived) => {
  if (err) { console.error(err); process.exit(1); }
  const hashHex = derived.toString('hex');
  const result = `pbkdf2:100000:${saltHex}:${hashHex}`;
  console.log('\nHash gerado:');
  console.log(result);
  console.log('\nSQL de INSERT:');
  console.log(`INSERT INTO users (name, email, password_hash, role) VALUES ('Nome Completo', 'email@nobelcapital.com.br', '${result}', 'financeiro');`);
});
