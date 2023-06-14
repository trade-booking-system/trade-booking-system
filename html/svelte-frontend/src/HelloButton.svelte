<script>
    import {Button} from "flowbite-svelte";

    let responseData;

    async function fetchData() {
        try {
        const response = await fetch('/api/hello');
        
        if (response.ok) {
            responseData = await response.json();
        } else {
            console.error('Error:', response.status);
        }
        } catch (error) {
        console.error('Error:', error);
        }
    }
</script>

<div>
  <Button on:click={fetchData}>hello</Button>
</div>

{#if responseData !== undefined}
  <h1>{responseData.hello}</h1>
{/if}