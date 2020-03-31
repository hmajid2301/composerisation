const button = document.getElementById("submit");
button.addEventListener("click", async _ => {
  const yaml = document.getElementById("yaml");
  let message = "Failed to convert docker-compose to Docker cli.";

  try {
    const response = await fetch("/docker/compose", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ docker_compose: yaml.innerText })
    });
    console.log(response);
    if (response.status == 200) {
      const data = await response.json();
      console.log(data);
      message = data.docker_cli;
    }
  } catch (err) {
    console.log(err);
    message = err;
  }
  document.getElementById("bash").innerText = message;
});
