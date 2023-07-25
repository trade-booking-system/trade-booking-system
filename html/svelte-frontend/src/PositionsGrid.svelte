<script>
  import { Grid } from "ag-grid-community";
  import { onMount, onDestroy } from "svelte";
  import { checkedAccounts } from "./checkedAccounts";

  let gridContainer;
  let grid;

  //this is where column headers are defined
  const columnDefs = [
    {
      headerName: "Positions",
      children: [
        { 
          field: "Account",
          filter: true,
        },
        { 
          field: "Ticker",
          filter: true,
        },
        { 
          field: "Quantity", 
          filter: "agNumberColumnFilter",
        },
        { field: "LastAggregationTime" },
        { field: "SystemLastAggregationProcessHost_Id" },
        { field: "Trade PL"},
        { field: "Position PL"},
        { field: "Total PL"}
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
  let positions = [];
  let rowData = [];
  let ws = null;

  async function populatePositionGrid(checkedAccounts) {
    console.log('checked Acount changed:', checkedAccounts)
    positions = [];
    console.log('cleared positions')

    const getPositionPromises = checkedAccounts.map(account => getPosition(account));
    const positionsArray = await Promise.all(getPositionPromises);
    positions = positionsArray.flat();
    
    console.log("positions", positions);

    console.log("clearing row data");
    rowData = [];
    populateRowData();
    if (gridOptions.api) {
      gridOptions.api.setRowData(rowData);
    }
  }

  async function getPosition(account){
    const response = await fetch(`api/positions/${account}`)
    if(response.ok){
      console.log("return of positions api call:", response);
      const responseJson = await response.json();
      console.log("response as a json:", responseJson);
      const positionsJson = responseJson.positions;
      console.log("positions as json:", positionsJson);
      return positionsJson;
    }
  }

  function populateRowData(){
    console.log("now populating row data");
    positions.forEach(position => {
      console.log("populating RowData")
      rowData.push({
        Account: position.account,
        Ticker: position.stock_ticker,
        Quantity: position.amount,
        LastAggregationTime: position.last_aggregation_time,
        SystemLastAggregationProcessHost_Id: position.last_aggregation_host,
        "Trade PL": position.trade_pl,
        "Position PL": position.position_pl,
        "Total PL": position.trade_pl + position.position_pl
      })
    })

  }

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
    checkedAccounts.subscribe((accounts) => {
      if(accounts.length > 0){
        populatePositionGrid(accounts);
        if (ws !== null) {
          ws.close()
        }
        ws = new WebSocket("ws://" + window.location.hostname + `/ws/positions?accounts=${accounts.join(',')}`);
        ws.onmessage = (updatedData) => {
          let jsonData = JSON.parse(updatedData.data);
          let newPosition = jsonData.payload;
          console.log("position websocket return", newPosition);
          let index = positions.findIndex((position) => {
            return position.account == newPosition.account && position.stock_ticker == newPosition.stock_ticker;
          });
          if (index > -1) {
            positions[index] = newPosition;
          } else {
            positions.push(newPosition);
          }
          rowData = [];
          populateRowData();
          if (gridOptions !== undefined && gridOptions.api) {
            gridOptions.api.setRowData(rowData);
          }
        }
      } else {
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
    --ag-header-foreground-color:  #98bfca;
    --ag-border-color: #98bfca;
    --ag-header-background-color: #202020;
    --ag-background-color: #202020;
    --ag-selected-row-background-color: #95C3B5 ;
    /* --ag-odd-row-background-color: none; */
  }
  /* :global(.ag-header-cell) {
    font-size: 12px;
    font-style: normal;
    font-family: Roboto;
  }  */
</style>
