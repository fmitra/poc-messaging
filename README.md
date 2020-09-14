# POC Messaging

POC to demonstrate how to set up a websockets API for distrubuted applications.

## Overview

Purpose of this project is to demonstrate basic scaffolding for a websocket
API, such as connection management and authentication.

1. Authentication: We introduce a short lived token for authentication as
browser support for passing headers on the websocket handshake may prevent
a authentication headers from being sent. A single use or short lived token
that is separate from the user's primary authentication token is appropriate.
Here we use a JWT token with 1-minute expiry.

2. Messsaging: Redis Pub/Sub is used to deliver messages. Applications store
open sockets in memory, grouped by a username and listen to incoming messages.
An application tracking a specific user then forwards the message down the
socket on receipt.

## Backend

Backend development server is available at `http://localhost:8080`

```
cd messaging
docker-compose -f docker-compose.test.yml up
make dev
pip install -r requirements_dev.txt
python -m messaging
```

## Frontend

To start and access the client application, run the following:

```
cd web
nvm use
npm install
npm run config:dev
npx npm run start
```

Client application will be available at `http://localhost:4000`

## Auditing

1. Start up the backend and frontend applications using the instructions above
2. Follow the UI instructions to open a websocket with any username
3. In a separate window/tab/browser, open the webapp and connect using the
same username from `step 2`
3. Submit a message to your username using the command below. Messages should
show up on all open web apps.

```
curl -X POST -d '{"username":"test-user","content":"hi there"}' http://localhost:8080/message
```
