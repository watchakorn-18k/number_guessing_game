import sqlite3


def qurty_database():
    conn = sqlite3.connect("storage.db")

    # Create a cursor object
    c = conn.cursor()

    # Execute a query to sort by score in descending order
    c.execute("SELECT name, score FROM players ORDER BY score DESC")

    # Fetch all the results
    results = c.fetchall()

    # Close the connection
    conn.close()
    return results


print(qurty_database()[0][1])

# for row in qurty_database():
#     print(f"Name: {row[0]}, Score: {row[1]}")


print(qurty_database()[1:])
