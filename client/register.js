(async () => {
  const form = document.querySelector("#chat_regis");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.querySelector("#username").value;
    if (!username) {
      alert("Please enter a username");
      return;
    }
    const formdata = new FormData();
    formdata.append("username", username);
    const takeUsername = await fetch("http://localhost:3000/", {
      method: "POST",
      credentials: "include",
      body: formdata,
    });
    if (!takeUsername.ok) {
      alert("Username already exists");
      return;
    }
    alert("Welcome to my chat app");
    if (takeUsername.ok) {
      location.href = "/index.html";
    }
  });
})();
