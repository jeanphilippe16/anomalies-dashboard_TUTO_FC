CREATE TABLE students (
    student_id VARCHAR,
    national_id VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    program VARCHAR,
    department_code VARCHAR,
    level VARCHAR,
    registration_date DATE,
    tuition_expected BIGINT,
    enrollment_status VARCHAR,
    advisor_id VARCHAR
);

CREATE TABLE payments (
    payment_id VARCHAR,
    student_id VARCHAR,
    fee_type VARCHAR,
    payment_date DATE,
    amount BIGINT,
    currency VARCHAR,
    payment_method VARCHAR,
    receipt_id VARCHAR,
    payment_status VARCHAR,
    entered_by VARCHAR
);

CREATE TABLE grades (
    student_id VARCHAR,
    course_code VARCHAR,
    course_name VARCHAR,
    semester VARCHAR,
    grade DOUBLE,
    grade_status VARCHAR,
    updated_at DATE
);

CREATE TABLE hr_staff (
    staff_id VARCHAR,
    staff_name VARCHAR,
    role VARCHAR,
    department_code VARCHAR,
    cost_center VARCHAR,
    active_flag INTEGER
);

CREATE TABLE finance_transactions (
    transaction_id VARCHAR,
    student_id VARCHAR,
    payment_id VARCHAR,
    transaction_date DATE,
    amount BIGINT,
    direction VARCHAR,
    ledger_account VARCHAR,
    cost_center VARCHAR,
    transaction_type VARCHAR,
    entered_by VARCHAR
);

-- DuckDB quick load examples:
-- COPY students FROM 'data/students.csv' (AUTO_DETECT TRUE, HEADER TRUE);
-- COPY payments FROM 'data/payments.csv' (AUTO_DETECT TRUE, HEADER TRUE);
-- COPY grades FROM 'data/grades.csv' (AUTO_DETECT TRUE, HEADER TRUE);
-- COPY hr_staff FROM 'data/hr_staff.csv' (AUTO_DETECT TRUE, HEADER TRUE);
-- COPY finance_transactions FROM 'data/finance_transactions.csv' (AUTO_DETECT TRUE, HEADER TRUE);
