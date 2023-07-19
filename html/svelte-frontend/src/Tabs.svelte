<script>
    import { Tabs, TabItem } from "flowbite-svelte";
    import Dropdown from "./Dropdown.svelte";
    import TradeGrid from "./TradeGrid.svelte";
    import PositionsGrid from "./PositionsGrid.svelte";
    import BulkBookingTabs from "./BulkBookingTabs.svelte";
</script>

<Tabs
    style="full"
    defaultClass="flex rounded-lg divide-x divide-gray-200 shadow dark:divide-gray-700"
>
    <TabItem class="w-full" open>
        <span slot="title">Position Management</span>
        <div class="dropdown">
            <Dropdown />
        </div>
        <PositionsGrid />
        <TradeGrid />
    </TabItem>
    <TabItem class="w-full">
        <span slot="title">Bulk Booking</span>
        <BulkBookingTabs />
    </TabItem>
</Tabs>

<style>
.dropdown {
    margin-bottom: 10%;
  }
</style>
