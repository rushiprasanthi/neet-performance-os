import asyncio
import asyncpg

async def main():
    print("Connecting to PostgreSQL...")
    # Connect to the default 'postgres' database to issue the CREATE command
    conn = await asyncpg.connect('postgresql://postgres:Bhavanarushi@localhost:5432/postgres')
    
    try:
        await conn.execute('CREATE DATABASE neet_pos_test')
        print("✅ Success! Database 'neet_pos_test' created.")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("✅ Database 'neet_pos_test' already exists.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())