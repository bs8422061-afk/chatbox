const chatBox   = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn   = document.getElementById("send-btn");

// ── Typing indicator ──────────────────────────────────────────
function showTyping() {
    const t = document.createElement("div");
    t.id = "typing";
    t.className = "typing-indicator";
    t.innerHTML = `<div class="typing-dot"></div>
                   <div class="typing-dot"></div>
                   <div class="typing-dot"></div>`;
    chatBox.appendChild(t);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
}

// ── Add message bubble ────────────────────────────────────────
function addMessage(message, type) {
    const welcome = chatBox.querySelector(".welcome-msg");
    if (welcome) welcome.remove();

    const div = document.createElement("div");
    div.classList.add("message", type === "user-message" ? "user" : "bot");

    const label = document.createElement("div");
    label.className = "msg-label";
    label.textContent = type === "user-message" ? "You" : "CuriBot.ai";

    const text = document.createElement("div");
    text.textContent = message;

    div.appendChild(label);
    div.appendChild(text);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ── Send to Flask ─────────────────────────────────────────────
async function sendMessage() {
    const input = userInput.value.trim();
    if (!input) return;

    addMessage(input, "user-message");
    userInput.value = "";
    sendBtn.disabled = true;
    showTyping();

    try {
        const res  = await fetch("/ask", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ message: input })
        });
        const data = await res.json();
        hideTyping();
        addMessage(data.response, "bot-message");
    } catch {
        hideTyping();
        addMessage("⚠️ Could not reach the server. Is Flask running?", "bot-message");
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// ── Clear chat ────────────────────────────────────────────────
function clearChat() {
    chatBox.innerHTML = `
        <div class="welcome-msg">
            <div class="welcome-icon">🤖</div>
            <h3>Chat cleared!</h3>
            <p>Ask me anything about Python!</p>
            <div class="welcome-tags">
                <span class="wtag py">🐍 Python</span>
            </div>
        </div>`;
}

// ── Python-only chip sets ─────────────────────────────────────
const CHIPS = {
    all: [
        ["What is Python?",  "what is python","python intro", "python overview", "python basics","python for beginners"],
        ["Python loops",     "python loops", "python for loop", "python while loop", "python loop examples"],
        ["Python functions", "python functions"],
        ["Python classes",   "python classes"],
        ["Big O Notation",   "what is big o"],
    ],
    python: [
        ["What is Python?",  "what is python"],
        ["Data types",       "python data types"],
        ["Loops",            "python loops"],
        ["Functions",        "python functions"],
        ["Classes",          "python classes"],
        ["Decorators",       "python decorators"],
        ["Async/Await",      "python async"],
        ["Generators",       "python generators"],
        ["Memory mgmt",      "python memory management"],
        ["List methods",     "python list methods"],
        ["Dict methods",     "python dict methods"],
        ["File handling",    "python file handling"],
        ["Testing",          "python testing"],
        ["GIL",              "python gil"],
    ],
};

function filterTopic(topic, el) {
    document.querySelectorAll(".topic-tab")
            .forEach(t => t.classList.remove("active"));
    el.classList.add("active");

    // map non-python tabs to python chips
    const key = (topic === "python") ? "python" : "all";

    const area = document.getElementById("suggestion-area");
    area.innerHTML = CHIPS[key]
        .map(([label, q]) =>
            `<span class="suggestion-chip" onclick="ask('${q}')">${label}</span>`)
        .join("");
}

// ── Suggestion shortcut ───────────────────────────────────────
function ask(msg) {
    userInput.value = msg;
    sendMessage();
}

// ── Listeners ─────────────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});