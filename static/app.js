// JavaScript vanilla de PromptLab.
// Gere l'envoi async des prompts, la relance des runs, le test des chaines
// et l'editeur de steps de chaine.

// Helper de traduction cote client. Les chaines sont injectees dans window.I18N
// par le layout selon la langue courante; repli sur la cle si absente.
function tr(key) {
  return (window.I18N && window.I18N[key]) ? window.I18N[key] : key;
}

// Aide : POST JSON et retour du JSON de reponse
async function postJson(url, body) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return resp.json();
}

// Aide : POST simple (sans corps) pour relance / test
async function postEmpty(url) {
  const resp = await fetch(url, { method: "POST" });
  return resp.json();
}

// Page campagne : envoi rapide, relance, lancement de chaine
function initCampaignPage() {
  const panel = document.getElementById("send-panel");
  if (!panel) return;

  const sendUrl = panel.dataset.sendUrl;
  const phUrlBase = panel.dataset.phUrl; // se termine par /0/placeholders
  const select = document.getElementById("payload-select");
  const freeWrap = document.getElementById("free-prompt-wrap");
  const phWrap = document.getElementById("placeholders-wrap");
  const phFields = document.getElementById("placeholders-fields");
  const preview = document.getElementById("template-preview");
  let currentTemplate = "";

  // Changement de payload : charger les placeholders ou revenir au texte libre
  select.addEventListener("change", async () => {
    const pid = select.value;
    if (!pid) {
      freeWrap.classList.remove("hidden");
      phWrap.classList.add("hidden");
      phFields.innerHTML = "";
      return;
    }
    freeWrap.classList.add("hidden");
    const url = phUrlBase.replace("/0/", "/" + pid + "/");
    const data = await (await fetch(url)).json();
    currentTemplate = data.content || "";
    phFields.innerHTML = "";
    (data.placeholders || []).forEach((key) => {
      const div = document.createElement("div");
      const label = document.createElement("label");
      label.textContent = key;
      const input = document.createElement("input");
      input.type = "text";
      input.dataset.key = key;
      input.className = "ph-input";
      input.addEventListener("input", renderPreview);
      div.appendChild(label);
      div.appendChild(input);
      phFields.appendChild(div);
    });
    phWrap.classList.remove("hidden");
    renderPreview();
  });

  function collectPlaceholders() {
    const values = {};
    phFields.querySelectorAll(".ph-input").forEach((el) => {
      values[el.dataset.key] = el.value;
    });
    return values;
  }

  function renderPreview() {
    let text = currentTemplate;
    const values = collectPlaceholders();
    Object.keys(values).forEach((k) => {
      if (values[k]) text = text.split("{" + k + "}").join(values[k]);
    });
    preview.textContent = text;
  }

  // Bouton Envoyer
  document.getElementById("send-btn").addEventListener("click", async () => {
    const status = document.getElementById("send-status");
    status.textContent = tr("js_sending");
    const body = {};
    if (select.value) {
      body.payload_id = select.value;
      body.placeholders = collectPlaceholders();
    } else {
      body.free_prompt = document.getElementById("free-prompt").value;
    }
    try {
      const run = await postJson(sendUrl, body);
      showResult(run);
      status.textContent = "";
    } catch (e) {
      status.textContent = tr("js_error") + ": " + e;
    }
  });

  function showResult(run) {
    document.getElementById("send-result").classList.remove("hidden");
    document.getElementById("result-prompt").textContent = run.prompt_sent || "";
    document.getElementById("result-response").textContent =
      run.text || run.raw_response || "";
    document.getElementById("result-meta").textContent =
      tr("js_result") + ": " + (run.result || "-") +
      " | " + tr("js_status") + ": " + (run.http_status || "-") +
      " | " + tr("js_duration") + ": " + (run.duration_ms || "-") + " ms";
    const link = document.getElementById("result-link");
    link.href = "/runs/" + run.id;
  }

  bindReplayButtons();
  bindChainButtons();
}

// Boutons relancer (present sur campagne et detail run)
function bindReplayButtons() {
  document.querySelectorAll(".replay-btn").forEach((btn) => {
    if (btn.dataset.bound) return;
    btn.dataset.bound = "1";
    btn.addEventListener("click", async () => {
      btn.textContent = "...";
      try {
        await postEmpty(btn.dataset.url);
        location.reload();
      } catch (e) {
        btn.textContent = tr("js_error");
      }
    });
  });
}

