-- Get full structure of user_credits table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_credits' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Get the user's record from users table
SELECT * FROM users WHERE email = 'oadatascientist@gmail.com';

-- Get the user's credit record (user_id is UUID)
SELECT * FROM user_credits
WHERE user_id = (SELECT supabase_user_id FROM users WHERE email = 'oadatascientist@gmail.com');
