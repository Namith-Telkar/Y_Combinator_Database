# Database Design - Final Project

This is the final project for DB Design - Z511 FA2024

### Data Preprocessing

The data for this project was obtained from [Kaggle](https://www.kaggle.com/datasets/sashakorovkina/ycombinator-all-funded-companies-dataset). Following were the preprocessing steps:

    1. The schools.csv had a few NaN values which didn't relate to any of the other rows in other tables of the database and hence were removed

    2. The prior_companies.csv also had a few NaN values which were removed for the same reason as above

    3. school.csv had all the years from start year to end year for each founder. Since the duration is irrelevant for the scope of this project and we are concerned with only the year that a founder graduated from a particular school, only the latest year for each school of each founder was considered and rest was removed

    4. Surprisingly, there were few founders in the founders.csv who didn't have any corresponding company in companies.csv. Thus those founders were removed and consequently the rows from related to those founders in prior_companies.csv and schools.csv were also removed.

## Run Locally

Clone the project

```bash
    git clone https://github.iu.edu/ntelkar/DB_Design_Project.git
```

Install necessary python libraries

```bash
    pip install -r requirements.txt
```

Create a .env file and add database credentials

```bash
    DB_HOST="db.luddy.indiana.edu"
    DB_USER="<your_username>"
    DB_PASSWORD="<your_password>"
    DB="<your_db>"
```

Run main.py which will initialize the database and add all the data entries. (Heads up: This script will take close to an hour to run)

```bash
  python3 main.py
```

Finally run queries.py which will run all the queries and display the results in table format in the command line.

```bash
  python3 queries.py
```