// Boutons lancer une chaine
function bindChainButtons() {
  document.querySelectorAll(".run-chain-btn").forEach((btn) => {
    if (btn.dataset.bound) return;
    btn.dataset.bound = "1";
    btn.addEventListener("click", async () => {
      const out = document.getElementById("chain-result");
      if (out) out.textContent = tr("js_chain_running");
      try {
        const data = await postEmpty(btn.dataset.url);
        const n = (data.runs || []).length;
        if (out) out.textContent = tr("js_chain_done_1") + n + tr("js_chain_done_2");
        setTimeout(() => location.reload(), 800);
      } catch (e) {
        if (out) out.textContent = tr("js_error") + ": " + e;
      }
    });
  });
}

// Editeur de chaine : ajout/suppression de steps et serialisation JSON
function initChainEditor() {
  const list = document.getElementById("steps-list");
  if (!list) return;

  const labels = JSON.parse(
    document.getElementById("payloads-labels").textContent || "[]"
  );
  const existing = JSON.parse(
    document.getElementById("chain-steps-data").textContent || "[]"
  );

  function payloadOptions(selected) {
    let html = '<option value="">' + escapeHtml(tr("free_text_option")) + '</option>';
    labels.forEach((p) => {
      const sel = String(p.id) === String(selected) ? " selected" : "";
      html += '<option value="' + p.id + '"' + sel + ">" + escapeHtml(p.label) + "</option>";
    });
    return html;
  }

  function addStep(data) {
    data = data || {};
    const idx = list.children.length + 1;
    const cond_next = data.condition_next || {};
    const cond_stop = data.condition_stop || {};
    const div = document.createElement("div");
    div.className = "panel panel-soft step-row";
    div.innerHTML =
      '<div class="flex-between"><strong>' + escapeHtml(tr("js_step")) + ' <span class="step-num">' + idx + '</span></strong>' +
      '<button type="button" class="btn btn-sm btn-danger remove-step">' + escapeHtml(tr("js_remove")) + '</button></div>' +
      '<label>Payload</label><select class="step-payload">' + payloadOptions(data.payload_id) + '</select>' +
      '<label>' + escapeHtml(tr("js_free_text_if_no_payload")) + '</label>' +
      '<textarea class="step-prompt">' + escapeHtml(data.prompt || "") + '</textarea>' +
      '<label>' + escapeHtml(tr("placeholders")) + ' (JSON)</label>' +
      '<input type="text" class="step-ph" value=\'' + escapeAttr(JSON.stringify(data.placeholders || {})) + '\'>' +
      '<div class="form-row">' +
      '<div><label>condition_next on_contains</label><input type="text" class="cn-contains" value="' + escapeAttr(cond_next.on_contains || "") + '"></div>' +
      '<div><label>goto (step)</label><input type="number" class="cn-goto" value="' + (cond_next.goto != null ? cond_next.goto : "") + '"></div>' +
      '<div><label>condition_stop on_contains</label><input type="text" class="cs-contains" value="' + escapeAttr(cond_stop.on_contains || "") + '"></div>' +
      '<div><label>delay_ms</label><input type="number" class="step-delay" value="' + (data.delay_ms != null ? data.delay_ms : "") + '"></div>' +
      '</div>';
    list.appendChild(div);
    div.querySelector(".remove-step").addEventListener("click", () => {
      div.remove();
      renumber();
    });
    renumber();
  }

  function renumber() {
    list.querySelectorAll(".step-num").forEach((el, i) => {
      el.textContent = i + 1;
    });
  }

  function serialize() {
    const steps = [];
    list.querySelectorAll(".step-row").forEach((row, i) => {
      let placeholders = {};
      try {
        placeholders = JSON.parse(row.querySelector(".step-ph").value || "{}");
      } catch (e) {
        placeholders = {};
      }
      const step = {
        step: i + 1,
        payload_id: row.querySelector(".step-payload").value
          ? parseInt(row.querySelector(".step-payload").value, 10)
          : null,
        prompt: row.querySelector(".step-prompt").value || null,
        placeholders: placeholders,
      };
      const cnContains = row.querySelector(".cn-contains").value;
      const cnGoto = row.querySelector(".cn-goto").value;
      if (cnContains || cnGoto) {
        step.condition_next = {};
        if (cnContains) step.condition_next.on_contains = cnContains;
        if (cnGoto) step.condition_next.goto = parseInt(cnGoto, 10);
      }
      const csContains = row.querySelector(".cs-contains").value;
      if (csContains) step.condition_stop = { on_contains: csContains };
      const delay = row.querySelector(".step-delay").value;
      if (delay) step.delay_ms = parseInt(delay, 10);
      steps.push(step);
    });
    return steps;
  }

  document.getElementById("add-step-btn").addEventListener("click", () => addStep());

  document.getElementById("chain-form").addEventListener("submit", () => {
    document.getElementById("steps-json").value = JSON.stringify(serialize());
  });

  // Chargement des steps existants
  if (existing.length) {
    existing.forEach((s) => addStep(s));
  } else {
    addStep();
  }

  bindChainButtons();
}

