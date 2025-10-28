# Introduction

The PIRO Airflow application is an implementation of scheduled jobs for the PIRO application using the [Apache Airflow](https://airflow.apache.org/) job scheduling tool.

## Getting Started

git clone [repository url]
python -m venv env   #create a virtual environment (First time only)

pip install -r .\requirements.txt

.\env\Scripts\activate  #activate your virtual environment

Update the localhost_debugging.py with the function to be executed and pass the parameters
py .\localhost_debugging.py
