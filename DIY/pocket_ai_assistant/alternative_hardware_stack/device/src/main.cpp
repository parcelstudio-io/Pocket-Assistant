#include <Arduino.h>
#include <ArduinoJson.h>
#include <M5Unified.h>
#include <WiFi.h>
#include <WiFiClient.h>

#if __has_include("device_config.h")
#include "device_config.h"
#endif

#ifndef POCKET_WIFI_SSID
#define POCKET_WIFI_SSID ""
#endif

#ifndef POCKET_WIFI_PASSWORD
#define POCKET_WIFI_PASSWORD ""
#endif

#ifndef POCKET_SERVER_URL
#define POCKET_SERVER_URL ""
#endif

#ifndef POCKET_DEVICE_TOKEN
#define POCKET_DEVICE_TOKEN ""
#endif

#ifndef POCKET_DEMO_PROMPT
#define POCKET_DEMO_PROMPT \
  "Introduce yourself as a cheerful pocket assistant in one short sentence."
#endif

namespace {

constexpr uint32_t kWifiConnectTimeoutMs = 12000;
// The host gateway permits a backend call to wait for 120 seconds. Give that
// wait ten seconds of transport margin, and measure inactivity rather than the
// whole turn so a long but healthy stream is never cut off.
constexpr uint32_t kServerIdleTimeoutMs = 130000;
constexpr size_t kMaxReplyBytes = 640;
constexpr size_t kMaxHttpLineBytes = 4096;

constexpr int16_t kActionX = 68;
constexpr int16_t kActionY = 202;
constexpr int16_t kActionW = 184;
constexpr int16_t kActionH = 30;

// Hand-picked RGB565 colors. Keeping these local avoids a sprite or asset
// dependency and makes the UI easy to redraw in a native device implementation.
constexpr uint16_t kInk = 0x29AA;
constexpr uint16_t kPaper = 0xFF9D;
constexpr uint16_t kCard = 0xFFFF;
constexpr uint16_t kMint = 0x8F76;
constexpr uint16_t kMintDark = 0x352D;
constexpr uint16_t kPeach = 0xFCAE;
constexpr uint16_t kLavender = 0xC5BF;
constexpr uint16_t kBlue = 0x64DF;
constexpr uint16_t kRose = 0xFB4D;
constexpr uint16_t kMuted = 0x8C71;

enum class UiState : uint8_t {
  kBooting,
  kOffline,
  kIdle,
  kListening,
  kThinking,
  kSpeaking,
  kError,
};

enum class AudioOwner : uint8_t {
  kNone,
  kMicrophone,
  kSpeaker,
};

UiState gState = UiState::kBooting;
AudioOwner gAudioOwner = AudioOwner::kNone;
String gReply;
String gDetail = "Starting the tiny companion...";
bool gTouchWasDown = false;
bool gDemoTurnPending = false;
uint32_t gDemoDeadlineMs = 0;
uint32_t gSpeakingDeadlineMs = 0;
uint32_t gLastFrameMs = 0;

bool elapsed(uint32_t now, uint32_t deadline) {
  return static_cast<int32_t>(now - deadline) >= 0;
}

bool idleExpired(uint32_t now, uint32_t lastActivity, uint32_t timeout) {
  // Unsigned subtraction stays correct when millis() rolls over.
  return static_cast<uint32_t>(now - lastActivity) >= timeout;
}

const char* stateLabel(UiState state) {
  switch (state) {
    case UiState::kBooting:
      return "WAKING UP";
    case UiState::kOffline:
      return "FACE DEMO";
    case UiState::kIdle:
      return "READY";
    case UiState::kListening:
      return "LISTENING";
    case UiState::kThinking:
      return "THINKING";
    case UiState::kSpeaking:
      return "SPEAKING";
    case UiState::kError:
      return "NEEDS HELP";
  }
  return "UNKNOWN";
}

uint16_t accentFor(UiState state) {
  switch (state) {
    case UiState::kListening:
      return kBlue;
    case UiState::kThinking:
      return kLavender;
    case UiState::kSpeaking:
      return kPeach;
    case UiState::kError:
      return kRose;
    default:
      return kMint;
  }
}

String compactLine(const String& source, size_t maxBytes = 48) {
  String line = source;
  line.replace('\n', ' ');
  line.replace('\r', ' ');
  if (line.length() <= maxBytes) {
    return line;
  }
  line.remove(maxBytes - 3);
  line += "...";
  return line;
}

void setState(UiState state, const String& detail = String()) {
  gState = state;
  if (!detail.isEmpty()) {
    gDetail = detail;
  }
  gLastFrameMs = 0;
}

void drawEye(int16_t x, int16_t y, bool blink, int16_t pupilOffset) {
  if (blink) {
    M5.Display.fillRoundRect(x - 24, y - 3, 48, 7, 4, kInk);
    return;
  }

  M5.Display.fillRoundRect(x - 25, y - 22, 50, 44, 19, kCard);
  M5.Display.drawRoundRect(x - 25, y - 22, 50, 44, 19, kInk);
  M5.Display.fillCircle(x + pupilOffset, y + 2, 9, kInk);
  M5.Display.fillCircle(x + pupilOffset + 3, y - 2, 3, kCard);
}

void drawMouth(UiState state, int16_t centerX, int16_t centerY) {
  switch (state) {
    case UiState::kListening: {
      const int16_t radius = 8 + ((millis() / 180) % 3);
      M5.Display.fillCircle(centerX, centerY, radius, kInk);
      M5.Display.fillCircle(centerX, centerY - 2, radius - 4, kPeach);
      break;
    }
    case UiState::kThinking:
      M5.Display.fillCircle(centerX - 10, centerY, 3, kInk);
      M5.Display.fillCircle(centerX, centerY, 3, kInk);
      M5.Display.fillCircle(centerX + 10, centerY, 3, kInk);
      break;
    case UiState::kSpeaking: {
      const int16_t height = 8 + ((millis() / 120) % 4) * 3;
      M5.Display.fillRoundRect(centerX - 15, centerY - height / 2, 30, height,
                               7, kInk);
      break;
    }
    case UiState::kError:
      M5.Display.drawLine(centerX - 15, centerY + 5, centerX,
                          centerY - 3, kInk);
      M5.Display.drawLine(centerX, centerY - 3, centerX + 15,
                          centerY + 5, kInk);
      break;
    default:
      M5.Display.drawArc(centerX, centerY - 8, 22, 16, 18, 162, kInk);
      break;
  }
}

void drawListeningRings() {
  const int16_t pulse = static_cast<int16_t>((millis() / 100) % 8);
  M5.Display.drawCircle(35, 104, 8 + pulse, kBlue);
  M5.Display.drawCircle(285, 104, 8 + pulse, kBlue);
}

void renderUi(bool force = false) {
  const uint32_t now = millis();
  if (!force && now - gLastFrameMs < 55) {
    return;
  }
  gLastFrameMs = now;

  const uint16_t accent = accentFor(gState);
  const bool blink = (gState == UiState::kIdle || gState == UiState::kOffline) &&
                     (now % 4300 > 4170);
  int16_t pupilOffset = 0;
  if (gState == UiState::kThinking) {
    pupilOffset = ((now / 420) % 2 == 0) ? -7 : 7;
  }

  M5.Display.startWrite();
  M5.Display.fillScreen(kPaper);

  M5.Display.fillRoundRect(10, 7, 300, 25, 12, kInk);
  M5.Display.fillCircle(23, 19, 5,
                        WiFi.status() == WL_CONNECTED ? kMint : kMuted);
  M5.Display.setTextDatum(middle_center);
  M5.Display.setTextColor(kCard, kInk);
  M5.Display.setTextSize(1);
  M5.Display.drawString(stateLabel(gState), 160, 19);

  M5.Display.fillRoundRect(17, 39, 286, 122, 28, accent);
  M5.Display.drawRoundRect(17, 39, 286, 122, 28, kInk);
  M5.Display.fillRoundRect(38, 56, 244, 90, 32, kCard);

  drawEye(105, 91, blink, pupilOffset);
  drawEye(215, 91, blink, pupilOffset);
  drawMouth(gState, 160, 129);
  if (gState == UiState::kListening) {
    drawListeningRings();
  }

  const String preview = gReply.isEmpty() ? gDetail : gReply;
  M5.Display.setTextDatum(middle_center);
  M5.Display.setTextColor(kInk, kPaper);
  M5.Display.drawString(compactLine(preview), 160, 180);

  M5.Display.fillRoundRect(kActionX, kActionY, kActionW, kActionH, 14,
                           gState == UiState::kListening ? kInk : accent);
  M5.Display.drawRoundRect(kActionX, kActionY, kActionW, kActionH, 14, kInk);
  M5.Display.setTextColor(
      gState == UiState::kListening ? kCard : kInk,
      gState == UiState::kListening ? kInk : accent);
  const char* action = gState == UiState::kListening
                           ? "RELEASE TO SEND"
                           : (WiFi.status() == WL_CONNECTED ? "HOLD TO TALK"
                                                            : "TRY FACE DEMO");
  M5.Display.drawString(action, 160, kActionY + kActionH / 2);
  M5.Display.endWrite();
}

void releaseAudio() {
  if (M5.Mic.isEnabled()) {
    while (M5.Mic.isRecording()) {
      M5.delay(1);
    }
    M5.Mic.end();
  }
  if (M5.Speaker.isEnabled()) {
    M5.Speaker.stop();
    M5.Speaker.end();
  }
  gAudioOwner = AudioOwner::kNone;
}

bool claimMicrophone() {
  // M5Unified's CoreS3 example documents this path as half-duplex. Never
  // leave the speaker active while starting the ES7210 microphone path.
  if (M5.Speaker.isEnabled()) {
    M5.Speaker.stop();
    M5.Speaker.end();
  }
  if (!M5.Mic.isEnabled() && !M5.Mic.begin()) {
    gAudioOwner = AudioOwner::kNone;
    return false;
  }
  gAudioOwner = AudioOwner::kMicrophone;
  return true;
}

bool claimSpeaker() {
  // The reverse transition is equally deliberate: finish any outstanding
  // microphone DMA ownership before enabling the AW88298 speaker path.
  if (M5.Mic.isEnabled()) {
    while (M5.Mic.isRecording()) {
      M5.delay(1);
    }
    M5.Mic.end();
  }
  if (!M5.Speaker.isEnabled() && !M5.Speaker.begin()) {
    gAudioOwner = AudioOwner::kNone;
    return false;
  }
  M5.Speaker.setVolume(48);
  gAudioOwner = AudioOwner::kSpeaker;
  return true;
}

struct HttpTarget {
  String host;
  String path;
  uint16_t port = 80;
};

enum class LineReadResult : uint8_t {
  kLine,
  kClosed,
  kIdleTimeout,
  kTooLong,
};

bool parseHttpTarget(HttpTarget& target, String& error) {
  String url = POCKET_SERVER_URL;
  url.trim();
  constexpr const char* kScheme = "http://";
  if (!url.startsWith(kScheme)) {
    error = "Server URL must start with http://";
    return false;
  }
  if (url.indexOf('?') >= 0 || url.indexOf('#') >= 0 ||
      url.indexOf('\r') >= 0 || url.indexOf('\n') >= 0) {
    error = "Server URL cannot contain a query, fragment, or newline";
    return false;
  }

  const int authorityStart = strlen(kScheme);
  const int pathStart = url.indexOf('/', authorityStart);
  String authority = pathStart >= 0 ? url.substring(authorityStart, pathStart)
                                    : url.substring(authorityStart);
  if (authority.isEmpty() || authority.indexOf('@') >= 0) {
    error = "Server URL needs a host and cannot contain user info";
    return false;
  }

  const int colon = authority.lastIndexOf(':');
  if (colon >= 0) {
    // Bracketed IPv6 is deliberately out of scope for the private-LAN MVP.
    if (authority.indexOf(':') != colon) {
      error = "Use an IPv4 address or LAN hostname for the server";
      return false;
    }
    const String portText = authority.substring(colon + 1);
    if (portText.isEmpty()) {
      error = "Server URL has an empty port";
      return false;
    }
    for (size_t index = 0; index < portText.length(); ++index) {
      if (portText[index] < '0' || portText[index] > '9') {
        error = "Server URL port must be numeric";
        return false;
      }
    }
    const long parsedPort = portText.toInt();
    if (parsedPort < 1 || parsedPort > 65535) {
      error = "Server URL port is outside 1-65535";
      return false;
    }
    target.port = static_cast<uint16_t>(parsedPort);
    authority.remove(colon);
  }
  if (authority.isEmpty()) {
    error = "Server URL host is empty";
    return false;
  }

  target.host = authority;
  target.path = pathStart >= 0 ? url.substring(pathStart) : String();
  while (target.path.endsWith("/")) {
    target.path.remove(target.path.length() - 1);
  }
  target.path += "/api/chat";
  return true;
}

LineReadResult readHttpLine(WiFiClient& client, String& line,
                            uint32_t& lastActivity) {
  line = "";
  while (true) {
    while (client.available()) {
      const int value = client.read();
      if (value < 0) {
        break;
      }
      lastActivity = millis();
      const char character = static_cast<char>(value);
      if (character == '\n') {
        if (line.endsWith("\r")) {
          line.remove(line.length() - 1);
        }
        return LineReadResult::kLine;
      }
      if (line.length() >= kMaxHttpLineBytes) {
        return LineReadResult::kTooLong;
      }
      line += character;
    }

    if (!client.connected() && !client.available()) {
      return LineReadResult::kClosed;
    }
    if (idleExpired(millis(), lastActivity, kServerIdleTimeoutMs)) {
      return LineReadResult::kIdleTimeout;
    }
    renderUi();
    M5.delay(8);
  }
}

String lineReadError(LineReadResult result) {
  switch (result) {
    case LineReadResult::kClosed:
      return "Local server closed the connection";
    case LineReadResult::kIdleTimeout:
      return "Local server was idle for 130 seconds";
    case LineReadResult::kTooLong:
      return "Local server sent an oversized HTTP line";
    case LineReadResult::kLine:
      break;
  }
  return "Local server response failed";
}

bool requestAssistant(const String& prompt, String& reply, String& error) {
  HttpTarget target;
  if (!parseHttpTarget(target, error)) {
    return false;
  }
  const String token = POCKET_DEVICE_TOKEN;
  if (token.indexOf('\r') >= 0 || token.indexOf('\n') >= 0) {
    error = "Device token cannot contain a newline";
    return false;
  }

  JsonDocument request;
  request["message"] = prompt;
  request["history"].to<JsonArray>();
  request["max_tokens"] = 96;
  String body;
  serializeJson(request, body);

  WiFiClient client;
  // WiFiClient expresses this socket option in seconds. The explicit polling
  // watchdog below remains the source of truth and refreshes on every byte.
  client.setTimeout((kServerIdleTimeoutMs + 999) / 1000);
  if (!client.connect(target.host.c_str(), target.port, 5000)) {
    error = "Could not connect to the local server";
    return false;
  }

  String headers = String("POST ") + target.path + " HTTP/1.1\r\n" +
                   "Host: " + target.host + ":" + target.port + "\r\n" +
                   "Content-Type: application/json\r\n" +
                   "Accept: text/event-stream\r\n" +
                   "Connection: close\r\n";
  if (!token.isEmpty()) {
    headers += String("Authorization: Bearer ") + token + "\r\n";
  }
  headers += String("Content-Length: ") + body.length() + "\r\n\r\n";
  if (client.print(headers) != headers.length() ||
      client.print(body) != body.length()) {
    client.stop();
    error = "Could not send the request to the local server";
    return false;
  }

  uint32_t lastActivity = millis();
  String line;
  LineReadResult readResult = readHttpLine(client, line, lastActivity);
  if (readResult != LineReadResult::kLine) {
    client.stop();
    error = lineReadError(readResult);
    return false;
  }
  if (!line.startsWith("HTTP/1.")) {
    client.stop();
    error = "Local server sent an invalid HTTP status line";
    return false;
  }
  const int firstSpace = line.indexOf(' ');
  const int secondSpace = line.indexOf(' ', firstSpace + 1);
  const int statusEnd = secondSpace >= 0 ? secondSpace : line.length();
  const int status =
      firstSpace >= 0 ? line.substring(firstSpace + 1, statusEnd).toInt() : 0;
  if (status != 200) {
    client.stop();
    error = status > 0 ? String("Local server returned HTTP ") + status
                       : "Local server returned an invalid HTTP status";
    return false;
  }

  do {
    readResult = readHttpLine(client, line, lastActivity);
    if (readResult != LineReadResult::kLine) {
      client.stop();
      error = lineReadError(readResult);
      return false;
    }
  } while (!line.isEmpty());

  bool receivedDone = false;
  String streamError;
  reply = "";

  while (!receivedDone) {
    readResult = readHttpLine(client, line, lastActivity);
    if (readResult != LineReadResult::kLine) {
      error = lineReadError(readResult);
      break;
    }
    line.trim();
    if (!line.startsWith("data:")) {
      continue;
    }

    String data = line.substring(5);
    data.trim();
    if (data == "[DONE]") {
      receivedDone = true;
      break;
    }

    JsonDocument event;
    if (deserializeJson(event, data)) {
      continue;
    }
    const char* errorMessage = event["error"]["message"] | "";
    if (*errorMessage != '\0') {
      streamError = errorMessage;
      break;
    }
    const char* token = event["choices"][0]["delta"]["content"] | "";
    if (*token == '\0') {
      continue;
    }
    if (reply.length() < kMaxReplyBytes) {
      const size_t room = kMaxReplyBytes - reply.length();
      String chunk = token;
      if (chunk.length() > room) {
        chunk.remove(room);
      }
      reply += chunk;
      gReply = reply;
    }
    renderUi(true);
  }

  client.stop();
  if (!streamError.isEmpty()) {
    error = String("Local model stream failed: ") + streamError;
    return false;
  }
  if (!receivedDone) {
    if (error.isEmpty()) {
      error = "The local model stream ended before [DONE]";
    }
    return false;
  }
  if (reply.isEmpty()) {
    error = "The local model returned an empty reply";
    return false;
  }
  return true;
}

bool actionIsTouched() {
  const auto touches = M5.Touch.getCount();
  for (size_t index = 0; index < touches; ++index) {
    const auto point = M5.Touch.getDetail(index);
    if (point.x >= kActionX && point.x < kActionX + kActionW &&
        point.y >= kActionY && point.y < kActionY + kActionH) {
      return true;
    }
  }
  return false;
}

void startListeningGesture() {
  if (gState == UiState::kThinking || gState == UiState::kSpeaking ||
      gState == UiState::kBooting) {
    return;
  }
  gReply = "";
  if (!claimMicrophone()) {
    setState(UiState::kError, "The built-in microphone did not start");
    renderUi(true);
    return;
  }
  setState(UiState::kListening,
           "Mic reserved; audio upload is the next milestone");
  renderUi(true);
}

void startSpeakingPreview(const String& response) {
  if (!claimSpeaker()) {
    releaseAudio();
    gReply = "";
    setState(UiState::kError, "The built-in speaker did not start");
    renderUi(true);
    return;
  }
  gReply = response;
  setState(UiState::kSpeaking);
  M5.Speaker.tone(740, 90);
  gSpeakingDeadlineMs = millis() + 2600;
  renderUi(true);
}

void finishListeningGesture() {
  if (gState != UiState::kListening) {
    return;
  }

  if (M5.Mic.isEnabled()) {
    while (M5.Mic.isRecording()) {
      M5.delay(1);
    }
    M5.Mic.end();
  }
  gAudioOwner = AudioOwner::kNone;
  setState(UiState::kThinking, "Asking the model on your LAN...");
  renderUi(true);

  const bool networkConfigured = strlen(POCKET_WIFI_SSID) > 0 &&
                                 strlen(POCKET_SERVER_URL) > 0;
  if (!networkConfigured || WiFi.status() != WL_CONNECTED) {
    gDemoTurnPending = true;
    gDemoDeadlineMs = millis() + 900;
    gDetail = "Running the review-only face demo...";
    return;
  }

  String reply;
  String error;
  if (!requestAssistant(POCKET_DEMO_PROMPT, reply, error)) {
    releaseAudio();
    gReply = "";
    setState(UiState::kError, error);
    renderUi(true);
    return;
  }
  startSpeakingPreview(reply);
}

void connectWifiIfConfigured() {
  if (strlen(POCKET_WIFI_SSID) == 0 || strlen(POCKET_SERVER_URL) == 0) {
    setState(UiState::kOffline,
             "No secrets file: tap below to preview the face");
    return;
  }

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(POCKET_WIFI_SSID, POCKET_WIFI_PASSWORD);
  setState(UiState::kBooting, "Joining the private 2.4 GHz LAN...");

  const uint32_t deadline = millis() + kWifiConnectTimeoutMs;
  while (WiFi.status() != WL_CONNECTED && !elapsed(millis(), deadline)) {
    renderUi(true);
    M5.delay(120);
  }

  if (WiFi.status() == WL_CONNECTED) {
    setState(UiState::kIdle,
             String("LAN ready: ") + WiFi.localIP().toString());
    Serial.printf("CoreS3-SE LAN address: %s\n",
                  WiFi.localIP().toString().c_str());
  } else {
    WiFi.disconnect(true, false);
    setState(UiState::kError,
             "Wi-Fi timed out; check the 2.4 GHz credentials");
  }
}

}  // namespace

