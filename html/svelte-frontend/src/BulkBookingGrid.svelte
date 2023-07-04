<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";

  export let tradeData = [];

  export let deleteCall = false;

  export let buttonName;

  export let submitTrade = false;

  export let tradesPosted = [];

  //this is in order for the to alway be a store of which data is currently being displayed
  let currentRows = [];

  let gridContainer;
  let grid;

  let amountOfSelectedNodes = 0;

  //this is where column headers are defined
  const columnDefs = [
    {
      headerName: "Delete",
      field: "Delete",
      checkboxSelection: true,
      headerCheckboxSelection: true,
      headerCheckboxSelectionFilteredOnly: true, 
      width: 80
    },
    { field: "ID" },
    { field: "Ticker" },
    { field: "Account" },
    { field: "BuyOrSell" },
    { field: "Shares" },
    { field: "Price" },
    { field: "Booked-At" },
    { field: "Request-Group" }
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

  let rowData = [];

  const rowselection = 'multiple';

  const gridOptions = {
    defaultColDef: defaultColDef,
    columnDefs: columnDefs,
    rowData: rowData,
    rowMultiSelectWithClick: true,
    rowSelection: rowselection,
    //this is for the reactive element below
    onSelectionChanged: function() {
        const selectedNodes = this.api.getSelectedNodes();
        amountOfSelectedNodes = selectedNodes.length;
    },
  };

  //in bulkbookingtabs  - this makes the button display there and activate/disable as needed
  $:{
    if (amountOfSelectedNodes === 1){
      buttonName = 'Delete Selected Row';
    }
    else if (amountOfSelectedNodes > 1) {
      buttonName = 'Delete Selected Rows';
    }
    else {
      buttonName = 'Please Select to Delete';
    }
  }


  function deleteNodes(){
      console.log("calls internal delete");
      const selectedNodes = gridOptions.api.getSelectedNodes();
      if (selectedNodes.length > 0){
        gridOptions.api.applyTransaction({ remove: selectedNodes.map(node => node.data) });
        tradeData = tradeData.filter(trade => !selectedNodes.find(node => node.data === trade)); //removes selected rows from tradedata ("deleting them")
        currentRows = getAllRows();
        rowData = currentRows;
      }
      deleteCall = false;
  }

  function getAllRows(){
    let rowNodes = [];
    rowNodes = gridOptions.api.getRenderedNodes().map(node => node.data);
    console.log({rowNodes: rowNodes})
    return rowNodes;
  }

  function getAllRowsForTradeSubmission(){
    let rowNodes = [];
    rowNodes = gridOptions.api.getRenderedNodes().map(node => {
      return {
        account: node.data.Account,
        type: node.data.BuyOrSell, 
        stock_ticker: node.data.Ticker, 
        amount: node.data.Shares,
        price: node.data.Price, 
        user: 'BulkBookingPortal',  // User is hardcoded because its always coming from the BulkBooking UI
      };
    });
    console.log({rowNodes: rowNodes})
    return rowNodes;
  }


  function populateGrid(){
    // Clear rowData
    rowData = [];
    rowData = getAllRows();
    // Populate rowData with tradeData (properly formatting it)
    tradeData.forEach(element => {
      rowData.push({
        Ticker: element.tickers,
        Account: element.accounts,
        BuyOrSell: element.buyOrSell,
        Shares: element.shares,
        Price: element.price,
      });
    });
    // Update the grid with rowData
    if (gridOptions.api) {
      gridOptions.api.setRowData(rowData);
    }
    currentRows = [...tradeData];
    tradeData = [];
  };


  $: {
    if(tradeData.length > 0 && deleteCall === false && submitTrade === false){
      populateGrid();
    }
    if (deleteCall === true){
      deleteNodes();
    }
    if (submitTrade === true){
      submitTrades();
    }
  }

  async function submitTrades(){
    const currentSubmission = getAllRowsForTradeSubmission();
    console.log(currentRows);

    try{
      const response = await fetch('api/bookTradesBulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentSubmission),
      });

      if(!response.ok){
        const errorText = await response.text();
        throw new Error(`Response not ok: ${errorText}`);
      }

      const jsonData = await response.json();
      console.log("made it to jsondata");

      tradeData = jsonData;

      console.log({tradeData: tradeData});

      populateGrid();
      console.log('why is it not populating grid then?');

      submitTrade = false;
    } catch (error){

      submitTrade = false;
      tradeData = [];
      console.error('Error:', error);
    }


  } 

  function sizeToFit() {
    gridOptions.api.sizeColumnsToFit({
      defaultMinWidth: 100,
    });
  }
  onMount(() => {
    window.addEventListener("resize", sizeToFit); //handles auto resizing: any time the window resizes at all it makes the grid resized to fit screen 
    // @ts-ignore (this doesnt actually seem to cause any problems in the code it just turns red)
    grid = new Grid(gridContainer, gridOptions); //creates the actual ag-grid
    sizeToFit();
    populateGrid();
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
