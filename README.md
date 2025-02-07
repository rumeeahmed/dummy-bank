# Dummy Bank App

A simple banking application that allows users to create accounts, make transfers, 
check balances and add or update their addresses.

## Features

- Create, update and list customers
- Create and list accounts.
- Deposit, withdraw and transfer funds.
- Create, update and list addresses with automatic address coordinate generation using 
Google API.

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy
- **Deployment:** Docker, Docker Compose

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL
- Docker & Docker Compose
- Just
- Poetry

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/rumeeahmed/dummy-bank.git
   cd dummy-bank-app
   ```
2. Create a virtual environment and install dependencies:
   ```sh
   just install
   ```
3. Configure environment variables in a .env file:
   ```
   DB_HOST=localhost
   DB_USER=service
   DB_NAME=service
   DB_PASS=service
   DB_PORT=5432
   GOOGLE_API_URL=https://maps.googleapis.com
   GOOGLE_API_KEY=API_KEY
   ```
4. Run docker:
   ```sh
   just up
   ```
5. Make the local db migration:
   ```sh
   just db-upgrade
   ```
6. Run the application:
   ```shell
      just run_api
   ```
7. API documentation available at `http://localhost:8080/docs`
after running the app.

## Testing

Run tests using:
```sh
  just test
```