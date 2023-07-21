<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";
  import { checkedAccounts } from "./checkedAccounts";

  let gridContainer;
  let grid;

  const columnDefs = [
    { field: "id" },
    { field: "account" },
    { field: "type" },
    { field: "stock_ticker" },
    { field: "amount" },
    { field: "date" },
    { field: "time" },
    { field: "user" },
    { field: "version" },
  ];

  const defaultColDef = {
    resizable: true,
  };

  // const rowData = [
  //   {
	// 	TradeId: "0001",
	// 	TradeDate: "1/1/23",
	// 	Account:"Account1",
	// 	Ticker:"AMA",
	// 	Buy_Sell_Indicator:"",
	// 	Quantity: 5,
	// 	Price: "$100.00",
	// 	Version: "1.0",
	// 	EnteredBy:"Account 1",
	// 	EnteredDateTime:"10-00-00",
	// 	SystemProcessHost_Id: "00001",
  //   },
  //   {
	// 	TradeId: "0001",
	// 	TradeDate: "1/1/23",
	// 	Account:"Account1",
	// 	Ticker:"AMA",
	// 	Buy_Sell_Indicator:"",
	// 	Quantity: 5,
	// 	Price: "$100.00",
	// 	Version: "1.0",
	// 	EnteredBy:"Account 1",
	// 	EnteredDateTime:"10-00-00",
	// 	SystemProcessHost_Id: "00001",
  //   },
  //   {
	// 	TradeId: "0001",
	// 	TradeDate: "1/1/23",
	// 	Account:"Account1",
	// 	Ticker:"AMA",
	// 	Buy_Sell_Indicator:"",
	// 	Quantity: 5,
	// 	Price: "$100.00",
	// 	Version: "1.0",
	// 	EnteredBy:"Account 1",
	// 	EnteredDateTime:"10-00-00",
	// 	SystemProcessHost_Id: "00001",
  //   },
  // ];



  

  function sizeToFit() {
    gridOptions.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    });
  }

  let rowData = [];
  let trades = [];
  let ws = null;

  let responseData;

  async function populateTradeGrid(accounts) {
    console.log('trades checked accounts changed');
    trades = [];
    console.log('cleared trades');

    const getTradePromises = accounts.map(account => getTrades(account));
    const tradesArray = await Promise.all(getTradePromises);
    trades = tradesArray.flat();

    console.log('trades', trades);
    rowData =[];
    console.log("cleared trade row data");
    populateRowData();
    if (gridOptions !== null && gridOptions.api) {
      gridOptions.api.setRowData(rowData);
      }
  }

  function populateRowData(){
    console.log("populating trade row data");
      trades.forEach(trade => {
        rowData.push(trade);
      });
  }

  async function getTrades(account){
    try {
      const response = await fetch(`/api/queryTrades?account=${account}`);

      if (response.ok) {
        responseData = await response.json();
        console.log(responseData);
        return responseData;
      } else {
        console.error("Error:", response.status);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  const gridOptions = {
    defaultColDef: defaultColDef,
    columnDefs: columnDefs,
    rowData: rowData,
  };

  onMount(() => {
    window.addEventListener("resize", sizeToFit); //handles auto resizing
    grid = new Grid(gridContainer, gridOptions);
    sizeToFit();
    checkedAccounts.subscribe((accounts) => {
      if(accounts.length > 0){
        populateTradeGrid(accounts);
        console.log('updating trades');
        if (ws !== null) {
          ws.close()
        }
        ws = new WebSocket("ws://" + window.location.hostname + `/ws/trades?accounts=${accounts.join(',')}`);
        ws.onmessage = (updatedData) => {
          let jsonData = JSON.parse(updatedData.data);
          let newTrade = jsonData.payload;
          if (jsonData.type == "create") {
            trades.push(newTrade)
          } else {
            let index = trades.findIndex((trade) => {trade.id == newTrade.id});
            if (index > -1) {
              trades[index] = newTrade;
            }
          }
          rowData = [];
          populateRowData();
          if (gridOptions !== undefined && gridOptions.api) {
            gridOptions.api.setRowData(rowData);
          }
        }
      }
      else {
        rowData = [];
        if (gridOptions !== undefined && gridOptions.api) {
          gridOptions.api.setRowData(rowData);
        }
      }
    });
  });

  onDestroy(() => {
    window.removeEventListener("resize", sizeToFit);
    if (grid) {
      grid.destroy();
    }
  });
</script>

<svelte:head>
  <script
    src="https://unpkg.com/ag-grid-community/dist/ag-grid-community.min.noStyle.js"
  ></script>
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/ag-grid-community@29.0.0/styles/ag-grid.css"
  />
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/ag-grid-community@29.0.0/styles/ag-theme-alpine.css"
  />
</svelte:head>

<div
  id="datagrid"
  class="ag-theme-alpine-dark"
  style="height: 50vh; width:80vw;"
  bind:this={gridContainer}
/>

<style>
  #datagrid {
    --ag-header-foreground-color: #95C3B5;
    --ag-border-color: #95C3B5;
    --ag-header-background-color: #202020;
    --ag-background-color: #202020;
    --ag-selected-row-background-color: #226272;
    /* --ag-odd-row-background-color: none; */
  }
  :global(.ag-header-cell) {
    font-size: 16px;
  }
</style>
