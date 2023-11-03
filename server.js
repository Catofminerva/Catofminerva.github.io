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
const sqlite3 = require('sqlite3').verbose();

const app = express();
const server = http.createServer(app);

// Initialize a SQLite database file
const db = new sqlite3.Database('./chat_history.db', (err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
  });
  

// Initialize the chat history table
db.run('CREATE TABLE chat_history (message TEXT)');

// Function to load the chat history from the database
const loadChatHistory = (callback) => {
  db.all('SELECT message FROM chat_history', [], (err, rows) => {
    if (err) {
      throw err;
    }
    callback(rows.map(row => row.message));
  });
};

// Function to save a message to the database
const saveMessage = (message) => {
  db.run('INSERT INTO chat_history (message) VALUES (?)', [message], (err) => {
    if (err) {
      return console.log(err.message);
    }
    // Message saved to the database
  });
};

// Initialize a WebSocket server
const wss = new WebSocket.Server({ server });

// Function to broadcast messages to all clients
const broadcastMessage = (message) => {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
};

// Set up the WebSocket connection
wss.on('connection', (ws) => {
    // Send the chat history to the client upon connection
    loadChatHistory((history) => {
        ws.send(JSON.stringify(history));
    });

// When the client sends a message
ws.on('message', (message) => {
    if (message === 'request-chat-history') {
        // Client requested chat history
        loadChatHistory((history) => {
            // Send the chat history to the requesting client only
            ws.send(JSON.stringify({ type: 'history', data: history }));
        });
    } else {
        // Store the message in the database
        saveMessage(message);
        // Broadcast the message to all clients
        broadcastMessage(JSON.stringify({ type: 'message', data: message }));
    }
});


// Start the server
server.listen(8080, () => {
    console.log('Server is listening on port 8080');
});

// Close the SQLite database on server stop
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Close the database connection.');
    process.exit();
  });
});


  

console.log('WebSocket server is running on ws://localhost:8080');
