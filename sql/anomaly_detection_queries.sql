-- 1) Doublons d'inscription
SELECT
    'DUPLICATE_REGISTRATION' AS alert_type,
    national_id AS business_key,
    COUNT(*) AS duplicate_count,
    STRING_AGG(student_id, ', ') AS impacted_students
FROM students
GROUP BY national_id
HAVING COUNT(*) > 1;

-- 2) Paiements marqués payés sans trace cohérente
SELECT
    'PAID_WITHOUT_TRACE' AS alert_type,
    payment_id,
    student_id,
    amount,
    receipt_id,
    payment_status
FROM payments
WHERE payment_status = 'PAID'
  AND (COALESCE(receipt_id, '') = '' OR amount <= 0);

-- 3) Notes manquantes ou incohérentes
SELECT
    'GRADE_ANOMALY' AS alert_type,
    student_id,
    course_code,
    semester,
    grade
FROM grades
WHERE grade IS NULL
   OR grade < 0
   OR grade > 20;

-- 4) Paiements orphelins
SELECT
    'ORPHAN_PAYMENT' AS alert_type,
    p.payment_id,
    p.student_id,
    p.amount,
    p.payment_date
FROM payments p
LEFT JOIN students s ON s.student_id = p.student_id
WHERE s.student_id IS NULL;

-- 5) Écarts inter-systèmes (centre de coût vs département attendu)
WITH student_expected AS (
    SELECT
        student_id,
        department_code,
        CASE department_code
            WHEN 'INFO' THEN 'CC-INFO'
            WHEN 'FIN' THEN 'CC-FIN'
            WHEN 'RH' THEN 'CC-RH'
            WHEN 'MKT' THEN 'CC-MKT'
            ELSE 'CC-UNKNOWN'
        END AS expected_cost_center
    FROM students
)
SELECT
    'CROSS_SYSTEM_GAP' AS alert_type,
    f.transaction_id,
    f.student_id,
    se.department_code,
    se.expected_cost_center,
    f.cost_center
FROM finance_transactions f
LEFT JOIN student_expected se ON se.student_id = f.student_id
WHERE COALESCE(se.expected_cost_center, 'CC-UNKNOWN') <> f.cost_center;

-- 6) Transactions inhabituelles - montant élevé
SELECT
    'UNUSUAL_TRANSACTION' AS alert_type,
    transaction_id,
    student_id,
    amount,
    transaction_date
FROM finance_transactions
WHERE amount > 1000000;

-- 7) Transactions inhabituelles - doublons même jour / même montant
SELECT
    'UNUSUAL_TRANSACTION_DUP' AS alert_type,
    student_id,
    transaction_date,
    amount,
    COUNT(*) AS duplicate_count,
    STRING_AGG(transaction_id, ', ') AS duplicated_transactions
FROM finance_transactions
GROUP BY student_id, transaction_date, amount
HAVING COUNT(*) >= 2;
