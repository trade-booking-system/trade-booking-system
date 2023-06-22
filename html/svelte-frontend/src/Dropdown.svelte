<script>
  import { onMount } from "svelte";
  import { Button, Dropdown, DropdownItem, Chevron, Checkbox } from "flowbite-svelte";

  const accounts = [];

  let selectedAccount;

  const selectAccount = (account) => {
    selectedAccount = account;
  };

  let responseData;

  async function fetchData() {
    try {
      const response = await fetch("/api/getAccounts");

      if (response.ok) {
        responseData = await response.json();
        console.log(responseData);
        responseData.forEach((element) => {
          accounts.push(element);
        });
      } else {
        console.error("Error:", response.status);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  onMount(fetchData);
</script>

<div class="allign_with_top">
  <Button><Chevron>Accounts</Chevron></Button>
  <Dropdown class="w-58 overflow-y-auto py-1 h-48">
    {#each accounts as account}
      <Checkbox
        class="w-58 p-3 space-y-3 text-sm"
        checked={selectedAccount === account}
        on:click={() => selectAccount(account)}>{account}</Checkbox>
    {/each}
  </Dropdown>
  {#if selectedAccount !== undefined}
    <div>
      Current Account selected: <div class="selected_account">
        {selectedAccount}
      </div>
    </div>
  {/if}
</div>

<style>
  .selected_account {
    color: orangered;
    display: inline;
    font-weight: bold;
  }
</style>
