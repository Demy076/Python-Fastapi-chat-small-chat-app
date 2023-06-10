(async () => {
  const me = await fetch("http://localhost:3000/me", {
    method: "GET",
    credentials: "include",
  }).then((res) => {
    console.log(res);
    if (!res.ok) {
      console.log("not logged in");
      location.href = "/login.html";
    }
    return res.json();
  });
  const messages = await fetch("http://localhost:3000", {
    credentials: "include",
  }).then((res) => res.json());
  const messages_box = document.querySelector("#messages-box");
  messages.messages.forEach((message) => {
    const messageElement = document.createElement("div");
    messageElement.innerText = `${message.username}: ${message.message}`;
    messages_box.appendChild(messageElement);
  });
  const socket = new WebSocket("ws://localhost:3000/chat");
  socket.addEventListener("open", () => {
    console.log("Connected to server");
  });
  socket.addEventListener("message", (event) => {
    // Append the received message to the DOM
    const message = JSON.parse(event.data);
    const messageElement = document.createElement("div");
    messageElement.innerText = `${message.username}: ${message.message}`;
    messages_box.appendChild(messageElement);
  });
  const form = document.querySelector("#sendMessage");
  const input = document.querySelector("#chat_input");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = input.value;
    const messageObject = {
      type: "message",
      message,
    };
    socket.send(JSON.stringify(messageObject));
    input.value = "";
  });
  //   Observe the div to the bottom
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.intersectionRatio > 0) {
        console.log("Scrolled to bottom!");
      }
    });
  });
  observer.observe(document.querySelector("#bottom"));
})();
