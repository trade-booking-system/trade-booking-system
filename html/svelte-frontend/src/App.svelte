<script>
  import Accountpicker from "./Dropdown.svelte";
  import HelloButton from "./HelloButton.svelte";
  import SumSearch from "./SumSearch.svelte";
  import TradeGrid from "./TradeGrid.svelte"
</script>

<div class="container">
  <div class="accountpicker">
    <Accountpicker />
  </div>
  <div class="hellobutton">
    <HelloButton />
  </div>
  <div class="sumsearch">
    <SumSearch />
  </div>
  <div id = "tradeGrid">
    <TradeGrid/>
  </div>
  
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .accountpicker {
    margin-bottom: 10%;
  }
</style>
