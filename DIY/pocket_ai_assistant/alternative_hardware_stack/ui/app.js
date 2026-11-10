(() => {
  "use strict";

  const STORAGE_KEY = "pip-pocket-ui-settings-v1";
  const DEFAULT_SETTINGS = Object.freeze({
    mode: "demo",
    endpoint: "/api/chat",
    speakReplies: true,
  });

  const stateCopy = {
    idle: "Ready when you are",
    listening: "I’m listening…",
    thinking: "Thinking it through…",
    speaking: "Here’s what I found",
    error: "Something needs attention",
  };

  const els = {
    device: document.querySelector(".device"),
    conversation: document.querySelector("#conversation"),
    suggestions: document.querySelector("#suggestions"),
    form: document.querySelector("#composer-form"),
    input: document.querySelector("#composer-input"),
    micButton: document.querySelector("#mic-button"),
    sendButton: document.querySelector("#send-button"),
    clearButton: document.querySelector("#clear-button"),
    stateLabel: document.querySelector("#state-label"),
    connectionLabel: document.querySelector("#connection-label"),
    connectionDot: document.querySelector("#connection-dot"),
    settingsButton: document.querySelector("#settings-button"),
    settingsDialog: document.querySelector("#settings-dialog"),
    settingsForm: document.querySelector("#settings-form"),
    modeSelect: document.querySelector("#mode-select"),
    endpointInput: document.querySelector("#endpoint-input"),
    tokenInput: document.querySelector("#token-input"),
    speechToggle: document.querySelector("#speech-toggle"),
    testButton: document.querySelector("#test-button"),
    testResult: document.querySelector("#test-result"),
    template: document.querySelector("#message-template"),
    toast: document.querySelector("#toast"),
    announcement: document.querySelector("#announcement"),
    hint: document.querySelector("#composer-hint"),
  };

  let settings = loadSettings();
  let accessToken = "";
  let conversation = [];
  let currentRequest = null;
  let recognition = null;
  let isListening = false;
  let speechFinalText = "";
  let toastTimer = null;

  function loadSettings() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (!saved || typeof saved !== "object") return { ...DEFAULT_SETTINGS };
      return {
        mode: saved.mode === "server" ? "server" : "demo",
        endpoint: typeof saved.endpoint === "string" && saved.endpoint.trim()
          ? saved.endpoint.trim()
          : DEFAULT_SETTINGS.endpoint,
        speakReplies: saved.speakReplies !== false,
      };
    } catch {
      return { ...DEFAULT_SETTINGS };
    }
  }

  function saveSettings() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      // Private browsing can deny storage. The current session still works.
    }
  }

  function setState(nextState, customLabel = "") {
    els.device.dataset.state = nextState;
    els.stateLabel.textContent = customLabel || stateCopy[nextState] || stateCopy.idle;
  }

  function setConnectionDisplay(status = "neutral") {
    els.connectionDot.classList.remove("is-online", "is-offline");

    if (settings.mode === "demo") {
      els.connectionLabel.textContent = "Demo";
      return;
    }

    els.connectionLabel.textContent = status === "online" ? "Local · online" : "Local server";
    if (status === "online") els.connectionDot.classList.add("is-online");
    if (status === "offline") els.connectionDot.classList.add("is-offline");
  }

  function scrollConversation() {
    requestAnimationFrame(() => {
      els.conversation.scrollTop = els.conversation.scrollHeight;
    });
  }

  function resizeComposer() {
    els.input.style.height = "auto";
    els.input.style.height = `${Math.min(els.input.scrollHeight, 108)}px`;
    updateSendButton();
  }

  function updateSendButton() {
    const busy = Boolean(currentRequest);
    els.sendButton.classList.toggle("is-busy", busy);
    els.sendButton.disabled = !busy && !els.input.value.trim();
    els.sendButton.setAttribute("aria-label", busy ? "Stop response" : "Send message");
  }

  function timeLabel() {
    return new Intl.DateTimeFormat([], { hour: "numeric", minute: "2-digit" }).format(new Date());
  }

  function addMessage(role, text, options = {}) {
    const node = els.template.content.firstElementChild.cloneNode(true);
    const bubble = node.querySelector("p");
    const avatar = node.querySelector(".message__avatar");
    const meta = node.querySelector("small");

    node.classList.add(`message--${role}`);
    if (options.error) node.classList.add("message--error");
    if (options.streaming) node.classList.add("is-streaming");
    avatar.textContent = role === "user" ? "You" : "P";
    avatar.setAttribute("aria-label", role === "user" ? "You" : "Pip");
    bubble.textContent = text;
    meta.textContent = options.meta || timeLabel();
    els.conversation.appendChild(node);
    scrollConversation();
    return { node, bubble, meta };
  }

  function showToast(message, duration = 3200) {
    clearTimeout(toastTimer);
    els.toast.textContent = message;
    els.toast.hidden = false;
    toastTimer = setTimeout(() => {
      els.toast.hidden = true;
    }, duration);
  }

  function announce(message) {
    els.announcement.textContent = "";
    requestAnimationFrame(() => {
      els.announcement.textContent = message;
    });
  }

  function setBusy(isBusy) {
    if (!isBusy) currentRequest = null;
    els.micButton.disabled = isBusy || !recognition;
    els.input.readOnly = isBusy;
    els.hint.textContent = isBusy
      ? "Tap the square to stop this response"
      : "Enter to send · Shift + Enter for a new line";
    updateSendButton();
  }

  function getServerFields() {
    return document.querySelectorAll(".server-field");
  }

  function syncSettingsForm() {
    els.modeSelect.value = settings.mode;
    els.endpointInput.value = settings.endpoint;
    els.tokenInput.value = accessToken;
    els.speechToggle.checked = settings.speakReplies;
    updateSettingsVisibility();
  }

  function updateSettingsVisibility() {
    const disabled = els.modeSelect.value !== "server";
    for (const field of getServerFields()) {
      field.classList.toggle("is-disabled", disabled);
    }
  }

  function normalizeEndpoint(value) {
    const trimmed = value.trim();
    if (!trimmed) return DEFAULT_SETTINGS.endpoint;
    return trimmed.replace(/\/$/, "");
  }

  function healthEndpoint(chatEndpoint) {
    try {
      const url = new URL(chatEndpoint, window.location.href);
      url.pathname = url.pathname.replace(/\/api\/chat\/?$/, "/api/health");
      if (!url.pathname.endsWith("/api/health")) {
        url.pathname = `${url.pathname.replace(/\/$/, "")}/health`;
      }
      url.search = "";
      url.hash = "";
      return url.toString();
    } catch {
      return "/api/health";
    }
  }

  async function testConnection(endpoint = els.endpointInput.value) {
    const oldText = els.testButton.textContent;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);
    els.testButton.disabled = true;
    els.testButton.textContent = "Checking…";
    els.testResult.className = "";
    els.testResult.textContent = "";

    try {
      const response = await fetch(healthEndpoint(normalizeEndpoint(endpoint)), {
        signal: controller.signal,
        headers: { Accept: "application/json" },
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      let detail = "Gateway reachable";
      try {
        const health = await response.json();
        const backend = health.backend || health.model || health.status;
        if (backend && backend !== "ok") detail = `Gateway reachable · ${backend}`;
      } catch {
        // A successful plain-text health response is also valid.
      }
      els.testResult.textContent = detail;
      els.testResult.className = "is-good";
      if (settings.mode === "server") setConnectionDisplay("online");
      return true;
    } catch (error) {
      const suffix = error.name === "AbortError" ? "timed out" : error.message;
      els.testResult.textContent = `Gateway not reachable (${suffix})`;
      els.testResult.className = "is-bad";
      if (settings.mode === "server") setConnectionDisplay("offline");
      return false;
    } finally {
      clearTimeout(timeout);
      els.testButton.disabled = false;
      els.testButton.textContent = oldText;
    }
  }

  function stopSpeaking() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  }

  function speak(text) {
    if (!settings.speakReplies || !("speechSynthesis" in window) || !text.trim()) {
      setState("idle");
      return;
    }

    stopSpeaking();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.03;
    utterance.pitch = 1.08;
    utterance.onstart = () => setState("speaking", "Reading that aloud…");
    utterance.onend = () => setState("idle");
    utterance.onerror = () => setState("idle");
    window.speechSynthesis.speak(utterance);
  }

  function abortCurrentResponse(discard = false) {
    if (!currentRequest) return;
    currentRequest.discard = discard;
    currentRequest.abort();
    stopSpeaking();
  }

  function parseEventPayload(rawPayload) {
    const data = rawPayload.trim();
    if (!data || data === "[DONE]") return { done: data === "[DONE]", token: "" };

    let parsed;
    try {
      parsed = JSON.parse(data);
    } catch {
      return { done: false, token: rawPayload };
    }

    if (parsed.error) {
      const detail = typeof parsed.error === "string"
        ? parsed.error
        : parsed.error.message || "The local model returned an error.";
      throw new Error(detail);
    }

    const choice = parsed.choices?.[0];
    const token = choice?.delta?.content
      ?? choice?.message?.content
      ?? choice?.text
      ?? parsed.token
      ?? (typeof parsed.delta === "string" ? parsed.delta : undefined)
      ?? parsed.message?.content
      ?? parsed.content
      ?? parsed.response
      ?? "";
    return { done: Boolean(parsed.done), token: String(token) };
  }

  async function streamServerReply(message, history, signal, onToken) {
    const boundedHistory = window.PipHistory.boundedCompleteHistory(history);
    const payload = {
      message,
      history: boundedHistory,
    };
    const headers = {
      Accept: "text/event-stream, application/x-ndjson, application/json",
      "Content-Type": "application/json",
    };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

    const response = await fetch(settings.endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      const rawError = await response.text();
      let detail = rawError.slice(0, 180);
      try {
        const errorBody = JSON.parse(rawError);
        detail = errorBody.detail || errorBody.error?.message || errorBody.error || detail;
      } catch {
        // Keep the bounded plain-text response as the detail.
      }
      throw new Error(detail || `Server returned HTTP ${response.status}.`);
    }

    const contentType = (response.headers.get("content-type") || "").toLowerCase();
    if (contentType.includes("application/json")) {
      const result = parseEventPayload(JSON.stringify(await response.json()));
      if (result.token) onToken(result.token);
      return;
    }

    if (!response.body) throw new Error("This browser cannot read the streaming response.");

    const structured = contentType.includes("text/event-stream")
      || contentType.includes("ndjson")
      || contentType.includes("jsonl");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    const consumeLine = (line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(":")) return false;
      if (trimmed.startsWith("event:") || trimmed.startsWith("id:") || trimmed.startsWith("retry:")) return false;
      const value = trimmed.startsWith("data:") ? trimmed.slice(5).trimStart() : line;
      const parsed = parseEventPayload(value);
      if (parsed.token) onToken(parsed.token);
      return parsed.done;
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });

      if (!structured) {
        onToken(chunk);
        continue;
      }

      buffer += chunk;
      const lines = buffer.split(/\r?\n/);
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (consumeLine(line)) return;
      }
    }

    buffer += decoder.decode();
    if (structured && buffer.trim()) consumeLine(buffer);
  }

  function demoAnswer(message) {
    const lower = message.toLowerCase();
    if (/\b(hello|hi|hey)\b/.test(lower)) {
      return "Hi there! I’m awake, cheerful, and running entirely in your browser right now. Switch me to Local server when your model is ready.";
    }
    if (lower.includes("how do you work") || lower.includes("local ai") || lower.includes("local model")) {
      return "Think of me as two little teammates. This screen gathers your words and shows the answer. Your local server does the heavy thinking, then streams the answer back a few words at a time. In demo mode, I use a tiny built-in reply instead—no network needed.";
    }
    if (lower.includes("joke")) {
      return "Why did the tiny robot bring a pencil? It wanted to draw less current! 🤖";
    }
    if (lower.includes("plan") || lower.includes("today")) {
      return "Here’s a one-minute plan: take one slow breath, choose the smallest useful next step, work on it for forty seconds, then write down what changed. Tiny loops make sturdy robots.";
    }
    if (lower.includes("hardware")) {
      return "For a friendly local assistant, the main pieces are a small controller, microphone, speaker amplifier, display, buttons, and a local model server on your network. Test each piece alone before joining the whole stack.";
    }
    return `I heard: “${message}”. I’m using my built-in demo brain, so this reply is only a UI preview. Choose Local model server in Brain settings to get a real model-generated answer.`;
  }

  function abortableDelay(milliseconds, signal) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, milliseconds);
      signal.addEventListener("abort", () => {
        clearTimeout(timer);
        reject(new DOMException("Stopped", "AbortError"));
      }, { once: true });
    });
  }

  async function streamDemoReply(message, signal, onToken) {
    await abortableDelay(420, signal);
    const pieces = demoAnswer(message).match(/\S+\s*/g) || [];
    for (const piece of pieces) {
      await abortableDelay(26 + Math.random() * 34, signal);
      onToken(piece);
    }
  }

  async function sendMessage(rawMessage) {
    const message = rawMessage.trim();
    if (!message || currentRequest) return;

    stopSpeaking();
    if (isListening) recognition?.stop();
    els.suggestions.hidden = true;
    els.input.value = "";
    resizeComposer();

    const priorHistory = conversation.slice();
    const userTurn = { role: "user", content: message };
    conversation.push(userTurn);
    addMessage("user", message);
    const reply = addMessage("assistant", "", {
      streaming: true,
      meta: settings.mode === "demo" ? "Pip’s demo brain" : "Your local model",
    });

    const controller = new AbortController();
    currentRequest = controller;
    setBusy(true);
    setState("thinking");
    let answer = "";

    const onToken = (token) => {
      if (!token) return;
      if (!answer) setState("speaking", "Writing a reply…");
      answer += token;
      reply.bubble.textContent = answer;
      scrollConversation();
    };

    try {
      if (settings.mode === "demo") {
        await streamDemoReply(message, controller.signal, onToken);
      } else {
        await streamServerReply(message, priorHistory, controller.signal, onToken);
        setConnectionDisplay("online");
      }

      if (!answer.trim()) throw new Error("The model finished without returning any text.");
      conversation.push({ role: "assistant", content: answer });
      reply.node.classList.remove("is-streaming");
      reply.meta.textContent = timeLabel();
      setBusy(false);
      announce("Pip finished replying.");
      speak(answer);
    } catch (error) {
      const wasStopped = error.name === "AbortError";
      reply.node.classList.remove("is-streaming");

      if (wasStopped && controller.discard) {
        reply.node.remove();
        setBusy(false);
        return;
      }

      if (wasStopped) {
        if (answer.trim()) {
          conversation.push({ role: "assistant", content: answer });
          reply.meta.textContent = "Stopped";
        } else {
          conversation = conversation.filter((turn) => turn !== userTurn);
          reply.node.remove();
        }
        setState("idle", "Response stopped");
        showToast("Response stopped");
      } else {
        conversation = conversation.filter((turn) => turn !== userTurn);
        reply.node.classList.add("message--error");
        reply.bubble.textContent = settings.mode === "server"
          ? `I couldn’t reach the local model. ${error.message}`
          : `The demo hit a snag. ${error.message}`;
        reply.meta.textContent = "Not added to chat history";
        setState("error");
        if (settings.mode === "server") setConnectionDisplay("offline");
        announce("The reply failed. Open Brain settings to check the connection.");
      }

      setBusy(false);
    }
  }

  function clearConversation() {
    abortCurrentResponse(true);
    stopSpeaking();
    speechFinalText = "";
    if (isListening) recognition?.abort();
    conversation = [];
    els.conversation.querySelectorAll(".message:not(.message--welcome)").forEach((node) => node.remove());
    els.suggestions.hidden = false;
    els.input.value = "";
    resizeComposer();
    setState("idle");
    showToast("Fresh conversation started");
    els.input.focus();
  }

  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      els.micButton.disabled = true;
      els.micButton.title = "Speech recognition is not available in this browser";
      return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = navigator.language || "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
      isListening = true;
      speechFinalText = "";
      els.micButton.setAttribute("aria-pressed", "true");
      setState("listening");
      els.hint.textContent = "Speak naturally · tap the mic when you’re done";
    };

    recognition.onresult = (event) => {
      let interim = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const transcript = event.results[index][0].transcript;
        if (event.results[index].isFinal) speechFinalText += transcript;
        else interim += transcript;
      }
      els.input.value = `${speechFinalText}${interim}`.trimStart();
      resizeComposer();
    };

    recognition.onerror = (event) => {
      if (event.error !== "aborted" && event.error !== "no-speech") {
        const explanations = {
          "not-allowed": "Microphone access was blocked. Allow it in your browser settings.",
          network: "Speech recognition could not connect. Typed chat still works.",
          "audio-capture": "No microphone was found.",
        };
        showToast(explanations[event.error] || `Microphone error: ${event.error}`);
        setState("error", "Microphone needs attention");
      }
    };

    recognition.onend = () => {
      isListening = false;
      els.micButton.setAttribute("aria-pressed", "false");
      els.hint.textContent = "Enter to send · Shift + Enter for a new line";
      if (speechFinalText.trim()) {
        const finalText = speechFinalText;
        speechFinalText = "";
        setState("idle");
        sendMessage(finalText);
      } else if (els.device.dataset.state === "listening") {
        setState("idle");
      }
    };
  }

  function toggleListening() {
    if (!recognition || currentRequest) return;
    stopSpeaking();
    if (isListening) recognition.stop();
    else {
      try {
        recognition.start();
      } catch {
        showToast("The microphone is already starting. Try again in a moment.");
      }
    }
  }

  els.form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (currentRequest) abortCurrentResponse();
    else sendMessage(els.input.value);
  });

  els.input.addEventListener("input", resizeComposer);
  els.input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      if (!currentRequest) els.form.requestSubmit();
    }
  });

  els.micButton.addEventListener("click", toggleListening);
  els.clearButton.addEventListener("click", clearConversation);

  els.suggestions.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-prompt]");
    if (button) sendMessage(button.dataset.prompt);
  });

  els.settingsButton.addEventListener("click", () => {
    syncSettingsForm();
    els.testResult.textContent = "";
    els.testResult.className = "";
    els.settingsDialog.showModal();
  });

  els.modeSelect.addEventListener("change", updateSettingsVisibility);
  els.testButton.addEventListener("click", () => testConnection());

  els.settingsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    settings = {
      mode: els.modeSelect.value === "server" ? "server" : "demo",
      endpoint: normalizeEndpoint(els.endpointInput.value),
      speakReplies: els.speechToggle.checked,
    };
    accessToken = els.tokenInput.value.trim();
    saveSettings();
    setConnectionDisplay();
    els.settingsDialog.close();
    showToast(settings.mode === "demo" ? "Demo brain selected" : "Local model server selected");
    if (settings.mode === "server") testConnection(settings.endpoint);
  });

  for (const closeButton of document.querySelectorAll(".settings-close")) {
    closeButton.addEventListener("click", () => els.settingsDialog.close());
  }

  els.settingsDialog.addEventListener("click", (event) => {
    if (event.target === els.settingsDialog) els.settingsDialog.close();
  });

  window.addEventListener("beforeunload", () => {
    abortCurrentResponse(true);
    stopSpeaking();
  });

  setupSpeechRecognition();
  setState("idle");
  setConnectionDisplay();
  syncSettingsForm();
  resizeComposer();
  if (settings.mode === "server") testConnection(settings.endpoint);
})();
