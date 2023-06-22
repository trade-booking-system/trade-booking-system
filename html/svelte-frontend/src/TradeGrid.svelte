<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";

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

  let responseData;

  async function fetchData() {
    try {
      const response = await fetch("/api/getTrades");

      if (response.ok) {
        responseData = await response.json();
        console.log(responseData);
        responseData.forEach((element) => {
          rowData.push(element);
        });
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

  onMount(async () => {
    await fetchData();
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
