<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";


  export let tradeData = [];

  export let deleteCall = false;

  export let buttonName;

  export let submitTrade = false;

  export let amountOfTradesPerGrouping;

  //this is in order for the to alway be a store of which data is currently being displayed
  let currentRows = [];

  let gridContainer;
  let grid;

  let amountOfSelectedNodes = 0;

  //this is where column headers are defined
  const columnDefs = [
    {
      headerName: "Bulk Booking Grid",
      children: [
        {
          headerName: "Delete",
          field: "Delete",
          checkboxSelection: true,
          headerCheckboxSelection: true,
          headerCheckboxSelectionFilteredOnly: true, 
          width: 80
        },
        { field: "ID" },
        { 
          field: "Ticker", 
          filter: true,
        },
        { field: "Account", 
          filter: true, 
        },
        { field: "BuyOrSell", 
          filter: true, 
        },
        { field: "Shares",
          filter: "agNumberColumnFilter", 
        },
        { field: "Price", 
          filter: "agNumberColumnFilter", 
        },
        { field: "Booked_At" },
        { field: "Request_Group" }
      ]
    }
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
    enableSorting: true,
    rowGroupPanelShow: 'always', // to show the row group panel
    groupMultiAutoColumn: true,
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
    gridOptions.api.forEachNode((node, index) => {
      if(node !== undefined){
        rowNodes.push(node.data);
      }
    });
    return rowNodes;
  }

  function getAllRowsForTradeSubmission(){
    let rowNodes = [];
     gridOptions.api.forEachNode((node, index) => {
      //if id is null that means it hasnt been submitted
        if (node.data.ID === null || node.data.ID === undefined) {
            rowNodes.push({
                account: node.data.Account,
                type: node.data.BuyOrSell, 
                stock_ticker: node.data.Ticker, 
                amount: node.data.Shares,
                price: node.data.Price, 
                user: 'BulkBookingPortal',  // User is hardcoded because it's always coming from the BulkBooking UI
            });
        }
    });
    return rowNodes;
  }

  function getAllSubmittedRows(){
    let rowNodes = [];
    gridOptions.api.forEachNode((node, index) => {
      //this means it has been submitted
        if (node.data.ID != null && node.data.ID != undefined) {
            rowNodes.push( {
              ID: node.data.ID,
              Booked_At: node.data.Booked_At,
              Request_Group: node.data.Request_Group,
              Account: node.data.Account,
              BuyOrSell: node.data.BuyOrSell, 
              Ticker: node.data.Ticker, 
              Shares: node.data.Shares,
              Price: node.data.Price,   
            });
        }
    });
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

    function populateGridBulkBook(data){
    // Clear rowData
    rowData = getAllSubmittedRows();
    // Populate rowData with tradeData (properly formatting it)
    data.forEach(element => {
      rowData.push({
        ID: element.id,
        Booked_At: element.booked_at,
        Request_Group: element.request_group,
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
    currentRows = [...tradeData, ...data];
    data = [];
  };


  $: {
    if(tradeData.length > 0 && deleteCall === false && submitTrade === false){
      populateGrid();
    }
    if (deleteCall === true){
      deleteNodes();
    }
    if (submitTrade === true){
      groupTrades();
    }
  }

  function groupTrades(){
    const currentSubmission = getAllRowsForTradeSubmission();

    if (currentSubmission.length == 0){
      submitTrade = false;
      return;
    }

    let tradesToSubmitGrouped = [];
    let counter = 0;

    if (amountOfTradesPerGrouping == undefined || amountOfTradesPerGrouping == null || amountOfTradesPerGrouping == 0 || currentSubmission.length < amountOfTradesPerGrouping){
      amountOfTradesPerGrouping = 100;
    }
    
    for (let index = 0; index < currentSubmission.length; index++) {
      const element = currentSubmission[index];
      tradesToSubmitGrouped.push(element);
      counter++;
      if (counter == amountOfTradesPerGrouping) {
        submitTrades(tradesToSubmitGrouped);
        tradesToSubmitGrouped = [];
        counter = 0;
      }
    }
    //if there are still unsubmitted trades submit them
    if (tradesToSubmitGrouped.length > 0){
      submitTrades(tradesToSubmitGrouped);
    }
  }

  async function submitTrades(currentSubmission){
    try{
      const response = await fetch('api//bookManyTrades', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentSubmission),
      });

      if(!response.ok){
        const errorText = await response.text();
        alert(`Error: ${errorText}`);
        throw new Error(`Response not ok: ${errorText}`);
      }

      const jsonData = await response.json();
      const data = jsonData;
      console.log({dataSubmitTrades: data});
      populateGridBulkBook(data);
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
    --ag-header-foreground-color: #95C3B5;
    --ag-border-color: #95C3B5;
    --ag-header-background-color: #202020;
    --ag-background-color: #202020;
    --ag-selected-row-background-color: #226272;
    /* --ag-odd-row-background-color: none; */
  }
  /* :global(.ag-header-cell) {
    font-size: 16px;
  } */
</style>
