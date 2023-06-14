<script>
    import { Button, Dropdown, DropdownItem, Chevron } from "flowbite-svelte";

    const accounts = ["Account 1", "Account 2", "Account 3"];

    let selectedAccount;

    const selectAccount = (account) => {
        selectedAccount = account;
    };
</script>

<div class="allign_with_top">
    <Button><Chevron>Accounts</Chevron></Button>
    <Dropdown>
        {#each accounts as account}
            <DropdownItem on:click={() => selectAccount(account)}>
                {account}</DropdownItem
            >
        {/each}
    </Dropdown>
    {#if selectedAccount !== undefined}
        <h1>{selectedAccount}</h1>
    {/if}
</div>