void setup() {
  auto config = M5.config();
  config.internal_mic = true;
  config.internal_spk = true;
  config.clear_display = true;
  M5.begin(config);

  Serial.begin(115200);
  M5.Display.setRotation(1);
  if (M5.Display.width() < M5.Display.height()) {
    M5.Display.setRotation(M5.Display.getRotation() ^ 1);
  }
  M5.Display.setBrightness(145);
  M5.Display.setTextFont(2);
  M5.Display.setTextWrap(false);

  // Begin from a known audio state. Every later owner transition passes through
  // claimMicrophone(), claimSpeaker(), or releaseAudio().
  releaseAudio();
  renderUi(true);
  connectWifiIfConfigured();
  renderUi(true);
}

void loop() {
  M5.update();
  const uint32_t now = millis();
  const bool touchDown = actionIsTouched();

  if (touchDown && !gTouchWasDown) {
    startListeningGesture();
  } else if (!touchDown && gTouchWasDown) {
    finishListeningGesture();
  }
  gTouchWasDown = touchDown;

  if (gDemoTurnPending && elapsed(now, gDemoDeadlineMs)) {
    gDemoTurnPending = false;
    startSpeakingPreview(
        "Hi! My face works; local speech is the next hardware milestone.");
  }

  if (gState == UiState::kSpeaking && elapsed(now, gSpeakingDeadlineMs)) {
    releaseAudio();
    gReply = "";
    const bool online = WiFi.status() == WL_CONNECTED;
    setState(online ? UiState::kIdle : UiState::kOffline,
             online ? "Ready for another local-model turn"
                    : "No secrets file: tap below to preview the face");
  }

  renderUi();
  M5.delay(8);
}
