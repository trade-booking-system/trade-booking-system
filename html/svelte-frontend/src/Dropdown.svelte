<script>
  import { onMount } from "svelte";
  import {
    GradientButton,
    Dropdown,
    DropdownItem,
    Chevron,
    Checkbox,
  } from "flowbite-svelte";
  import { checkedAccounts } from "./checkedAccounts"

  const accounts = [];
  let selectedAccount;
  let checkedAccountsList;

  checkedAccounts.subscribe((accounts) => {
    selectedAccount = accounts.join(", ");
    checkedAccountsList = accounts;
  });

  function dealWithAccountSelection(account) {
    checkedAccounts.update((accounts) => {
      const index = accounts.indexOf(account);
      if (index > -1) {
        accounts.splice(index, 1);
      } else {
        accounts.push(account);
      }
      console.log(accounts);
      return accounts;
    });
  }

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
  <GradientButton color = "pinkToOrange"><Chevron>Accounts</Chevron></GradientButton>
  <Dropdown class="w-58 overflow-y-auto py-1 h-30">
    {#each accounts as account}
      <Checkbox
        class="w-58 p-3 space-y-3 text-sm overflow-y-auto center"
        checked={checkedAccountsList.includes(account)}
        on:click={() => dealWithAccountSelection(account)}>{account}</Checkbox
      >
    {/each}
  </Dropdown>
  {#if selectedAccount !== undefined}
    <div>
      Current Accounts selected: <div class="selected_account">
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
