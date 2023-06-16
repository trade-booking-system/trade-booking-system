<script>
  import { Button, Dropdown, DropdownItem, Chevron } from "flowbite-svelte";

  const accounts = [];

  let selectedAccount;

  const selectAccount = (account) => {
    selectedAccount = account;
  };

  let responseData;

  async function fetchData() {
      try {
        const response = await fetch('/api/accounts/');
      
        if (response.ok) {
          responseData = await response.json();
          responseData.forEach(element => {
            accounts.push(element);
          });
      } else {
          console.error('Error:', response.status);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  }
</script>

<div class="allign_with_top">
  <Button on:click={fetchData}><Chevron>Accounts</Chevron></Button>
  <Dropdown>
    {#each accounts as account}
      <DropdownItem on:click={() => selectAccount(account)}
        >{account}</DropdownItem
      >
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
