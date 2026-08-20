---
name: tailscale-remote-access
description: "Acesso remoto a serviços do Hermes (WebUI, dashboard) via Tailscale — instalação, tailscale serve (HTTPS + MagicDNS), diagnóstico de conectividade e endurecimento de ACLs."
version: 1.0.0
author: HAL 9000
platforms: [linux]
metadata:
  hermes:
    tags: [tailscale, vpn, webui, remote, acl, https, magicdns]
    category: hermes-ops
    related_skills: [gateway-troubleshooting]
---

# Acesso Remoto via Tailscale (Hermes WebUI)

Como expor o Hermes WebUI (ou outros serviços locais) para acesso remoto seguro via Tailscale — tailnet privada, sem exposição à internet pública.

## ⚠️ ESTADO ATUAL (ago/2026): Tailscale REMOVIDO — Cloudflare Tunnel é a rota ativa

O Tailscale foi **desinstalado do host** (ago/2026) porque a rede corporativa MPT
bloqueia o control plane (`controlplane.tailscale.com` — ver seção "Falha em rede
corporativa"). A rota de acesso remoto ativa agora é o **Cloudflare Tunnel**:
`https://webui.asideia.net` (domínio `asideia.net`, túnel `webui-tunnel`).

- **Se o acesso remoto for requisitado:** NÃO tentar reinstalar Tailscale primeiro —
  o fluxo atual é Cloudflare Tunnel (ver `references/cloudflare-tunnel-setup.md`).
- **Remoção do Tailscale (para referência):** `sudo tailscale serve reset` →
  `sudo systemctl stop tailscaled && sudo systemctl disable tailscaled` →
  `sudo apt remove -y tailscale` (opcional: `sudo rm -rf /var/lib/tailscale`).
- O conteúdo abaixo sobre Tailscale permanece como referência histórica/para
  outros ambientes que não tenham a restrição corporativa.

## Quando Ativar

- Usuário quer acessar o WebUI/dashboard de fora da LAN (celular, notebook, outra máquina)
- Usuário instalou/configurou Tailscale e precisa de ajuda para expor um serviço
- Acesso remoto funciona no ping mas falha no HTTP/HTTPS
- Usuário quer restringir/quebrar o "allow all" das ACLs da tailnet

## Topologia do Ambiente (PRT14/Hermes)

| Serviço | Porta | Exposição no compose |
|---------|-------|----------------------|
| WebUI | 8787 | `0.0.0.0:8787` (todas as interfaces) |
| API Hermes | 8642 | `127.0.0.1` (só local) |
| Dashboard | 9119 | `127.0.0.1` (só local) |

- Como o WebUI já escuta em `0.0.0.0`, **não precisa mexer no docker-compose** para o Tailscale alcançá-lo — basta o host entrar na tailnet.
- Host: Ubuntu 24.04 LTS, hostname tailscale `as7-hermes-docker`, tailnet `tail15f7e7`, IP `100.104.19.99`.
- Endereços finais conhecidos: `https://as7-hermes-docker.tail15f7e7.ts.net` (serve) e `http://as7-hermes-docker:8787` (HTTP direto).

## Passo a Passo

### 1. Instalar no host (Ubuntu/Debian)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
# ou
sudo apt-get update && sudo apt-get install -y tailscale
```

### 2. Autenticar

```bash
sudo tailscale up
```

Abre link de login (criar conta/tailnet na primeira vez). Verificar IP:

```bash
tailscale ip -4   # ex: 100.104.19.99
tailscale status  # mostra nome da máquina + dispositivos na tailnet
```

### 3. Expor serviço com HTTPS (tailscale serve)

⚠️ **A sintaxe do CLI mudou nas versões novas.** A forma antiga (`tailscale serve https / http://...`) é **deprecada** — o próprio CLI devolve erro sugerindo o comando novo. Usar:

```bash
sudo tailscale serve --bg http://127.0.0.1:8787
sudo tailscale serve status
```

Isso cria proxy reverso na porta 443 da máquina com HTTPS + certificado automático (Let's Encrypt via Tailscale), restrito à tailnet. Endereço resultante:

```
https://<hostname>.<tailnet>.ts.net
```

### 4. Acessar do cliente

| Situação | URL |
|----------|-----|
| Com serve ativo | `https://<hostname>.<tailnet>.ts.net` (HTTPS, sem porta) |
| Sem serve | `http://<hostname>:8787` (HTTP direto) |

- `tailscale serve` (padrão) = só dispositivos da tailnet. `tailscale funnel` = internet pública — **evitar** para o WebUI.
- O nome MagicDNS (`as7-hermes-docker`) funciona mesmo se o IP mudar — preferir nome a IP.

## Diagnóstico: ping OK mas HTTP não conecta

Ladder de verificação (nesta ordem):

1. **Serviço de pé?** — do container: `curl -s -o /dev/null -w "%{http_code}" http://hermes-webui:8787` → esperar 200
2. **Porta ouvindo no host?** — `sudo ss -tlnp | grep 8787` → esperar `0.0.0.0:8787` ou `*:8787`
3. **Teste local pelo IP tailscale:** `curl -s -o /dev/null -w "%{http_code}" http://<IP-TS>:8787`
   - 200 → host OK, problema no cliente/firewall dele
   - falha → firewall do host
4. **Firewall do host:** `sudo ufw status`; `sudo iptables -L INPUT -n | grep 8787`
   - Se ufw ativo: `sudo ufw allow in on tailscale0`
5. **Do cliente Windows (PowerShell):** `Test-NetConnection <IP-TS> -Port 8787`
   - `TcpTestSucceeded: True` → porta chega; problema é URL no navegador (usar http://, não https://, quando não há serve)
   - `False` → firewall do Windows bloqueando

## Falha em rede corporativa (Tailscale bloqueado) — caso MPT/ago-2026

**Sintoma típico:** no cliente dentro da rede corporativa, `tailscale status` mostra
o peer `offline`, e `tailscale netcheck` falha com:

```
No DERP map from tailscaled; using default.
attempting to fetch a DERPMap from https://controlplane.tailscale.com
Failed to fetch a DERP map, so netcheck cannot continue.
fetch prodDERPMap failed: ... context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

**Diagnóstico (importante):** o erro do DERP map NÃO é bloqueio de UDP — o cliente
**nem chegou a testar** UDP/DERP. Ele não consegue falar com o **servidor de controle**
(`controlplane.tailscale.com`) — a rede corporativa **bloqueia o domínio** (blocklist
de VPN) ou exige proxy HTTP que o tailscaled não usa. Sem o control plane, o Tailscale
não faz nada (nem login, nem mapa, nem relay). Ou seja: **Tailscale inviável nessa rede**,
independente de qualquer configuração no host/servidor.

**Confirmação em 10s (no cliente):**
```bash
curl -v --max-time 8 https://controlplane.tailscale.com/derpmap/default
# timeout → domínio bloqueado (blocklist)  |  responde → problema é outro (proxy?)
curl -v --max-time 8 https://www.google.com   # controle: HTTPS básico funciona?
```

**Regra de ouro:** se **Telegram/site HTTPS funciona** mas `controlplane.tailscale.com`
não responde → bloqueio seletivo por domínio de VPN. A solução é um **túnel HTTPS:443**
com domínio próprio (não está na blocklist), NÃO brigar com a rede.

**Alternativas (funcionam atrás de CGNAT e de proxy corporativo — HTTPS:443):**

| Solução | Como burla | Custo | Notas |
|---------|-----------|-------|-------|
| **Cloudflare Tunnel** (cloudflared) | Túnel HTTPS:443 de SAÍDA + domínio próprio | Grátis + domínio ~R$40/ano | **Recomendada**: sem porta aberta, TLS automático, Cloudflare Access grátis (email/OTP) |
| **ngrok Free** | URL `xxx.ngrok-free.app` via HTTPS | $0 | ⚠️ 1 GB/mês transferência, domínio feio, banner "free" p/ visitantes; bom p/ POC |
| **IP público + DDNS** (porta no roteador) | Acesso direto por IP/domínio dinâmico | DDNS grátis | ⚠️ Depende do ISP liberar (CGNAT!), **expõe o serviço à internet aberta** (bots/brute-force) — só se precisar de acesso fora da tailnet |

- CGNAT (IP `100.64.0.0/10`) **não afeta Tailscale** (é o caso de uso dele) nem túneis HTTPS — afeta apenas acesso direto por IP.
- Diagnosticar CGNAT do lado servidor: `curl -s https://api.ipify.org` → se começar com `100.` está na faixa CGNAT.
- **Não desistir do Tailscale por causa de 1 rede bloqueada**: ele continua válido para as demais origens (celular, casa). O túnel HTTPS é complemento para a rede corporativa.

## Endurecimento de ACLs (default-deny explícito)

Tailscale é **deny-by-default por design**: o "allow all" é apenas o default quando NÃO há seção de política definida no policy file. Ao definir `acls` OU `grants`, tudo que não for listado é negado — basta **comentar/remover a regra genérica** e listar as permissões explícitas.

### ⚠️ Duas sintaxes: `acls` (legado) vs `grants` (novo — preferir)

- **`grants`** é o formato NOVO e recomendado; tailnets criadas recentemente já vêm com `grants` no JSON (o painel mostra `grants` em vez de `acls`). Grants têm `accept` implícito (sem campo `action`) e separam protocolo/porta no campo `ip`.
- **`acls`** é o formato legado (campo `action` explícito, `dst` com `host:porta`). Funciona indefinidamente, mas não recebe features novas.
- **Sintaxe de destino difere:** em `grants`, `dst` NÃO leva porta (fica no campo `ip`); em `acls`, a porta vai no `dst` (`host:443`).
- Sempre perguntar/verificar qual formato o painel do usuário usa antes de montar o JSON.

Policy file em **grants** (usado na PRT14 — portas 443 e 22 liberadas, resto negado):

```json
{
  "grants": [
    {
      "src": ["autogroup:member"],
      "dst": ["as7-hermes-docker"],
      "ip": ["tcp:443"]
    },
    {
      "src": ["autogroup:member"],
      "dst": ["as7-hermes-docker"],
      "ip": ["tcp:22"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self"],
      "users": ["autogroup:nonroot", "root"]
    }
  ]
}
```

Policy file em **acls** (legado, equivalente):

```json
{
  "acls": [
    // {"action": "accept", "src": ["*"], "dst": ["*:*"]},  ← comentada
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["*:icmp"]
    },
    {
      "action": "accept",
      "src": ["autogroup:member"],
      "dst": ["as7-hermes-docker:443"]
    }
    // SSH: "dst": ["as7-hermes-docker:22"]
  ]
}
```

Regras (ambas as sintaxes):
- `autogroup:member` = todos os usuários da tailnet; restringir com email direto se preciso
- Nome MagicDNS no `dst` é imune a mudança de IP (melhor que IP fixo)
- **Ordem importa:** deny antes de accept (first-match-wins) — em `grants` não há deny explícito (deny-by-default já), então a ordem só importa se misturar com `acls`
- Bloquear só a porta 8787 na tailnet mantém o HTTPS (443) e a LAN local intactos
- Se errar o JSON e derrubar tudo: **o admin console continua acessível** (ACLs não bloqueiam o painel) — reverter por lá
- Não esquecer SSH na ACL se o usuário depende de acesso remoto ao host
- **ICMP/ping é implícito** quando há TCP/UDP liberado entre o par — não precisa regra separada

## Pitfalls

- **Sintaxe antiga do `tailscale serve`:** `tailscale serve https / http://...` retorna erro "the CLI for serve and funnel has changed" com o comando novo sugerido. Usar `tailscale serve --bg http://127.0.0.1:PORTA`.
- **Navegador forçando HTTPS (HSTS):** se o usuário abriu https:// antes e falhou, o navegador pode insistir em https — testar em aba anônima ou limpar HSTS.
- **URL errada no cliente:** sem serve ativo, usar `http://` (não https) e sem `.ts.net` — o MagicDNS resolve, mas sem serve não há 443.
- **Tudo no host vs container:** Tailscale instala no **host** (onde roda o Docker), não no container. Do container não há docker.sock nem acesso à interface tailscale.
- **ACL "allow all" padrão:** é só default quando `acls` ausente; definir `acls` ativa deny-by-default — o usuário pode achar que "está tudo liberado" quando na verdade é o comportamento padrão.

## Arquivos

- `references/cloudflare-tunnel-setup.md` — setup completo do Cloudflare Tunnel (rota ativa, ago/2026): domínio, túnel, rota, Access e pitfalls (HERMES_WEBUI_PASSWORD no compose)
- `templates/tailscale-acl-explicit.json` — policy file de ACLs explícitas (formato LEGADO) pronto para editar/colar
- `templates/tailscale-grants-explicit.json` — policy file em formato GRANTS (novo, recomendado — usado na PRT14)
