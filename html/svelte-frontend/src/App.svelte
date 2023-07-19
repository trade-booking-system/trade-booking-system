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
  import Tabs from "./Tabs.svelte";


</script>

<div class="container">
  <div id="tabs" class = "bottomPadding">
    <Tabs/>
  </div>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .bottomPadding{
    padding-bottom: 5vh;
  }
</style>
