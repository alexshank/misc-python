import duckdb


def print_query_results(query_result, title):
    """Print query results with nice formatting"""
    # extract columns and fetch results
    columns = [desc[0] for desc in query_result.description]
    result = query_result.fetchall()
    
    # calculate column widths
    col_widths = [len(col) for col in columns]
    for row in result:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # display results with proper formatting
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print()
    
    # print header
    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
    print(header)
    print("-" * len(header))
    
    # print rows
    for row in result:
        row_str = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        print(row_str)
    
    # print total count
    print()
    print(f"{title}: {len(result)} records.")
    
    return result


def main():
    con = duckdb.connect(':memory:')
    
    # create vehicle_log table from CSV
    con.execute("""
        CREATE TABLE vehicle_log AS 
        SELECT * FROM read_csv_auto('vehicle-log.csv')
    """)
    
    # create a filtered view for subsequent queries
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
    
    # query the filtered table and nicely print
    query_result = con.execute("""
        SELECT * FROM filtered_log
            WHERE FillUp = 'True'
    """)
    print_query_results(query_result, "Records with VT_ID = 34")
    
    # create intermediate table with differences between fill-ups
    con.execute("""
        CREATE TABLE fillup_differences AS
        SELECT 
            LogDate,
            Mileage,
            LAG(LogDate) OVER (ORDER BY LogDate) AS prev_date,
            LAG(Mileage) OVER (ORDER BY LogDate) AS prev_mileage,
            DATEDIFF('day', LAG(LogDate) OVER (ORDER BY LogDate), LogDate) AS days_between,
            TRY_CAST(REPLACE(Mileage, ',', '') AS DOUBLE) - TRY_CAST(REPLACE(LAG(Mileage) OVER (ORDER BY LogDate), ',', '') AS DOUBLE) AS mileage_difference
        FROM filtered_log
        WHERE FillUp = 'True'
    """)
    
    # display the intermediate differences table
    diff_query_result = con.execute("""
        SELECT * FROM fillup_differences
        WHERE days_between IS NOT NULL
    """)
    print_query_results(diff_query_result, "Fill-up Differences")
    
    # query the average from the differences table
    avg_result = con.execute("""
        SELECT 
            AVG(days_between) AS avg_days_between_fillups,
            AVG(mileage_difference) AS avg_mileage_between_fillups
        FROM fillup_differences
        WHERE days_between IS NOT NULL AND mileage_difference IS NOT NULL
    """).fetchone()
    
    print()
    print("=" * 80)
    print("Fill-up Statistics:")
    print("=" * 80)
    print()
    if avg_result[0]:
        print(f"Average days between fill-ups: {avg_result[0]:.2f}")
        print(f"Average mileage between fill-ups: {avg_result[1]:.2f}")
    else:
        print("Not enough data to calculate averages.")
    
    # query averages grouped by year
    yearly_query_result = con.execute("""
        SELECT 
            YEAR(LogDate) AS year,
            AVG(days_between) AS avg_days_between_fillups,
            AVG(mileage_difference) AS avg_mileage_between_fillups
        FROM fillup_differences
        WHERE days_between IS NOT NULL AND mileage_difference IS NOT NULL
        GROUP BY YEAR(LogDate)
        ORDER BY year
    """)
    print_query_results(yearly_query_result, "Yearly Fill-up Statistics")
    
    con.close()


if __name__ == "__main__":
    main()
