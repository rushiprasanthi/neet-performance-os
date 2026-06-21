import asyncio
import asyncpg

async def main():
    print("Connecting to database...")
    # Connect directly to your neet_pos database
    conn = await asyncpg.connect('postgresql://postgres:Bhavanarushi@localhost:5432/neet_pos')
    
    try:
        # Update the user's email_verified flag to True
        await conn.execute("UPDATE users SET email_verified = true WHERE email = 'student@neet.com'")
        print("✅ Success! User 'student@neet.com' is now verified.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())