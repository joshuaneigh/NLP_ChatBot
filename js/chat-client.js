// #!javascript
//
// var http = require('http');
// http.createServer(function (req, res) {
//     res.writeHead(200, {'Content Type': 'text/plain'});
//     res.write('Hello World!');
//     res.end();
// }).listen(8080);

let connection = new WebSocket("ws://localhost:9876");

connection.onopen = function () {
    connection.send("I HAVE CONNECTED");
};

connection.onerror = function (error) {
    console.log(error);
};

connection.onmessage = function (e) {
    console.log("Server: " + e.data);
};

document.getElementById("send").addEventListener("click", function () {
    connection.send(document.getElementById("message").value);
});
