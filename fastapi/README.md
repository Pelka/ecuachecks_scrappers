# My FastAPI App

This is a basic API built with FastAPI. It includes features such as calling an external API, user authentication, and WebSocket connections.

## Installation

1. Clone this repository.
2. Install the required packages with `pip install -r requirements.txt`.
3. Set the necessary environment variables in the `.env` file.

## Usage

Run the application with `uvicorn app.main:app --reload`.

The API has the following endpoints:

- `/api/external`: Calls an external API and returns the response.
- `/api/auth/login`: Authenticates a user.
- `/api/auth/logout`: Logs out a user.
- `/ws`: Accepts WebSocket connections.

## Testing

Run the tests with `pytest`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)