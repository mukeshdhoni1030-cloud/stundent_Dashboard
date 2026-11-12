
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import engine
import uuid


def run_constraint_test(connection, name, test_function):
    savepoint = connection.begin_nested()

    try:
        test_function(connection)

        # The invalid operation was accepted.
        # Roll it back so no test data remains.
        savepoint.rollback()

        print(f"FAIL: {name} - Database accepted invalid data")

    except IntegrityError:
        # Expected: PostgreSQL rejected the invalid operation.
        savepoint.rollback()
        print(f"PASS: {name} - Invalid data rejected")

    except Exception:
        savepoint.rollback()
        raise


def duplicate_email(connection):
    connection.execute(text("""
        INSERT INTO users (email, password_hash, role)
        SELECT email, password_hash, role
        FROM users
        LIMIT 1
    """))


def duplicate_student_roll(connection):
    temporary_email = f"db-test-{uuid.uuid4().hex}@example.com"

    result = connection.execute(
        text("""
            INSERT INTO users (email, password_hash, role)
            VALUES (:email, 'temporary-test-hash', 'student')
            RETURNING id
        """),
        {"email": temporary_email}
    )

    new_user_id = result.scalar()

    connection.execute(text("""
        INSERT INTO students (user_id, class_id, name, roll_no)
        SELECT :user_id, class_id, name, roll_no
        FROM students
        LIMIT 1
    """), {"user_id": new_user_id})


def duplicate_student_attendance(connection):
    connection.execute(text("""
        INSERT INTO student_attendance (student_id, date, status)
        SELECT student_id, date, status
        FROM student_attendance
        LIMIT 1
    """))


def duplicate_teacher_attendance(connection):
    connection.execute(text("""
        INSERT INTO teacher_attendance (teacher_id, date, status)
        SELECT teacher_id, date, status
        FROM teacher_attendance
        LIMIT 1
    """))


def invalid_marks(connection):
    connection.execute(text("""
        INSERT INTO marks (
            student_id, exam_id, subject_id,
            marks_obtained, max_marks
        )
        SELECT
            student_id, exam_id, subject_id, 101, 100
        FROM marks
        LIMIT 1
    """))


def invalid_fees(connection):
    connection.execute(text("""
        INSERT INTO fees (student_id, total_fee, paid_amount)
        SELECT student_id, 100, 101
        FROM fees
        LIMIT 1
    """))


def duplicate_teacher_salary(connection):
    connection.execute(text("""
        INSERT INTO salaries (teacher_id, salary_month, amount)
        SELECT teacher_id, salary_month, amount
        FROM salaries
        LIMIT 1
    """))


def main():
    tests = [
        ("Duplicate user email", duplicate_email),
        ("Duplicate student roll number", duplicate_student_roll),
        ("Duplicate student attendance", duplicate_student_attendance),
        ("Duplicate teacher attendance", duplicate_teacher_attendance),
        ("Marks greater than maximum marks", invalid_marks),
        ("Paid fees greater than total fees", invalid_fees),
        ("Duplicate teacher salary", duplicate_teacher_salary),
    ]

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            print("\nDATABASE CONSTRAINT TESTING")
            print("===========================")

            for name, test_function in tests:
                try:
                    run_constraint_test(
                        connection,
                        name,
                        test_function
                    )
                except Exception as error:
                    print(f"CHECK ERROR: {name}")
                    print(error)

            # Roll back the entire testing transaction.
            transaction.rollback()

            print("\nDATABASE TESTING COMPLETED")
            print("All test changes have been rolled back.")

        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise


if __name__ == "__main__":
    main()
