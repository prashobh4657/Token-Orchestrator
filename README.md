# Token-Orchestrator

## Problem Statement

Design a server capable of generating, assigning, and managing API keys with specific functionalities. The server should offer various endpoints for interaction:

### Endpoints

1. **Create New Keys**
   - **Endpoint:** `POST /keys`
   - **Description:** Generate new keys.
   - **Status:** 201

2. **Retrieve an Available Key**
   - **Endpoint:** `GET /keys`
   - **Description:** Retrieve an available key for client use, ensuring the key is randomly selected and not currently in use. This key should then be blocked from being served again until its status changes. If no keys are available, a 404 error should be returned.
   - **Status:** 200 / 404
   - **Response:** `{ "keyId": "<keyID>" } / {}`

3. **Provide Information About a Specific Key**
   - **Endpoint:** `GET /keys/:id`
   - **Description:** Provide information (e.g., assignment timestamps) about a specific key.
   - **Status:** 200 / 404
   - **Response:**
     ```json
     { 
       "isBlocked" : "<true> / <false>", 
       "blockedAt" : "<blockedTime>", 
       "createdAt" : "<createdTime>" 
     } / {}
     ```

4. **Remove a Specific Key**
   - **Endpoint:** `DELETE /keys/:id`
   - **Description:** An endpoint to permanently remove a key from the system. Remove a specific key, identified by :id, from the system.
   - **Status:** 200 / 404

5. **Unblock a Key for Further Use**
   - **Endpoint:** `PUT /keys/:id`
   - **Description:** An endpoint to unblock a previously assigned key, making it available for reuse. Unblock a key for further use.
   - **Status:** 200 / 404

6. **Key Keep-Alive Functionality**
   - **Endpoint:** `PUT /keepalive/:id`
   - **Description:** An endpoint for key keep-alive functionality, requiring clients to signal every 5 minutes to prevent the key from being deleted. Signal the server to keep the specified key, identified by :id, from being deleted.
   - **Status:** 200 / 404

### Constraints

- Each generated key has a life of 5 minutes after which it gets deleted automatically if the keep-alive operation is not run for that key.
- Automatically release blocked keys within 60 seconds if not unblocked explicitly.
- Ensuring efficient key management without the need to iterate through all keys for any operation. The complexity of endpoint requests should be aimed at O(log n) or O(1) for scalability and efficiency.
