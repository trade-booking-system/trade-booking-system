<script>
  import Accountpicker from "./Dropdown.svelte";
  import HelloButton from "./HelloButton.svelte";
  import SumSearch from "./SumSearch.svelte";
  import TradeGrid from "./TradeGrid.svelte";
  import PositionsGrid from "./PositionsGrid.svelte";
  import WebSocketTest from "./WebSocketTest.svelte";
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
  <div class="WebSocketTest">
    <WebSocketTest />
  </div>
  <div id = "tradeGrid" class = "bottomPadding">
    <TradeGrid/>
  </div>
  <div id = "positionsGrid" class = "bottomPadding">
    <PositionsGrid/>
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

  .bottomPadding{
    padding-bottom: 5vh;
  }
</style>
