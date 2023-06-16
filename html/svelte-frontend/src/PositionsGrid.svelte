<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";

  let gridContainer;
  let grid;

  //this is where column headers are defined
  const columnDefs = [
    { field: "Account" },
    { field: "Ticker" },
    { field: "Quantity" },
    { field: "LastAggregationTime" },
    { field: "SystemLastAggregationProcessHost_Id" },
  ];

  //this allows you to drag and resize columns 
  const defaultColDef = {
    resizable: true,
  };

/**
 * This is where the rows are created
 * the format for data is {field:data}
 * {
 * Account:"account1"
 * price: 100
 * }
 */
  const rowData = [
    {
      Account: "Account 1",
      Ticker: "AMA",
      Quantity: "1000",
      Time: 12,
      LastAggregationTime: "10-00-00",
      SystemLastAggregationProcessHost_Id: "00000000",
    },
    {
      Account: "Account 1",
      Ticker: "AMA",
      Quantity: "1000",
      Time: 12,
      LastAggregationTime: "10-00-00",
      SystemLastAggregationProcessHost_Id: "00000000",
    },
    {
      Account: "Account 1",
      Ticker: "AMA",
      Quantity: "1000",
      Time: 12,
      LastAggregationTime: "10-00-00",
      SystemLastAggregationProcessHost_Id: "00000000",
    },
  ];

  const gridOptions = {
    defaultColDef: defaultColDef,
    columnDefs: columnDefs,
    rowData: rowData,
  };

  function sizeToFit() {
    gridOptions.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    });
  }
  onMount(() => {
    window.addEventListener("resize", sizeToFit); //handles auto resizing: any time the window resizes at all it makes the grid resized to fit screen 
    grid = new Grid(gridContainer, gridOptions); //creates the actual ag-grid
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
