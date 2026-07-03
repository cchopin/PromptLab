# Recon of an LLM chat endpoint

Language: [Francais](RECON.md) | English

Practical memo to identify the API of a new box (HTB or other) and configure it
as a PromptLab target. Keep it handy for every new lab.

## DevTools checklist (reliable method)

1. Open the lab page in the browser.
2. Open DevTools (F12), Network tab.
3. Enable the "Fetch/XHR" filter and check "Preserve log".
4. Send a message in the chat.
5. Look at the requests and note four things:
   - Exact URL (Request URL)
   - Method (POST most of the time)
   - Request body (Payload tab): the name of the field holding the prompt
   - Response (Response tab): where the bot text sits
6. Count how many requests one send triggers. A simple chat makes one. An async
   chat makes two (see below).

Tip: the Response tab of the GET that lists messages often reveals the field
names at once (`content`, `sender`, values `Bot` / `Victim`), which directly
gives `content_field`, `sender_field` and `bot_value`.

## The two common API patterns

### Pattern 1: single request (synchronous)

A POST sends the prompt, the AI reply is directly in the response body.
Connector `htb` in simple mode, or `raw_http`.

```json
{
  "connector": "htb",
  "url": "http://TARGET:PORT/api/chat",
  "prompt_field": "message",
  "response_path": "$.response"
}
```

`response_path` is the jsonpath to the text (e.g. `$.reply`, `$.data.answer`,
`$.choices[0].message.content`).

### Pattern 2: POST then polling (asynchronous), TrynaSob style

A send POST only acknowledges receipt (`{"message": "delivered"}`), and the AI
reply then appears in a second URL (message list) read via GET. Connector `htb`
with `poll_url`.

```json
{
  "connector": "htb",
  "url": "http://TARGET:PORT/api/messages/send",
  "prompt_field": "content",
  "poll_url": "http://TARGET:PORT/api/messages",
  "poll_retries": 8,
  "poll_delay_ms": 1000,
  "messages_path": "$",
  "sender_field": "sender",
  "bot_value": "Bot",
  "victim_value": "Victim",
  "content_field": "content"
}
```

How to recognize it: one send triggers two requests (a short POST then a GET),
and the POST does not contain the bot reply. The engine posts the message then
polls `poll_url` until it finds the first `Bot` message after the last message
from the sender (`victim_value`, sometimes "User" instead of "Victim").

## Quick clues by server

- `Cannot POST /xxx` as HTML: Express (Node) backend. The route is wrong, the
  real one is elsewhere. Look for `/api/...` in the Network tab.
- JSON response `{"choices": [...]}`: OpenAI compatible API, use the `openai`
  connector with `base_url`.
- Response `{"content": [{"type": "text", ...}]}`: Anthropic Messages API.
- 401 / 403: missing auth header, add it under `headers`.

## Shortcut: copy the request from the browser

No external tool required. In the Network tab, right click the send request, then
"Copy > Copy as cURL". The command contains everything: URL, method, headers and
body (so the prompt field name). Just read it to build the auth_config.

Example of a copied command and its translation into a raw_http target:

```
curl 'http://TARGET:PORT/api/submit' -X POST \
  -H 'Content-Type: application/json' \
  --data-raw '{"application":"..."}'
```

becomes:

```json
{
  "connector": "raw_http",
  "url": "http://TARGET:PORT/api/submit",
  "method": "POST",
  "body_type": "json",
  "body_template": "{\"application\": \"{PROMPT}\"}",
  "response_path": "$.decision"
}
```

If the response is an HTML page (not JSON), see the next section.

## Special case: the response is an HTML page

Some labs (e.g. a request form reviewed by an AI) repost the whole page with the
decision embedded in the HTML, instead of returning JSON. In that case
`response_path` finds nothing and the connector falls back to the raw HTML.

Two practical consequences:

- The run text contains the whole page. That is normal; the AI reply (for
  example "APPROVED" or "DENIED") is somewhere inside.
- To classify automatically, use the target's regex scoring:

```json
{
  "connector": "raw_http",
  "url": "http://TARGET:PORT/api/submit",
  "method": "POST",
  "body_type": "form",
  "query_field": "application",
  "scoring": {
    "success_regex": "APPROVED|ACCEPTED|granted",
    "refusal_regex": "DENIED|REJECTED|refused"
  }
}
```

The `scoring` field classifies the run as success or fail based on what the
response contains, without reading the whole page by hand. Look at a real
response first to tune the exact words (APPROVED, Decision: ACCEPT, etc.).
