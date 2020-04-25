const button = document.getElementById("submit");
button.addEventListener("click", async (_) => {
  const yaml = document.getElementById("yaml");
  console.log(yaml.innerText);
  let message = "Failed to convert docker-compose to Docker cli.";

  try {
    const response = await fetch("/docker/compose", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ docker_compose: yaml.innerText }),
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
  console.log(message);
  const bash = document.getElementById("bash");
  bash.innerHTML = Prism.highlight(message, Prism.languages.bash, "bash");

  copyToClipboard(bash);
  showSnackBar();
});

function showSnackBar() {
  const snackbar = document.getElementById("snackbar");
  snackbar.className = "show";
  setTimeout(function() {
    snackbar.className = snackbar.className.replace("show", "");
  }, 3000);
}

function copyToClipboard(bash) {
  const element = document.createElement("textarea");
  element.value = bash.innerText;
  element.setAttribute("readonly", "");
  element.style.position = "absolute";
  element.style.left = "-9999px";
  document.body.appendChild(element);
  element.select();
  document.execCommand("copy");
  document.body.removeChild(element);
}

function reRunPrismJS() {
  const yamlEditable = document.getElementById("yaml-editable");
  const dockerCompose = yamlEditable.innerText;
  yamlEditable.innerHTML = "";
  yamlEditable.innerHTML += '<code id="yaml" class="language-yaml"></code>';
  const yaml = document.getElementById("yaml");
  yaml.innerHTML = Prism.highlight(dockerCompose, Prism.languages.yaml, "yaml");
}
