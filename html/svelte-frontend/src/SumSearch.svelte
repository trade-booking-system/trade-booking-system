<script>
    import { Input, Label, Helper, Button } from 'flowbite-svelte';
    
    let number1 = '';
    let number2 = '';
    let SumData;

    async function getSum(){
        try{
        const sum = await fetch('/api/sum/?a=${number1}&b=${number2}')
        
        if (sum.ok) {
            SumData = await sum.json();
        } else {
            console.error('Error:', sum.status);
        }
        } catch (error) {
        console.error('Error:', error);
        }
    }
</script>

<form>
  <div class="grid gap-2 mb-2 md:grid-cols-2">
    <div>
      <Label for="first_digit" class="mb-2">First Digit</Label>
      <Input type="text" bind:value={number1} id="first_name" placeholder="x" required  />
    </div>
    <div>
      <Label for="second_digit" class="mb-2">Second Digit</Label>
      <Input type="text" bind:value={number2} id="last_name" placeholder="y" required />
    </div>
  <Button type="submit" on:click={getSum}>Sumify</Button>
</form>

{#if SumData !== undefined}
  <h1>{SumData.sum}</h1>
{/if}
  
  