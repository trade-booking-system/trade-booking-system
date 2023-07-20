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

  import { onMount } from "svelte";

  import BulkBookingGrid from "./BulkBookingGrid.svelte";

  let validTickers = [];

  let tickers = '', accounts = '', buyOrSell = '', shares = '', price = '';

  let tradesToGenerate;

  let amountOfTradesPerGrouping;

  let tradeData = [];

  let submitTrade = false;

  let fileUpload;

  let buttonName;

  let deleteCall = false;

  $: deletebuttonTitle = buttonName;

  let validationErrors = [];

function validateForm() {
  validationErrors = [];

  const splitTickers = tickers.split(',').map(ticker => ticker.trim().toUpperCase());
  splitTickers.forEach(ticker => {
    if (!validTickers.includes(ticker)) {
      validationErrors.push(`Invalid Ticker: ${ticker}`);
    }
  });

  const splitBuyOrSell = buyOrSell.split(',').map(input => input.trim().toLowerCase());
  splitBuyOrSell.forEach(input => {
    if (input !== 'b' && input !== 's') {
      validationErrors.push(`Invalid Buy or Sell input: ${input}`);
    }
  });

  const splitShares = shares.split(',').map(share => parseFloat(share.trim()));
  splitShares.forEach(share => {
    if (share <= 0) {
      validationErrors.push(`Shares must be greater than 0, got: ${share}`);
    }
  });

  const splitPrice = price.split(',').map(price => parseFloat(price.trim()));
  splitPrice.forEach(price => {
    if (price <= 0) {
      validationErrors.push(`Price must be greater than 0, got: ${price}`);
    }
  });

  if (tradesToGenerate <= 0) {
    validationErrors.push(`Trades to Generate must be greater than 0, got: ${tradesToGenerate}`);
  }

  if (amountOfTradesPerGrouping <= 0 && !undefined) {
    validationErrors.push(`Amount of Trades Per Grouping must be greater than 0, got: ${amountOfTradesPerGrouping}`);
  }

  // If validationErrors is empty, the form is valid
  return validationErrors.length === 0;
}

  function handleAdd(){
    event.preventDefault();
    //splits data as needed

    if (!validateForm()) {
    alert('There are errors in the form:\n' + validationErrors.join('\n'));
    return;
  }

    const splitTickers = tickers.split(',').map(ticker => ticker.trim().toUpperCase()), 
    splitAccounts = accounts.split(',').map(account => account.trim()),
    splitBuyOrSell = buyOrSell.split(',').map(account => account.trim().toLowerCase()),
    splitShares = shares.split(',').map(share => parseFloat(share.trim())),
    splitPrice = price.split(',').map(price => parseFloat(price.trim()));

    const tradeJson = createRows(splitTickers,splitAccounts,splitBuyOrSell,splitShares,splitPrice);

    tradeData = [...tradeData, ...tradeJson];

  }

  /*
   * if there is or isnt an uneven amount of inputs this deals w it 
   */
  function createRows(splitTickers, splitAccounts, splitBuyOrSell, splitShares, splitPrice){
    let amountOfIterations = 0;
    const createdTrades = [];

 
    while (amountOfIterations <= tradesToGenerate - 1){
      let index = amountOfIterations % splitTickers.length;
      const currentTicker = splitTickers[index];
      
      let indexOfAccounts = amountOfIterations % splitAccounts.length;
      const currentAccount = splitAccounts[indexOfAccounts];
      
      let indexOfBuyOrSell = amountOfIterations % splitBuyOrSell.length;
      const currentBuyOrSell = splitBuyOrSell[indexOfBuyOrSell];

      let indexOfSplitShares = amountOfIterations % splitShares.length;
      const currentShares = splitShares[indexOfSplitShares];
      
      let indexOfPrice = amountOfIterations % splitPrice.length;
      const currentPrice = splitPrice[indexOfPrice];

      createdTrades.push({
        tickers: currentTicker,
        accounts: currentAccount,
        buyOrSell: currentBuyOrSell,
        shares: currentShares,
        price: currentPrice,
      });

      amountOfIterations++;
    }

  return createdTrades;


  }

  function handleDelete() {
    deleteCall = true;
  }

  function submitTrades(){
    submitTrade = true;

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

  async function uploadFile() {
    try{
      let data = new FormData();

      data.append('file', fileUpload);

      const response = await fetch('api/csvToJson', {
        method: 'POST',
        body: data,
      });

      if(!response.ok){
        throw new Error('Network Response not OK');
      }

      const jsonData = await response.json();

      tradeData = jsonData;

      console.log({jsonData: jsonData});
    } catch (error){
      console.error('this error');
    }
  }

  onMount( async () => {
    try {
      const response = await fetch('/api/tickers');
      if (response.ok) {
        const data = await response.json();
        validTickers = [...data];
        console.log({ tickers: validTickers });
      } else {
        console.error('Failed to fetch tickers:', response.status);
      }
    } catch (error) {
      console.error('Error while fetching tickers:', error);
    }
  });
</script>
<div class="bg-backgroundProj-100">

  <Tabs class = "bg-backgroundProj-100 mb-4" contentClass = 'bg-backgroundProj-100' activeClasses = "bg-orangeProj-100" inactiveClasses = "bg-backgroundProj-100"  >
    <TabItem open>
      <span slot="title">Import From CSV</span>
      <Label class="pb-2 text-orangeProj-100 font-bold mt-2">Upload CSV file</Label>
      <Fileupload on:change={handleFileChange}/>

      {#if fileUpload != null}
        <GradientButton color="tealToLime" class="mt-3" on:click={uploadFile}>Upload</GradientButton>
      {:else}
        <GradientButton color="tealToLime" class="mt-3" on:click={uploadFile} disabled>Upload</GradientButton>
      {/if}
    </TabItem>
    <TabItem>
      <span slot="title">Generate Bulk Trades</span>
      <form on:submit|preventDefault="{handleAdd}">
        <Label class="block mt-2 mb-2">
          <div class="orange">
            Ticker Ladder
          </div>
        </Label>
        <Input label="Ticker-Ladder" id="Ticker-Ladder" name="Ticker-Ladder" required placeholder="Enter a Value like: AAPL,IBM,MSFT" bind:value = "{tickers}"/>
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
        <Input label="Account-Ladder" id="Account-Ladder" name="Account-Ladder" required placeholder="Enter a Value like: Account-1,Account-2,Account-3" bind:value = "{accounts}"/>
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
        <Input label="Buy/Sell-Ladder" id="Buy/Sell-Ladder" name="Buy/Sell-Ladder" required placeholder="Enter a Value like: b,b,s" bind:value = "{buyOrSell}"/>
        <Helper class="text-sm mb-2">
          <div class="helper">
            Please enter a comma seperated list of b (buy) or s (sell).
          </div>
        </Helper>

        <Label class="block mb-2">
          <div class="orange">
            Shares Ladder
          </div>
        </Label>
        <Input label="Shares-Ladder" id="Shares-Ladder" name="Shares-Ladder" required placeholder="Enter a Value like: 5,100,50" bind:value = "{shares}"/>
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
        <Input label="Price-Ladder" id="Price-Ladder" name="Price-Ladder" required placeholder="Enter a Value like: 10,15.5,32" bind:value = "{price}"/>
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
        <Input label="Total-Trades" id="Total-Trades" name="Total-Trades" required placeholder="Enter a Value like: 500" bind:value = "{tradesToGenerate}"/>
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
    <Input label="Trades-Per-BulkBooking" id="Trades-Per-BulkBooking" name="Trades-Per-BulkBooking" required placeholder="Enter a value like: 100" bind:value = "{amountOfTradesPerGrouping}"/>
    <Helper class="text-sm mb-2">
      <div class="helper">
        Please enter the amount of trades per grouping
      </div>
    </Helper>
    <GradientButton color="purpleToBlue" class = "mb-4"on:click = {submitTrades}>Bulk Book</GradientButton>
  </div>

  <BulkBookingGrid bind:tradeData = {tradeData} bind:deleteCall = {deleteCall} bind:buttonName = {buttonName} bind:submitTrade = {submitTrade} bind:amountOfTradesPerGrouping = {amountOfTradesPerGrouping}/>
</div>
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