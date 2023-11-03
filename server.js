// Import WebSocket library
const WebSocket = require('ws');

// Initialize a WebSocket server
const wss = new WebSocket.Server({ port: 8080 });

// Broadcast to all clients
const broadcast = (data) => {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(data);
        }
    });
};


const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let chatHistory = []; // This will store the chat history

wss.on('connection', function connection(ws) {
  // Send the chat history to the client
  ws.send(JSON.stringify(chatHistory));

  ws.on('message', function incoming(message) {
    // Store message in chatHistory
    chatHistory.push(message);
    // Broadcast to all clients
    wss.clients.forEach(function each(client) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  });
});

server.listen(8080, function listening() {
  console.log('Listening on %d', server.address().port);
});


// Set up the WebSocket connection
wss.on('connection', (ws) => {
    console.log('New client connected!');

    // Send a welcome message to the connected client
    ws.send('Welcome to the chat!');

    // Set up a response when a message is received
    ws.on('message', (message) => {
        console.log(`Received: ${message}`);
        // Broadcast the message to all clients
        broadcast(message);
    });

    // Handle when a client disconnects
    ws.on('close', () => {
        console.log('Client has disconnected.');
    });
});

console.log('WebSocket server is running on ws://localhost:8080');
