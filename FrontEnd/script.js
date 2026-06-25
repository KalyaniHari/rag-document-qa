const API_URL = "http://127.0.0.1:8000/chat";

const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

let history = [];

function renderMarkdown(content) {
  const html = marked.parse(content, { breaks: true });
  return DOMPurify.sanitize(html);
}

function addMessage(role, content) {
  const messageEl = document.createElement("div");
  messageEl.className = `message ${role}`;

  const label = document.createElement("span");
  label.className = "message-label";
  label.textContent = role === "user" ? "You" : "Assistant";

  const text = document.createElement("div");
  text.className = "message-content";

  if (role === "assistant") {
    text.innerHTML = renderMarkdown(content);
  } else {
    text.textContent = content;
  }

  messageEl.appendChild(label);
  messageEl.appendChild(text);
  chatMessages.appendChild(messageEl);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
  const userMessage = messageInput.value.trim();

  if (!userMessage) return;

  addMessage("user", userMessage);
  messageInput.value = "";

  messageInput.disabled = true;
  sendButton.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
        history: history,
      }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    const assistantReply = data.reply || "No response received.";

    addMessage("assistant", assistantReply);

    history.push({
      role: "user",
      content: userMessage,
    });

    history.push({
      role: "assistant",
      content: assistantReply,
    });
  } catch (error) {
    addMessage("assistant", `Error: Request failed. ${error.message}`);
  } finally {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
  }
}

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});