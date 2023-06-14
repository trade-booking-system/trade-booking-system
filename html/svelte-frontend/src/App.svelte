<script>
  import { Button, Dropdown, DropdownItem, Chevron } from "flowbite-svelte";
</script>

<main>
  <Button><Chevron>Accounts</Chevron></Button>
  <Dropdown>
      <DropdownItem>Account 1</DropdownItem>
      <DropdownItem>Account 2</DropdownItem>
      <DropdownItem>Account 3</DropdownItem>
  </Dropdown>
</main>

<!-- <main>
  <div class = "card logo">
    <button>Get</button>
  </div>
  <div class = "card logo">
    <button>Post</button>
  </div>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  /* .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  } */
</style> -->
