# POC Messaging

Proof of concept to demonstrate the use of websockets for messaging

## Overview

Purpose of this project is to demonstrate basic scaffolding for a websocket
API, such as connection management and authentication.

## Backend

Backend development server is available at `http://localhost:8080`

```
cd messaging
pip install -r requirements_dev.txt
python -m messaging
```

Pytest is used for testing:

```
pytest tests/
```

## Frontend

To start and access the client application, run the following:

```
cd web
nvm use
npm install
npx npm run start
```

Client application will be available at `http://localhost:4000`

Jest is used for testing:

```
npx npm run test
npx npm run lint
```
