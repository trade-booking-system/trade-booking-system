<script>
    const ws = new WebSocket("ws://" + window.location.hostname + "/api/ws");
    ws.onopen = (event) => {
        ws.send("Here's some text that the server is urgently awaiting!");
    };
    ws.onmessage = (event) => {
        document.getElementById("text").textContent = event.data;
    }
</script>

<h1 id="text">

</h1>