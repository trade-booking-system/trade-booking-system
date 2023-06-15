<script>
  import { Input, Label, Helper, Button } from "flowbite-svelte";

  let number1 = "";
  let number2 = "";
  let SumData;

  async function getSum() {
    event.preventDefault(); //prevents page reload getting rid of the result, delete this to see what i mean
    try {
      console.log("number1:", number1);
      console.log("number2:", number2);
      const sum = await fetch(`/api/sum/?a=${number1}&b=${number2}`);

      if (sum.ok) {
        SumData = await sum.json();
      } else {
        console.error("Error:", sum.status);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }
</script>

<form>
  <div class="grid gap-2 mb-2 md:grid-cols-2 topPadding">
    <div>
      <Label for="first_digit" class="mb-2">
        <div class="whiteColor">First Digit</div>
      </Label>
      <Input
        type="text"
        bind:value={number1}
        id="first_name"
        placeholder="0"
        required
      />
    </div>
    <div>
      <Label for="second_digit" class="mb-2"> 
        <div class="whiteColor">Second Digit</div>
      </Label>
      <Input
        type="text"
        bind:value={number2}
        id="last_name"
        placeholder="0"
        required
      />
    </div>
  </div>

  <div class="bottomPadding topPadding">
    <Button type="submit" on:click={getSum}>Sumify</Button>
  </div>
</form>

{#if SumData !== undefined}
  <h1>{SumData.sum}</h1>
{/if}

<style>
  .bottomPadding {
    padding-bottom: 2vh;
  }
  .topPadding {
    padding-top: 2vh;
  }
  .whiteColor {
    color: aliceblue;
  }
</style>
