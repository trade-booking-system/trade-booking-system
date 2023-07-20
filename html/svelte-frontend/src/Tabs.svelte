<script>
    import { Tabs, TabItem } from "flowbite-svelte";
    import Dropdown from "./Dropdown.svelte";
    import TradeGrid from "./TradeGrid.svelte";
    import PositionsGrid from "./PositionsGrid.svelte";
    import BulkBookingTabs from "./BulkBookingTabs.svelte";
</script>

<Tabs
    style="full"
    defaultClass="flex mb-4"
    class = "bg-backgroundProj-100" contentClass = 'bg-backgroundProj-100' activeClasses = "!bg-orangeProj-100" inactiveClasses = "!bg-backgroundProj-100"
>
    <TabItem class="w-full" open>
        <span slot="title">Position Management</span>
        <div class="dropdown" style="position: relative; z-index: 1;">
            <Dropdown />
        </div>
        <PositionsGrid />
        <TradeGrid />
    </TabItem>
    <TabItem class="w-full bg-backgroundProj-100" >
        <span slot="title">Bulk Booking</span>
        <BulkBookingTabs />
    </TabItem>
</Tabs>

<style>
.dropdown {
    margin-bottom: 10%;
  }
</style>
