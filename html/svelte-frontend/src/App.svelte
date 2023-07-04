<script>
  import Accountpicker from "./Dropdown.svelte";
  import HelloButton from "./HelloButton.svelte";
  import SumSearch from "./SumSearch.svelte";
  import TradeGrid from "./TradeGrid.svelte";
  import PositionsGrid from "./PositionsGrid.svelte";
  import WebSocketTest from "./WebSocketTest.svelte";
  import { writable } from 'svelte/store'
  import BulkBookingTabs from "./BulkBookingTabs.svelte";
  import { getContext } from "svelte";

  const checkedAccountsStore = writable([]);
  let checkedAccounts = [];
  checkedAccountsStore.subscribe(value => {
    checkedAccounts = value
  })

</script>

<div class="container">
<div id="bulkBookingTabs" class = "bottomPadding">
    <BulkBookingTabs/>
  </div>
  <div class="accountpicker">
    <Accountpicker {checkedAccountsStore}/>
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
    <PositionsGrid {checkedAccounts}/>
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
