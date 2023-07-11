<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";
    import { append_hydration } from "svelte/internal";
    import PositionsGrid from "./PositionsGrid.svelte";

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

  export let checkedAccounts;

  let rowData = [];
  let trades = [];

  let responseData;

  $: {
    if(checkedAccounts.length > 0){
      populateTradeGrid();
      console.log('updating trades');
      const ws = new WebSocket("ws://" + window.location.hostname + `/ws/trades?accounts=${checkedAccounts.join(',')}`);
      ws.onmessage = (updatedData) => {
        let jsonData = updatedData.data.json();
        let newTrade = jsonData.payload
        rowData.forEach(trade => {
          if(trade.id == newTrade.id){
            let index = trades.indexOf(trade);
            if(index > -1){
              trades.splice(index, 1);
            }
            trades.push(trade);
          }
        });
        rowData = [];
        populateRowData();
        if (gridOptions.api) {
          gridOptions.api.setRowData(rowData);
        }
      }
    }
    else{
      rowData = [];
      if (gridOptions.api) {
        gridOptions.api.setRowData(rowData);
      }
    }
  }
  async function populateTradeGrid() {
    console.log('trades checked accounts changed');
    trades = [];
    console.log('cleared trades');

    const getTradePromises = checkedAccounts.map(account => getTrades(account));
    const tradesArray = await Promise.all(getTradePromises);
    trades = tradesArray.flat();

    console.log('trades', trades);
    rowData =[];
    console.log("cleared trade row data");
    populateRowData();
    if (gridOptions.api) {
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
    --ag-header-foreground-color: orangered;
  }
  :global(.ag-header-cell) {
    font-size: 16px;
  }
</style>
