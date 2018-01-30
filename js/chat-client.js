DEFAULT_ERROR = 'Error:  Server connection closed. Is it running?';

function addMessage(text, className) {
    let node = document.getElementById("messages"),
        message = document.createElement("div"),
        wrapper = document.createElement("div");
    wrapper.className = className;
    message.appendChild(document.createTextNode(text));
    wrapper.appendChild(message);
    node.appendChild(wrapper);
}

function alert(message) {
    let alert = document.createElement("div"),
        closeButton = document.createElement("span"),
        closeFunction = function () {
            alert.style.opacity = "0";
            setTimeout(function () {
                document.body.removeChild(alert);
            }, 600);
        };

    closeButton.className = "closeButton";
    alert.className = "alert";
    closeButton.appendChild(document.createTextNode("\u00D7"));
    closeButton.addEventListener("click", closeFunction);
    alert.appendChild(closeButton);
    alert.appendChild(document.createTextNode(message || DEFAULT_ERROR));
    document.body.appendChild(alert);
    setTimeout(closeFunction, 4000);
}

function sendMessage() {
    let node = document.getElementById("message-input");
    if (node.value.length > 0) {
        addMessage(node.value, "message-right");
        connection.send(node.value);
        node.value = "";
    }
}

function promptName() {
    let prompt = document.createElement("div"),
        title = document.createElement("h3"),
        input = document.createElement("input")
        submit = document.createElement("button"),
        submitFunction = function() {
            if (input.value) {
                connection.send(input.value);
                document.cookie = "username=" + input.value;
                document.body.removeChild(prompt);
            }
        }

    prompt.className = "name-prompt";
    input.placeholder = "Your name..."
    submit.addEventListener("click", submitFunction);
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") submitFunction();
    });
    title.appendChild(document.createTextNode("Welcome!"));
    submit.appendChild(document.createTextNode("Submit"));
    prompt.appendChild(title);
    prompt.appendChild(input);
    prompt.appendChild(submit);
    document.body.appendChild(prompt);
}

function getCookie(name) {
    let value = "; " + document.cookie,
        parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function onOpen() {
    // TODO: Get name from cookie if it exists
    name = getCookie("username");
    if (name !== "undefined") connection.send(name);
    else promptName();

}

function onClose(e) {
    alert(e.reason);
}

function onMessage(e) {
    addMessage(e.data, "message-left");
}

function init() {
    // window.onerror = function() {return true;}; // Uncomment when published
    connection = new WebSocket("ws://localhost:9876");
    connection.onopen = onOpen;
    connection.onclose = onClose;
    connection.onmessage = onMessage;

    document.getElementById("send").addEventListener("click", sendMessage);
    document.getElementById("message-input").addEventListener("keydown", function (e) {
        if (e.key === "Enter") sendMessage();
    });
}

window.addEventListener("load", init);
