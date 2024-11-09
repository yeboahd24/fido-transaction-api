# Fido Transaction API

This is a simple API for managing transactions in a database. It uses FastAPI and PostgreSQL as the database and Redis as the cache. 


NB: All requests are authenticated using JWT tokens. The API is secured by default

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 16 or higher
- Redis

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yeboahd24/fido-transaction-api.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add the following environment variables:

```bash
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
ENCRYPTION_KEY=your_encryption_key
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
```

Replace `your_encryption_key`, `your_jwt_secret_key`, and `your_jwt_algorithm` with your own values.

4. Create the database and tables:

```bash
python manage.py create_db
```

5. Run the application:

```bash
uvicorn app.main:app --reload
```

## Usage

### Registering a user

To register a new user, send a POST request to the `/auth/register` endpoint with the following JSON payload:

```json
{
  "username": "your_username",
  "email": "your_email",
  "password": "your_password"
}
```

### Logging in

To log in a user, send a POST request to the `/auth/login` endpoint with the following JSON payload:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

The response will contain the access token and other relevant information.

### Creating a transaction

To create a new transaction, send a POST request to the `/transactions` endpoint with the following JSON payload:

```json
{
  "full_name": "John Doe",
  "transaction_date": "2023-01-01",
  "transaction_amount": 100.0,
  "transaction_type": "credit"
}
```

The response will contain the transaction details, including the ID, full name, transaction date, transaction amount, and transaction type.

### Updating a transaction

To update a transaction, send a PUT request to the `/transactions/{transaction_id}` endpoint with the following JSON payload:

```json
{
  "full_name": "Jane Doe",
  "transaction_date": "2023-02-01",
  "transaction_amount": 200.0,
  "transaction_type": "debit"
}
```

The response will contain the updated transaction details, including the ID, full name, transaction date, transaction amount, and transaction type.

### Deleting a transaction

To delete a transaction, send a DELETE request to the `/transactions/{transaction_id}` endpoint.

The response will contain a success message.

### Getting user analytics

To get user analytics, send a GET request to the `/analytics` endpoint.

The response will contain the user's analytics data, including the full name, total transactions, total credit, total debit, average transaction value, and the busiest day.


## Docker

To run the application using Docker, follow these steps:

1. Build the Docker image:

```bash
docker-compose build
```

2. Run the Docker container:

```bash
docker-compose up -d
```
You can run the tests with Docker Compose using the command:
```bash
docker-compose up --abort-on-container-exit --exit-code-from test test
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.
