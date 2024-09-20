import asyncio
import websockets
import json
from cryptography.fernet import Fernet

# Generate an encryption key (shared between clients and server)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

clients = set()

async def handle_client(websocket, path):
    # Register client
    clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            # Decrypt message
            decrypted_message = cipher_suite.decrypt(message.encode()).decode()
            print(f"Received: {decrypted_message}")

            # Broadcast the encrypted message to all clients
            for client in clients:
                if client != websocket:
                    encrypted_message = cipher_suite.encrypt(decrypted_message.encode())
                    await client.send(encrypted_message.decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Unregister client
        clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

# Start the WebSocket server
async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("Server started on port 8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
