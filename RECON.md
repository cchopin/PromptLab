# Reconnaissance d'un endpoint de chat LLM

Langue : Français | [English](RECON.en.md)

Mémo pratique pour identifier l'API d'une nouvelle box (HTB ou autre) et la
configurer comme cible PromptLab. À garder sous la main à chaque nouveau lab.

## Checklist DevTools (méthode fiable)

1. Ouvrir la page du lab dans le navigateur.
2. Ouvrir les DevTools (F12), onglet Network.
3. Activer le filtre "Fetch/XHR" et cocher "Preserve log".
4. Envoyer un message dans le chat.
5. Observer les requêtes et noter quatre choses:
   - URL exacte (Request URL)
   - Méthode (POST le plus souvent)
   - Corps envoyé (onglet Payload) : le nom du champ qui contient le prompt
   - Réponse (onglet Response) : où se trouve le texte du bot
6. Repérer le nombre de requêtes déclenchées par un seul envoi. Un chat simple
   fait une requête. Un chat asynchrone en fait deux (voir plus bas).

Astuce : l'onglet Response du GET qui liste les messages révèle souvent d'un
coup les noms de champs (`content`, `sender`, valeurs `Bot` / `Victim`), ce qui
renseigne directement `content_field`, `sender_field` et `bot_value`.

## Les deux patterns d'API courants

### Pattern 1 : requête unique (synchrone)

Un POST envoie le prompt, la réponse de l'IA est directement dans le corps de
réponse. Connecteur `htb` en mode simple, ou `raw_http`.

```json
{
  "connector": "htb",
  "url": "http://CIBLE:PORT/api/chat",
  "prompt_field": "message",
  "response_path": "$.response"
}
```

`response_path` est le chemin jsonpath vers le texte (ex: `$.reply`,
`$.data.answer`, `$.choices[0].message.content`).

### Pattern 2 : POST puis polling (asynchrone), type TrynaSob

Un POST d'envoi accuse simplement réception (`{"message": "delivered"}`), et la
réponse de l'IA apparaît ensuite dans une seconde URL (liste des messages) lue
en GET. Connecteur `htb` avec `poll_url`.

```json
{
  "connector": "htb",
  "url": "http://CIBLE:PORT/api/messages/send",
  "prompt_field": "content",
  "poll_url": "http://CIBLE:PORT/api/messages",
  "poll_retries": 8,
  "poll_delay_ms": 1000,
  "messages_path": "$",
  "sender_field": "sender",
  "bot_value": "Bot",
  "victim_value": "Victim",
  "content_field": "content"
}
```

Comment le reconnaître : un seul envoi déclenche deux requêtes (un POST court
puis un GET), et le POST ne contient pas la réponse du bot. Le moteur poste le
message puis interroge `poll_url` jusqu'à trouver le premier message `Bot` situé
après le dernier message `Victim`.

## Indices rapides selon le serveur

- `Cannot POST /xxx` en HTML : backend Express (Node). La route est fausse, la
  vraie existe ailleurs. Chercher `/api/...` dans l'onglet Network.
- Réponse JSON `{"choices": [...]}` : API compatible OpenAI, utiliser le
  connecteur `openai` avec `base_url`.
- Réponse `{"content": [{"type": "text", ...}]}` : API Anthropic Messages.
- 401 / 403 : header d'auth manquant, l'ajouter dans `headers`.

## Si le JS est minifié

Onglet Sources, puis recherche globale (Cmd+Shift+F ou Ctrl+Shift+F) sur
`fetch(`, `axios`, `/api/`, `/send` ou `/message`. Les routes apparaissent
souvent en clair même dans un bundle.

## Raccourci : copier la requête depuis le navigateur

Aucun outil externe requis. Dans l'onglet Network des DevTools, clic droit sur la
requête d'envoi, puis "Copy > Copy as cURL". La commande obtenue contient tout :
l'URL, la méthode, les headers et le corps (donc le nom du champ du prompt). Il
suffit de la relire pour construire l'auth_config.

Exemple d'une commande copiée et sa traduction en cible raw_http :

```
curl 'http://CIBLE:PORT/api/submit' -X POST \
  -H 'Content-Type: application/json' \
  --data-raw '{"application":"..."}'
```

devient :

```json
{
  "connector": "raw_http",
  "url": "http://CIBLE:PORT/api/submit",
  "method": "POST",
  "body_type": "json",
  "body_template": "{\"application\": \"{PROMPT}\"}",
  "response_path": "$.decision"
}
```

Si la réponse est une page HTML (et non du JSON), voir la section suivante.

## Cas particulier : la réponse est une page HTML

Certains labs (ex: un formulaire de demande relu par une IA) repostent la page
entière avec la décision insérée dans le HTML, au lieu de renvoyer du JSON. Dans
ce cas `response_path` ne trouve rien et le connecteur retombe sur le HTML brut.

Deux conséquences pratiques :

- Le texte du run contient toute la page. C'est normal, la réponse de l'IA (par
  exemple "APPROVED" ou "DENIED") est quelque part dedans.
- Pour classer automatiquement, utiliser le scoring par regex de la cible :

```json
{
  "connector": "raw_http",
  "url": "http://CIBLE:PORT/api/submit",
  "method": "POST",
  "body_type": "form",
  "query_field": "application",
  "scoring": {
    "success_regex": "APPROVED|ACCEPTED|granted",
    "refusal_regex": "DENIED|REJECTED|refused"
  }
}
```

Le champ `scoring` classe le run en succès ou échec selon ce que contient la
réponse, sans avoir à lire toute la page à la main. Regarder d'abord une réponse
réelle pour caler les mots exacts (APPROVED, Decision: ACCEPT, etc.).
