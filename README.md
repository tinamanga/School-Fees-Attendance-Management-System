1. Once you've cloned the repo, Open your terminal and run: 
    cd School-Fees-Attendance-Management-System

2. Create and Activate a Virtual Environment:

    # Create virtual environment (called .venv)
       RUN: python3 -m venv .venv

    # Activate the virtual environment
       RUN: source .venv/bin/activate

3. Install Dependencies.
        RUN:
    pip install --upgrade pip
    pip install -r requirements.txt

4. Initialize the Database.

        flask db init        # (Run only once, skip if migrations/ exists)
        flask db migrate -m "Initial migration"
        flask db upgrade

5. Seed the Database with Default Users.
            RUN:
        python seed.py

-  This will create: 
        Default Admin: name-admin / Password-admin123
        Default Teacher: name-teacher1 / Password-teacher123
        Default Student: name-student1 / Password-student123 

6. Start the Backend Server.
            RUN:
        flask run

    Default URL: http://localhost:5000


7. API Endpoints (Examples)

        POST /login — User authentication

        GET /students — All students (admin/teacher)

        GET /students/<id> — Student profile and data

        POST /fee-payments — Submit student fee payment

        POST /attendance-records/bulk-weekly — Record weekly attendance (admin/teacher)


8.  Useful Commands.

        Re-run seed script - python seed.py

        Create a migration - flask db migrate -m "message"

        Apply migration -   flask db upgrade

        Run development - flask run

        Reset DB (optional) - Delete migrations/ and .db file, then rerun migrations and seed