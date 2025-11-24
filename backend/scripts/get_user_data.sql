-- Get all columns and types from users table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Get the specific user's data
SELECT * FROM users WHERE email = 'oadatascientist@gmail.com';

-- Get all columns from user_credits
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'user_credits' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Try to find user_credits record by the UUID we know
SELECT * FROM user_credits WHERE user_id = '92f3f140-ddb5-4e21-a6d7-814982b55ebc'::uuid;
