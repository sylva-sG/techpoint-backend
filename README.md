# POS Flask Backend Starter

## Requirements
Python 3.10+ and PostgreSQL.

# Python Virtual Environment and PostgreSQL Setup (Ubuntu/WSL)

## 1. Open your project directory

```bash
cd ~/Python/your-project
```# Python Virtual Environment and PostgreSQL Setup (Ubuntu/WSL)

## 1. Open your project directory

```bash
cd ~/Python/your-project
```

Replace `your-project` with your actual project folder.

## 2. Create and activate the virtual environment

Run this only if the environment does not already exist:

```bash
python3 -m venv venv
source venv/bin/activate
```

If the environment already exists, activate it with:

```bash
source venv/bin/activate
```

## 3. Install project dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install PostgreSQL

Run this only if PostgreSQL is not already installed:

```bash
sudo apt update
sudo apt install postgresql 
```

Check the installation:

```bash
psql --version
```

## 5. Start PostgreSQL and check its status

```bash
sudo service postgresql start
sudo service postgresql status
```

### 6. Check weather PostgresSQL is accepting connections

```bash
pg_isready -h localhost -p 5432
```

### 7. Create User with password

```bash
sudo -u postgres createuser --pwprompt username1 # replace username1 with your username and enter password for your user
```

## 8. Create database
```bash
sudo -u postgres createdb --owner=username1 database # replace username1 with your username and replace database with name of your database
```

## 9. Open the PostgreSQL terminal to interact with your database

```bash
psql -h localhost -u username1 -d database #replace username1 with your user and database with name of your database
```

Useful commands inside `psql`

```sql
\l      -- List databases
\du     -- List users/roles
\dt     -- List tables in the current database
\q      -- Exit psql
```

Exit with `\q`.

A typical database URL for a Python app is:

```text
postgresql://myproject_user:YOUR_PASSWORD@localhost:5432/myproject_db
```

Keep real credentials in a local `.env` file or environment variables. Do not commit passwords, API keys, or `.env` files to Git.

## Quick command checklist

```bash
cd ~/Moringa/Python/your-project
source venv/bin/activate
pip install -r requirements.txt
sudo service postgresql start
sudo service postgresql status
sudo -u postgres psql

**Note:** The `venv` and PostgreSQL installation commands are only needed if those components do not already exist. Replace all example project, database, and username values with your team's actual values.


Replace `your-project` with your actual project folder.

## 2. Create and activate the virtual environment

Run this only if the environment does not already exist:

```bash
python3 -m venv venv
source venv/bin/activate
```

If the environment already exists, activate it with:

```bash
source venv/bin/activate
```

## 3. Install project dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install PostgreSQL

Run this only if PostgreSQL is not already installed:

```bash
sudo apt update
sudo apt install postgresql 
```

Check the installation:

```bash
psql --version
```

## 5. Start PostgreSQL and check its status

```bash
sudo service postgresql start
sudo service postgresql status
```

### 6. Check weather PostgresSQL is accepting connections

```bash
pg_isready -h localhost -p 5432
```

### 7. Create User with password

```bash
sudo -u postgres createuser --pwprompt username1 # replace username1 with your username and enter password for your user
```

## 8. Create database
```bash
sudo -u postgres createdb --owner=username1 database # replace username1 with your username and replace database with name of your database
```

## 9. Open the PostgreSQL terminal to interact with your database

```bash
psql -h localhost -u username1 -d database #replace username1 with your user and database with name of your database
```

Useful commands inside `psql`

```sql
\l      -- List databases
\du     -- List users/roles
\dt     -- List tables in the current database
\q      -- Exit psql
```

Exit with `\q`.

A typical database URL for a Python app is:

```text
postgresql://myproject_user:YOUR_PASSWORD@localhost:5432/myproject_db
```

Keep real credentials in a local `.env` file or environment variables. Do not commit passwords, API keys, or `.env` files to Git.

## Quick command checklist

```bash
cd ~/Moringa/Python/your-project
source venv/bin/activate
pip install -r requirements.txt
sudo service postgresql start
sudo service postgresql status
sudo -u postgres psql
```

**Note:** The `venv` and PostgreSQL installation commands are only needed if those components do not already exist. Replace all example project, database, and username values with your team's actual values.
