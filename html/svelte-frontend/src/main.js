import "./app.postcss";
import App from "./App.svelte";
import Dropdown from "./Dropdown.svelte"

const app = new App({
  target: document.getElementById("app"),
});

const dropdown = new Dropdown({
  target: document.getElementById("dropdown"),
});

export default app;
