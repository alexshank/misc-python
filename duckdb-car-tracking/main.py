import duckdb


def main():
    # Connect to DuckDB (in-memory database)
    con = duckdb.connect(':memory:')
    
    # Load the CSV file into a table
    con.execute("""
        CREATE TABLE vehicle_log AS 
        SELECT * FROM read_csv_auto('vehicle-log.csv')
    """)
    
    # Create a filtered view for subsequent queries
    con.execute("""
        CREATE TABLE filtered_log AS
        SELECT Log_ID, VT_ID, RecType, Mileage, FillUp, LogDate, Provider, Cost
        FROM vehicle_log
        WHERE VT_ID = 34
            AND RecType = '1'
            AND Mileage IS NOT NULL
            AND Mileage != '-1.00'
        ORDER BY LogDate ASC
    """)
    
    # Query the filtered table
    query_result = con.execute("""
        SELECT * FROM filtered_log
            WHERE FillUp = 'True'
    """)
    
    # Get column names and rows
    columns = [desc[0] for desc in query_result.description]
    result = query_result.fetchall()
    
    # Calculate column widths
    col_widths = [len(col) for col in columns]
    for row in result:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # Display results with proper formatting
    print("Records with VT_ID = 34:")
    print()
    
    # Print header
    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in result:
        row_str = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        print(row_str)
    
    # Get count of matching records
    count = len(result)
    print()
    print(f"Total records with VT_ID = 34: {count}")
    
    # Close connection
    con.close()


if __name__ == "__main__":
    main()
