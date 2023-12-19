# Ecuachecks API

This is a basic API built with FastAPI. It includes features such as calling an external API, user authentication, and WebSocket connections.

## Installation

1. Clone this repository.
2. Install the required packages with `pip install -r requirements.txt`.
3. Set the necessary environment variables in the `.env` file.

## Usage
The API has the following endpoints:

- `/api/external`: Calls an external API and returns the response.
- `/api/auth/login`: Authenticates a user.
- `/api/auth/logout`: Logs out a user.
- `/ws`: Accepts WebSocket connections.

