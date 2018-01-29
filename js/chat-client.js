function addMessage(text, className) {
    let node = document.getElementById("messages"),
        message = document.createElement("div"),
        wrapper = document.createElement("div");
    wrapper.className = className;
    message.appendChild(document.createTextNode(text));
    wrapper.appendChild(message);
    node.appendChild(wrapper);
}

function sendMessage() {
    let node = document.getElementById("message-input");
    addMessage(node.value, "message-right");
    connection.send(node.value);
    node.value = "";
}

function init() {
    connection = new WebSocket("ws://localhost:9876");
    connection.onopen = function () {
        connection.send("I HAVE CONNECTED");
    };

    connection.onerror = function (error) {
        console.log(error);
    };

    connection.onmessage = function (e) {
        console.log("Server: " + e.data);
        addMessage(e.data, "message-left");
    };

    document.getElementById("send").addEventListener("click", sendMessage);
    document.getElementById("message-input").addEventListener("keydown", function (e) {
        if (e.key === "Enter") sendMessage();
    });
}

window.addEventListener("load", init);
