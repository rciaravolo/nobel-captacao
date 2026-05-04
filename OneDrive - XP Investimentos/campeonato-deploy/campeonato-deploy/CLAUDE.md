# Campeonato da Soneca — Regras e Estrutura

## O Jogo

Os participantes apostam em que hora o grupo chegará ao destino do pedal. Quem acertar mais perto ganha pontos.

- **SAÍDA**: horário em que o grupo parte
- **CHEGADA**: horário real em que o grupo chegou ao destino
- **Palpite**: horário que cada participante apostou para a chegada

---

## Pontuação

| Situação | Pontos |
|---|---|
| Palpite mais próximo da chegada real **E** a menos de 3 min | **3 pts** |
| Palpite mais próximo da chegada real **mas** a mais de 3 min | **1 pt** (Campeão da Rodada) |
| Não é o mais próximo, mas fica a até 3 min da chegada real | **1 pt** |
| Erra por mais de 3 minutos e não é o mais próximo | **0 pts** |

### Regra do empate no "mais próximo"
Se dois palpites ficarem à mesma distância da chegada real, ambos são considerados "mais próximos" e ambos recebem a pontuação correspondente.

---

## Critérios de Desempate (geral)

1. Maior número de pontos acumulados
2. Mais acertos exatos (0 minutos de diferença)
3. Mais vezes "mais perto" (ganhou a rodada)
4. Menor erro total acumulado no campeonato

---

## Participantes

| ID | Nome |
|---|---|
| aaa-0001 | Léo |
| aaa-0002 | Victor |
| aaa-0003 | Bradock |
| aaa-0004 | Luka |
| aaa-0005 | Gaspar |
| aaa-0006 | Paulo |
| aaa-0007 | Vini |

> Victor também atende por "Hair Studios" nos registros.
> Léo também aparece como "Leo PS5".

---

## Banco de Dados (Cloudflare D1)

- **database_id**: `5e44b5ed-056a-4714-9472-8ae4a0e12d29`
- **championship_id**: `champ-soneca`
- **slug**: `soneca`

### IDs de rodadas
| Round ID | Número | Data | Saída | Chegada |
|---|---|---|---|---|
| round-soneca-001 | 1 | 2026-04-27 | 14:53 | 16:18 |
| round-soneca-002 | 2 | 2026-04-28 | 14:36 | 16:02 |
| round-soneca-003 | 3 | 2026-04-30 | 14:28 | 15:50 |
| round-soneca-004 | 4 | 2026-05-04 | 14:13 | 15:23 |

### Próxima rodada
Usar ID `round-soneca-005`, número 5.

---

## Como Inserir uma Nova Rodada

### 1. Inserir a rodada
```sql
INSERT INTO rounds (id, championship_id, number, date, leave_time, result, created_at)
VALUES ('round-soneca-00X', 'champ-soneca', X, 'YYYY-MM-DD', 'HH:MM', 'HH:MM', 'YYYY-MM-DDTHH:MM:00.000Z')
```

### 2. Calcular pontos de cada participante

Para cada palpite, calcular `diff = |palpite - chegada_real|` em minutos.

- Encontrar o `min_diff` (menor diferença entre todos)
- Para cada participante:
  - Se `diff == min_diff` E `diff <= 3` → **3 pontos**, `is_closest = 1`
  - Se `diff == min_diff` E `diff > 3`  → **1 ponto**, `is_closest = 1`
  - Se `diff != min_diff` E `diff <= 3` → **1 ponto**, `is_closest = 0`
  - Se `diff != min_diff` E `diff > 3`  → **0 pontos**, `is_closest = 0`

### 3. Inserir os bets
```sql
INSERT INTO bets (id, round_id, participant_id, bet_value, diff_value, points, is_closest, created_at)
VALUES
  ('bet-sX-001', 'round-soneca-00X', 'aaa-000X', 'HH:MM', DIFF, POINTS, IS_CLOSEST, 'YYYY-MM-DDTHH:MM:00.000Z'),
  ...
```

### 4. Deploy
```
npx wrangler pages deploy . --project-name campeonato
```

---

## Exemplo de Cálculo

**Rodada 3 — 30/04, chegada real: 15:50**

| Participante | Palpite | Diff | Pontos |
|---|---|---|---|
| Bradock | 15:58 | 8 min | **1** (mais próximo, mas > 3 min) |
| Gaspar | 16:00 | 10 min | 0 |
| Paulo | 16:04 | 14 min | 0 |
| Victor | 16:05 | 15 min | 0 |
| Léo | 16:08 | 18 min | 0 |
| Luka | 16:11 | 21 min | 0 |
| Vini | 16:15 | 25 min | 0 |
