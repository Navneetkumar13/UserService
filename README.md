# User Service

Description:
This service is a part of another microservice PostService which uses the same the SQL Database as the PostService and communicates with the microservice PostService for the operations. It uses Docker for containerisation. You can refer LLD Class-Diagram for better underating of the microservices flow that is present in the repo

Use Cases:
1. Login/Signup user through JWT token
2. Update user details
3. Delete a user
4. Search users by name
5. Follow other users
6. Get a user by username
7. List all users

Tech Stack:
1. It is build on Python and the framework used is Django-Rest-FrameWork.
2. For the Database it is using PostgreSQL Database
3. It also contains Dockerfile through which this service can be containerised

Steps to run the django service:
1. Clone the repo using git clone url
2. Create a Virtual Environment using following command: python -m venv env
3. Activate the environment: source env/bin/activate
4. Install all the requirements in the env. Locate the directory where requirement.txt file is located and run command: pip install -r requirements.txt
5. It uses Sql DB PostgreSql so create .env file define the database properties. For reference you can refer the dummy .env file in the code.
6. After creating Postgresql database and defining all the properties you have to make mirations. Goto where manage.py file is located and run command: python manage.py makemigrations
7. After that run: python manage.py migrate
8. Then you are ready to run the django application: python manage.py runserver