// Formulaire cible : modeles de connecteur pre-remplis
const CONNECTOR_PRESETS = {
  openai: {
    connector: "openai",
    base_url: "http://localhost:11434/v1",
    api_key: "",
    model: "llama3",
    system_prompt: "",
    temperature: 0.7,
  },
  anthropic: {
    connector: "anthropic",
    api_key: "sk-ant-...",
    model: "claude-3-haiku-20240307",
    max_tokens: 1024,
    system_prompt: "",
  },
  htb_chat: {
    connector: "htb",
    url: "http://CIBLE:PORT/api/messages/send",
    prompt_field: "content",
    poll_url: "http://CIBLE:PORT/api/messages",
    poll_retries: 8,
    poll_delay_ms: 1000,
    throttle: [5, 10],
  },
  htb_simple: {
    connector: "htb",
    url: "http://CIBLE:PORT/api/chat",
    method: "POST",
    headers: { Authorization: "Bearer TOKEN" },
    prompt_field: "prompt",
    response_path: "$.response",
    throttle: [5, 10],
  },
  raw_http: {
    connector: "raw_http",
    url: "http://CIBLE:PORT/ask",
    method: "POST",
    body_type: "json",
    body_template: '{"q": "{PROMPT}"}',
    response_path: "$.answer",
    throttle: [5, 10],
  },
};

function initTargetForm() {
  const select = document.getElementById("connector-preset");
  const apply = document.getElementById("apply-preset");
  const textarea = document.getElementById("auth_config");
  if (!select || !apply || !textarea) return;

  apply.addEventListener("click", () => {
    const key = select.value;
    if (!key || !CONNECTOR_PRESETS[key]) return;
    // Avertit avant d'ecraser un contenu existant
    if (textarea.value.trim() && !confirm(tr("js_confirm_replace_authconfig"))) {
      return;
    }
    textarea.value = JSON.stringify(CONNECTOR_PRESETS[key], null, 2);
  });
}

// Page diff : envoi d'un meme prompt a deux cibles
function initDiffPage() {
  const panel = document.getElementById("diff-panel");
  if (!panel) return;
  const runUrl = panel.dataset.runUrl;
  const phUrlBase = panel.dataset.phUrl;
  const select = document.getElementById("payload-select");
  const freeWrap = document.getElementById("free-prompt-wrap");
  const phWrap = document.getElementById("placeholders-wrap");
  const phFields = document.getElementById("placeholders-fields");

  select.addEventListener("change", async () => {
    const pid = select.value;
    if (!pid) {
      freeWrap.classList.remove("hidden");
      phWrap.classList.add("hidden");
      phFields.innerHTML = "";
      return;
    }
    freeWrap.classList.add("hidden");
    const data = await (await fetch(phUrlBase.replace("/0/", "/" + pid + "/"))).json();
    phFields.innerHTML = "";
    (data.placeholders || []).forEach((key) => {
      const div = document.createElement("div");
      const label = document.createElement("label");
      label.textContent = key;
      const input = document.createElement("input");
      input.type = "text";
      input.dataset.key = key;
      input.className = "ph-input";
      div.appendChild(label);
      div.appendChild(input);
      phFields.appendChild(div);
    });
    phWrap.classList.remove("hidden");
  });

  document.getElementById("compare-btn").addEventListener("click", async () => {
    const status = document.getElementById("diff-status");
    status.textContent = tr("js_sending");
    const values = {};
    phFields.querySelectorAll(".ph-input").forEach((el) => { values[el.dataset.key] = el.value; });
    const body = {
      target_a: document.getElementById("target-a").value,
      target_b: document.getElementById("target-b").value,
      placeholders: values,
    };
    if (select.value) body.payload_id = select.value;
    else body.free_prompt = document.getElementById("free-prompt").value;
    try {
      const data = await postJson(runUrl, body);
      document.getElementById("diff-results").classList.remove("hidden");
      document.getElementById("res-a-label").textContent = data.a.target || "A";
      document.getElementById("res-b-label").textContent = data.b.target || "B";
      document.getElementById("res-a").textContent = fmtDiff(data.a.result);
      document.getElementById("res-b").textContent = fmtDiff(data.b.result);
      status.textContent = "";
    } catch (e) {
      status.textContent = tr("js_error") + ": " + e;
    }
  });

  function fmtDiff(r) {
    if (!r) return "";
    if (r.error) return "[" + tr("js_error") + "] " + r.error;
    return (r.text || "") + "\n\n---\n" + tr("js_status") + ": " + (r.status_code || "-") +
      " | " + tr("js_duration") + ": " + (r.duration_ms || "-") + " ms";
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
function escapeAttr(str) {
  return String(str).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
