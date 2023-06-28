<script>
  import {
    Tabs,
    TabItem,
    GradientButton,
    Label,
    Fileupload,
    Input,
    Helper,
    Indicator,
  } from "flowbite-svelte";

  import BulkBookingGrid from "./BulkBookingGrid.svelte";

  let tickers = '', accounts = '', buyOrSell = '', shares = '', price = '';

  let tradesToGenerate = 0;

  let amountOfTradesPerGrouping = 0;

  let tradeData = [];

  let fileUpload;

  let buttonName;

  let deleteCall = false;

  $: deletebuttonTitle = buttonName;

  function handleAdd(){
    event.preventDefault();
    //splits data as needed
    const splitTickers = tickers.split(',').map(ticker => ticker.trim()), 
    splitAccounts = accounts.split(',').map(account => account.trim()),
    splitBuyOrSell = buyOrSell.split(',').map(account => account.trim()),
    splitShares = shares.split(',').map(share => parseFloat(share.trim())),
    splitPrice = price.split(',').map(price => parseFloat(price.trim()));

    const tradeJson = splitTickers.map((tickers, i) => ({
      tickers,
      accounts: splitAccounts[i],
      buyOrSell : splitBuyOrSell[i],
      shares: splitShares[i],
      price: splitPrice[i] 
    }))

    tradeData = [...tradeData, ...tradeJson];

  }

function handleDelete() {
  deleteCall = true;
}

  function submitTrades(){
    event.preventDefault();
  }

  function handleFileChange(event) {
    const file = event.target.files[0];
    checkFileType(file);
  }

  function checkFileType(file) {
    const filename = file.name;
    const fileExtention = filename.split(".").pop().toLowerCase();

    if (fileExtention === "csv") {
      fileUpload = file;
      return;
    } else if (fileExtention === "xls") {
      fileUpload = file;
      return;
    } else {
      fileUpload = null;
      alert("File must be xls or csv");
      throw new Error("File is not xls or csv");
    }
  }

  function upload() {}
</script>

<Tabs>
  <TabItem open>
    <span slot="title">Import From CSV</span>
    <Label class="pb-2">Upload CSV file</Label>
    <Fileupload on:change={handleFileChange}/>

    {#if fileUpload != null}
      <GradientButton color="tealToLime" class="mt-3" on:click={upload}>Upload</GradientButton>
    {:else}
      <GradientButton color="tealToLime" class="mt-3" on:click={upload} disabled>Upload</GradientButton>
    {/if}
  </TabItem>
  <TabItem>
    <span slot="title">Generate Bulk Trades</span>
    <form on:submit|preventDefault="{handleAdd}">
      <Label class="block mb-2">
        <div class="orange">
          Ticker Ladder
        </div>
      </Label>
      <Input label="Ticker-Ladder" id="Ticker-Ladder" name="Ticker-Ladder" required placeholder="AMA,IBM,MSFT" bind:value = "{tickers}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter a comma seperated list of tickers.
        </div>
      </Helper>

      <Label class="block mb-2">
        <div class="orange">
          Account Ladder
        </div>
      </Label>
      <Input label="Account-Ladder" id="Account-Ladder" name="Account-Ladder" required placeholder="Account-1,Account-2,Account-3" bind:value = "{accounts}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter a comma seperated list of accounts.
        </div>
      </Helper>

      <Label class="block mb-2">
        <div class="orange">
          Buy/Sell Ladder
        </div>
      </Label>
      <Input label="Buy/Sell-Ladder" id="Buy/Sell-Ladder" name="Buy/Sell-Ladder" required placeholder="B,B,S" bind:value = "{buyOrSell}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter a comma seperated list of B or S.
        </div>
      </Helper>

      <Label class="block mb-2">
        <div class="orange">
          Shares Ladder
        </div>
      </Label>
      <Input label="Shares-Ladder" id="Shares-Ladder" name="Shares-Ladder" required placeholder="5,100,50" bind:value = "{shares}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter a comma seperated list of the amount of shares.
        </div>
      </Helper>

      <Label class="block mb-2">
        <div class="orange">
          Price Ladder
        </div>
      </Label>
      <Input label="Price-Ladder" id="Price-Ladder" name="Price-Ladder" required placeholder="10,15.5,32" bind:value = "{price}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter a comma seperated list of prices.
        </div>
      </Helper>

      <Label class="block mb-2">
        <div class="orange">
          Total Trades
        </div>
      </Label>
      <Input label="Total-Trades" id="Total-Trades" name="Total-Trades" required placeholder="500" bind:value = "{tradesToGenerate}"/>
      <Helper class="text-sm mb-2">
        <div class="helper">
          Please enter the total number of trades to book.
        </div>
      </Helper>

      <GradientButton color="tealToLime" on:click = {handleAdd}>Add</GradientButton>
      {#if buttonName != 'Please Select to Delete'}
      <GradientButton color="pinkToOrange" on:click = {handleDelete}>{deletebuttonTitle}</GradientButton>
    {:else}
      <GradientButton color="pinkToOrange" on:click disabled = {handleDelete}>{deletebuttonTitle}</GradientButton>
    {/if}
    </form>
  </TabItem>
</Tabs>


<div>
  <Label class="block mt-2 mb-2">
    <div class="orange">
      Trades Per Bulk Booking
    </div>
  </Label>
  <Input label="Trades-Per-BulkBooking" id="Trades-Per-BulkBooking" name="Trades-Per-BulkBooking" required placeholder="50" bind:value = "{amountOfTradesPerGrouping}"/>
  <Helper class="text-sm mb-2">
    <div class="helper">
      Please enter the amount of trades per grouping
    </div>
  </Helper>
  <GradientButton color="purpleToBlue" on:click = {submitTrades}>Bulk Book</GradientButton>
</div>

<BulkBookingGrid bind:tradeData = {tradeData} bind:deleteCall = {deleteCall} bind:buttonName = {buttonName}/>

<style>
  .orange {
    color: orangered;
    font-weight: bold;
  }

  .helper {
    opacity: 50%;
    color: gray;
  }
</style>

  <!-- id = {null} 
  ticker = {tradeData.tickers} 
  account = {tradeData.accounts} 
  buyOrSell = {tradeData.buyOrSell} 
  shares = {tradeData.shares} 
  price = {tradeData.price}
  bookedAt = {null}
  requestGroup = {null} -->