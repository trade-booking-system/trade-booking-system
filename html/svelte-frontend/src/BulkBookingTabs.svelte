<script>
  import { Tabs, TabItem, GradientButton, Label, Fileupload, Input, Helper } from 'flowbite-svelte';

  let fileuploadprops = {
    id : 'user_avatar'
  }

</script>

<Tabs>
  <TabItem open>
    <span slot="title">Import From CSV</span>
    <Label class="pb-2">Upload CSV file</Label>
    <Fileupload {...fileuploadprops} />
  </TabItem>
  <TabItem>
    <span slot="title">Generate Bulk Trades</span>

    <Label class='block mb-2'><div class="orange">Ticker Ladder</div></Label>
    <Input label="Ticker-Ladder" id="Ticker-Ladder" name="Ticker-Ladder" required placeholder="AMA,IBM,MSFT"/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter a comma seperated list of tickers.</div></Helper>

    <Label class='block mb-2'><div class="orange">Account Ladder</div></Label>
    <Input label="Account-Ladder" id="Account-Ladder" name="Account-Ladder" required placeholder="Account-1,Account-2,Account-3"/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter a comma seperated list of accounts.</div></Helper>

    <Label class='block mb-2'><div class="orange">Buy/Sell Ladder</div></Label>
    <Input label="Buy/Sell-Ladder" id="Buy/Sell-Ladder" name="Buy/Sell-Ladder" required placeholder="B,B,S"/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter a comma seperated list of B or S.</div></Helper>

    <Label class='block mb-2'><div class="orange">Shares Ladder</div></Label>
    <Input label="Shares-Ladder" id="Shares-Ladder" name="Shares-Ladder" required placeholder="5,100,50"/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter a comma seperated list of the amount of shares.</div></Helper>

    <Label class='block mb-2'><div class="orange">Price Ladder</div></Label>
    <Input label="Price-Ladder" id="Price-Ladder" name="Price-Ladder" required placeholder="10,15.5,32"/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter a comma seperated list of prices.</div></Helper>

    <Label class='block mb-2'><div class="orange">Total Trades</div></Label>
    <Input label="Total-Trades" id="Total-Trades" name="Total-Trades" required placeholder= 500/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter the total number of trades to book.</div></Helper>

    <GradientButton color="tealToLime">Add</GradientButton>
    <GradientButton color="pinkToOrange">Replace</GradientButton>

  </TabItem>
</Tabs>

<div>
    <Label class='block mt-2 mb-2'><div class="orange">Trades Per Bulk Booking</div></Label>
    <Input label="Trades-Per-BulkBooking" id="Trades-Per-BulkBooking" name="Trades-Per-BulkBooking" required placeholder=50/>
    <Helper class='text-sm mb-2'><div class="helper">Please enter the amount of trades per grouping</div></Helper>
    <GradientButton color="purpleToBlue">Bulk Book</GradientButton>
</div>
<style>
  .orange{
    color: orangered;
    font-weight: bold;
  }

  .helper{
    opacity: 50%;
    color: gray;
  }

</style>
