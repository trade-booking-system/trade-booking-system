<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";

  export let tradeData = [];

  export let deleteCall = false;

  export let buttonName;

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
    onSelectionChanged: function() {
        const selectedNodes = this.api.getSelectedNodes();
        amountOfSelectedNodes = selectedNodes.length;
    },
  };

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
        tradeData = tradeData.filter(trade => !selectedNodes.find(node => node.data === trade));
        currentRows = getAllRows();
        rowData = currentRows;
        console.log({currentRows: currentRows});
      }
      console.log(deleteCall);
      deleteCall = false;
  }

  function getAllRows(){
    let rowNodes = [];
    //gridOptions.apiforEachNode(node => rowNodes.push(node.data));
    rowNodes = gridOptions.api.getRenderedNodes().map(node => node.data);
    console.log({rowNodes: rowNodes})
    return rowNodes;
  }

  function populateGrid(){
    // Clear rowData
    rowData = [];
    rowData = getAllRows();
    // Populate rowData with tradeData
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
    console.log({tradeData: tradeData});
    console.log({rowData:  rowData});
    currentRows = [...tradeData];
    tradeData = [];
  };

    $: {
      if(tradeData.length > 0 && deleteCall === false){
      //comment up all of the code
      //maybe make a specific tradedata object to signify to clear grid
        populateGrid();
      }
      if (deleteCall === true){
        deleteNodes();
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
