# IPv6 + CGNAT (Claro) — alternativa ao túnel Cloudflare

**Descoberta (ago/2026):** Claro usa **CGNAT só no IPv4**. No IPv6, cada
dispositivo recebe prefixo delegado (ex: `/56`) e tem IPv6 público **roteável
globalmente** — nada de CGNAT.

## Como testar

```bash
# IPv6 do dispositivo (VM/PC)
curl -6 ifconfig.me
# → 2804:14d:cc86:402a:be24:11ff:febb:21ee

# IPv6 WAN do roteador (interface wan0)
ip -6 addr show dev wan0 scope global
# → 2804:14d:cc86:1000::30e/64
```

## Firewall do roteador ainda controla

| Endereço testado | O que valida |
|------------------|--------------|
| IPv6 da VM (`2804:...:21ee`) porta 8787 | Firewall permite tráfego **direto** pro dispositivo (sem NAT) |
| IPv6 do roteador (`2804:...:30e`) porta 8787 | Roteador faz DNAT/port-forward pro IPv6 da VM |

**No IPv6 não precisa de NAT/port forwarding** — o normal é liberar a porta no
firewall IPv6 do roteador pro **IPv6 da VM**. Mas roteadores ISP (Claro) vêm com
firewall IPv6 **bloqueando tudo por padrão** — precisa criar regra:

```bash
# Exemplo regra firewall IPv6 (interface web do roteador)
Nome: WebUI-Hermes
Protocolo: TCP
Porta externa: 8787
Porta interna: 8787
Endereço IPv6 destino: 2804:14d:cc86:402a:be24:11ff:febb:21ee
Ação: Permitir / Allow
Direção: Entrada (WAN → LAN)
```

**Teste externo** (de outra rede, ex: celular 4G):
```bash
nmap -6 -p 8787 2804:14d:cc86:402a:be24:11ff:febb:21ee
# Open = funcionando | Filtered/Closed = firewall bloqueando
```

> ⚠️ **SSH (porta 22) exposto no IPv6 público** — se não foi intencional, fechar
> no firewall do roteador ou configurar sshd para ouvir só em interface
> específica.

## Trade-off túnel vs IPv6 direto

| Aspecto | Cloudflare Tunnel | IPv6 direto |
|---------|-------------------|-------------|
| Segurança | Access (e-mail+OTP) + senha WebUI + WAF + DDoS | Só firewall do roteador + senha WebUI |
| CGNAT | Funciona sempre | Não afetado (IPv6 não tem CGNAT) |
| Domínio | `webui-01.asideia.net` (fixo, bonito) | IPv6 numérico (feio) ou DDNS AAAA |
| Configuração | Token no dashboard + cloudflared | Regra firewall IPv6 no roteador |
| Manutenção | Baixa (dashboard) | Depende do roteador ISP (pode travar) |

**Recomendação:** manter o **Cloudflare Tunnel como principal** (já ativo, 2
camadas, domínio fixo). IPv6 direto como **fallback** se túnel falhar — mas
exige configurar firewall no roteador da Claro (interface pode ser limitada).