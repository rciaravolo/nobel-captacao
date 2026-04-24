import { Context, Next } from 'hono';
import { AppContext, JWTPayload } from '../types';

function base64urlDecode(str: string): string {
  // base64url → base64: replace - with + and _ with /
  return atob(str.replace(/-/g, '+').replace(/_/g, '/'));
}

function base64urlEncode(buf: ArrayBuffer): string {
  return btoa(String.fromCharCode(...new Uint8Array(buf)))
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

async function getHmacKey(secret: string, usage: KeyUsage[]): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    usage
  );
}

export async function verifyJWT(token: string, secret: string): Promise<JWTPayload> {
  const parts = token.split('.');
  if (parts.length !== 3) throw new Error('Formato de token inválido');

  const [headerB64, payloadB64, signatureB64] = parts;
  const key = await getHmacKey(secret, ['verify']);
  const data = new TextEncoder().encode(`${headerB64}.${payloadB64}`);

  // base64url decode da assinatura
  const sigStr = signatureB64.replace(/-/g, '+').replace(/_/g, '/');
  const sigPadded = sigStr + '='.repeat((4 - sigStr.length % 4) % 4);
  const signature = Uint8Array.from(atob(sigPadded), c => c.charCodeAt(0));

  const valid = await crypto.subtle.verify('HMAC', key, signature, data);
  if (!valid) throw new Error('Assinatura inválida');

  // decode payload
  const payloadStr = payloadB64.replace(/-/g, '+').replace(/_/g, '/');
  const payloadPadded = payloadStr + '='.repeat((4 - payloadStr.length % 4) % 4);
  const payload = JSON.parse(atob(payloadPadded)) as JWTPayload;

  if (payload.exp < Math.floor(Date.now() / 1000)) throw new Error('Token expirado');
  return payload;
}

export async function signJWT(
  payload: Omit<JWTPayload, 'exp'>,
  secret: string,
  expiresInSeconds = 60 * 60 * 24 * 7 // 7 dias
): Promise<string> {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');

  const fullPayload = { ...payload, exp: Math.floor(Date.now() / 1000) + expiresInSeconds };
  const payloadB64 = btoa(JSON.stringify(fullPayload))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');

  const key = await getHmacKey(secret, ['sign']);
  const data = new TextEncoder().encode(`${header}.${payloadB64}`);
  const signature = await crypto.subtle.sign('HMAC', key, data);

  return `${header}.${payloadB64}.${base64urlEncode(signature)}`;
}

export async function hashPassword(password: string): Promise<string> {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');

  const keyMaterial = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']
  );
  const derived = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial, 256
  );
  const hashHex = Array.from(new Uint8Array(derived))
    .map(b => b.toString(16).padStart(2, '0')).join('');

  return `pbkdf2:100000:${saltHex}:${hashHex}`;
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const parts = stored.split(':');
  if (parts.length !== 4 || parts[0] !== 'pbkdf2') return false;

  const [, iterStr, saltHex, storedHash] = parts;
  const iterations = parseInt(iterStr, 10);
  const salt = new Uint8Array(saltHex.match(/.{2}/g)!.map(h => parseInt(h, 16)));

  const keyMaterial = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']
  );
  const derived = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
    keyMaterial, 256
  );
  const hashHex = Array.from(new Uint8Array(derived))
    .map(b => b.toString(16).padStart(2, '0')).join('');

  return hashHex === storedHash;
}

export async function authMiddleware(c: Context<AppContext>, next: Next) {
  const authHeader = c.req.header('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Não autorizado' }, 401);
  }

  const token = authHeader.slice(7);
  try {
    const payload = await verifyJWT(token, c.env.JWT_SECRET);
    c.set('user', payload);
    await next();
  } catch {
    return c.json({ error: 'Token inválido ou expirado' }, 401);
  }
}
