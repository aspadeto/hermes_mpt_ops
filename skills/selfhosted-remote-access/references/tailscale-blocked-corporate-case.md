# Sessão 2026-08-03 — Diagnóstico real: Tailscale bloqueado na rede MPT

## Contexto
Usuário (rede corporativa MPT) não conseguia acessar o WebUI do Hermes via
Tailscale. Telegram funcionava normalmente na mesma rede.

## Erro exato do cliente Tailscale (rede MPT)

```
2026/08/03 13:14:18 No DERP map from tailscaled; using default.
2026/08/03 13:14:18 attempting to fetch a DERPMap from https://controlplane.tailscale.com
2026/08/03 13:14:28 Failed to fetch a DERP map, so netcheck cannot continue.
fetch prodDERPMap failed: Get "https://controlplane.tailscale.com/derpmap/default":
context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

### Leitura do erro (importante)
- **NÃO é bloqueio de UDP** — o cliente nem chegou a testar UDP/DERP
- É o **servidor de controle** (`controlplane.tailscale.com`) que não responde
- "Client.Timeout exceeded" = firewall dropa silenciosamente OU proxy corporativo
  que o tailscaled não usa
- Sem control plane, o Tailscale não faz NADA (nem login, nem DERP, nada)

### Teste de confirmação (10s, na rede de origem)
```bash
curl -v --max-time 8 https://controlplane.tailscale.com/derpmap/default  # timeout
curl -v --max-time 8 https://www.google.com                                # OK
```
Resultado: bloqueio seletivo por domínio → Tailscale inviável → túnel HTTPS.

## Decisão tomada
- **Removido Tailscale do host** (`sudo systemctl stop/disable tailscaled` + `apt remove`)
- **Escolhido Cloudflare Tunnel** + domínio `asideia.net` (registrado no próprio Cloudflare)
- Motivos: grátis, HTTPS puro (443), funciona atrás de CGNAT, Access grátis,
  sem banner, domínio próprio (não bloqueado por blocklist de VPN)

## Nota sobre CGNAT (Claro Residencial)
- IP atual do host: 181.220.199.51 (Claro NXT, Porto Velho) — **fora** da faixa
  CGNAT (100.64.0.0/10) no momento
- Claro tem migrado clientes residenciais para CGNAT — **não afeta** o túnel
  (conexão de saída), mas impediria acesso direto por IP + port forwarding

## Lição de segurança
Expor o Hermes (agente que executa comandos) por IP público + porta aberta é
arriscado — bots de brute-force 24/7. Túnel HTTPS (Cloudflare na frente) mantém
o origin oculto. Camadas: Cloudflare Access (e-mail+OTP) + senha do serviço.

## Estado final (2026-08-04)
- `webui.asideia.net` → Cloudflare Tunnel → localhost:8787 (WebUI)
- Cloudflare Access configurado (policy Allow por e-mail)
- Pendente: adicionar `HERMES_WEBUI_PASSWORD` no `environment:` do compose
  (bug descoberto: variável no .env não é injetada no container)
