package main

import (
	"fmt"
	"net/http"
	"sync"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

// Map user IDs to their WebSocket connections
var clients = make(map[string]*websocket.Conn)
var mu sync.Mutex

func handleConnections(w http.ResponseWriter, r *http.Request) {
	// Simple identifier for testing (in production, use your JWT logic here)
	userID := r.URL.Query().Get("id")
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil { return }
	defer ws.Close()

	mu.Lock()
	clients[userID] = ws
	mu.Unlock()

	fmt.Printf("User %s connected\n", userID)

	for {
		var msg map[string]interface{}
		err := ws.ReadJSON(&msg)
		if err != nil { break }

		// Route the message to the target_id
		targetID := msg["target_id"].(string)
		mu.Lock()
		if targetConn, ok := clients[targetID]; ok {
			targetConn.WriteJSON(msg)
		}
		mu.Unlock()
	}
}

func main() {
	http.HandleFunc("/ws", handleConnections)
	fmt.Println("🚀 Signaling Server running on :8081")
	http.ListenAndServe(":8081", nil)
}