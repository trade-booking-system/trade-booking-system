<svelte:head>
	<script src="https://unpkg.com/ag-grid-community/dist/ag-grid-community.min.noStyle.js"></script>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@29.0.0/styles/ag-grid.css" />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@29.0.0/styles/ag-theme-alpine.css"/>
</svelte:head>

<script>
  import { Grid } from 'ag-grid-community';
	import {onMount, onDestroy} from 'svelte'

	let gridContainer
	let grid


	const columnDefs = [
		{ field: "Account" },
		{ field: "TradeID" },
        { field: "Date" },
        { field: "Time" },
        { field: "Ticker" },
		{ field: "Price" }
	];

    const defaultColDef = {
        resizable: true,
    }

	const rowData = [
		{Account: "Account 1", TradeID: "0001", Date: "01/01/2023", Time: 12, Ticker : "ama", Price : "$100"},
		{Account: "Account 2", TradeID: "0002", Date: "01/01/2023", Time: 12,  Ticker : "ama", Price : "$100"},
		{Account: "Account 3", TradeID: "0003", Date: "01/01/2023", Time: 12,  Ticker : "ama", Price : "$100"}
	];

	const gridOptions = {
        defaultColDef: defaultColDef,
		columnDefs: columnDefs,
		rowData: rowData,
		
	};

    function sizeToFit(){
        gridOptions.api.sizeColumnsToFit({
            defaultMinWidth: 100,
        })
    }

	onMount(() => {
		window.addEventListener('resize', sizeToFit); //handles auto resizing
		grid = new Grid(gridContainer, gridOptions);
        sizeToFit()
	})

	 onDestroy(() => {
		window.removeEventListener('resize', sizeToFit);
    if (grid) {
      grid.destroy();
    }
  });

</script>

<div id="datagrid" class="ag-theme-alpine-dark" style="height: 50vh; width:80vw;" bind:this={gridContainer}></div>

<style>
	#datagrid {
		--ag-header-foreground-color: orangered;
	}	
	:global(.ag-header-cell) {
		font-size: 16px;
	}
</style>