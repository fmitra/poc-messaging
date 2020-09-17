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
socket on receipt. A pub/sub broker ensures that regardless of where a client
connects, we can deliver messages.

### Other Concerns

These items are not covered in this POC, but depending on your application's
needs, you should take into consideration the following:

1. Depending on the use-case, clients may need access to older/undelivered
messages for proper UX. Messages should be timestamped, stored, and queryable
if this is required.

2. Delivered messages should be structured and convey meaning. A good
example is the [Slack API](https://api.slack.com/rtm) which implement's a `type` parameter
as opposed to enabling multiple websocket APIs to deliver different messages.

3. You will want to budget for a [thundering herd of client reconnections](https://centrifugal.github.io/centrifugo/blog/scaling_websocket/) should
a service go down. Common solutions for this include exponential backoff
implemented on the client and rate limiting.

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
