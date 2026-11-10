(function installHistoryPolicy(root, factory) {
  "use strict";

  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.PipHistory = api;
})(typeof globalThis === "object" ? globalThis : this, () => {
  "use strict";

  const DEFAULT_MAX_MESSAGES = 38;
  const DEFAULT_MAX_CONTENT_BYTES = 56 * 1024;

  function utf8Bytes(value) {
    return new TextEncoder().encode(value).byteLength;
  }

  /**
   * Return the newest contiguous user/assistant turns that fit both limits.
   * Incomplete, malformed, and non-chat messages are excluded. The input is
   * never mutated, and a turn is never split or truncated to make it fit.
   */
  function boundedCompleteHistory(
    history,
    maxMessages = DEFAULT_MAX_MESSAGES,
    maxContentBytes = DEFAULT_MAX_CONTENT_BYTES,
  ) {
    if (!Array.isArray(history) || maxMessages < 2 || maxContentBytes < 0) return [];

    const completeTurns = [];
    let pendingUser = null;

    for (const message of history) {
      if (!message || typeof message.content !== "string") continue;

      if (message.role === "user") {
        pendingUser = { role: "user", content: message.content };
      } else if (message.role === "assistant" && pendingUser) {
        completeTurns.push([
          pendingUser,
          { role: "assistant", content: message.content },
        ]);
        pendingUser = null;
      }
    }

    const selectedTurns = [];
    let selectedMessages = 0;
    let selectedBytes = 0;

    for (let index = completeTurns.length - 1; index >= 0; index -= 1) {
      const turn = completeTurns[index];
      const turnBytes = utf8Bytes(turn[0].content) + utf8Bytes(turn[1].content);
      if (selectedMessages + 2 > maxMessages || selectedBytes + turnBytes > maxContentBytes) break;

      selectedTurns.unshift(turn);
      selectedMessages += 2;
      selectedBytes += turnBytes;
    }

    return selectedTurns.flat();
  }

  return Object.freeze({
    boundedCompleteHistory,
    DEFAULT_MAX_MESSAGES,
    DEFAULT_MAX_CONTENT_BYTES,
  });
});
