<script>
    const ws = new WebSocket("ws://" + window.location.hostname + "/api/ws/ws");
    ws.onmessage = (event) => {
        document.getElementById("text").textContent = event.data;
    }
</script>

<h1 id="text">

</h1>