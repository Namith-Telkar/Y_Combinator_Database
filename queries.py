import csv
import os 
import pymysql
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB = os.getenv("DB")

def get_connection():
    print("===== Connecting to Database =====")
    print(f"Host: {DB_HOST}")
    print(f"User: {DB_USER}")
    print(f"Password: {DB_PASSWORD}")
    print(f"Database: {DB}")
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB,
        cursorclass=pymysql.cursors.DictCursor
    )


def query1(connection):
    query = """
        SELECT 
            r.Region, 
            r.Country,
            COUNT(DISTINCT c.CompanyID) AS TotalStartups,
            SUM(CASE WHEN cb.BadgeID = (SELECT BadgeID FROM Badges WHERE BadgeName = 'isHiring') THEN 1 ELSE 0 END) AS Hiring,
            COUNT(DISTINCT CASE WHEN c.Status = 'Active' THEN c.CompanyID END) AS ActiveStartups
        FROM 
            Regions r
        INNER JOIN 
            Companies c ON r.RegionID = c.RegionID
        LEFT JOIN 
            CompanyBadges cb ON c.CompanyID = cb.CompanyID
        WHERE
            r.Region != '' AND r.Region IS NOT NULL
            AND r.Country != '' AND r.Country IS NOT NULL 
            AND c.RegionID IS NOT NULL
        GROUP BY 
            r.Region, r.Country
        HAVING 
            COUNT(DISTINCT c.CompanyID) > 5
        ORDER BY 
            Hiring DESC, TotalStartups DESC
        LIMIT 10;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def query2(connection):
    query = """
        SELECT 
            i.IndustryName,
            COUNT(DISTINCT c.CompanyID) AS TotalStartups,
            SUM(CASE WHEN c.Status = 'Active' THEN 1 ELSE 0 END) AS ActiveStartups,
            SUM(CASE WHEN c.Status = 'Acquired' THEN 1 ELSE 0 END) AS AcquiredStartups,
            SUM(CASE WHEN c.Status = 'Public' THEN 1 ELSE 0 END) AS PublicStartups,
            ROUND(SUM(CASE WHEN c.Status IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT c.CompanyID), 2) AS SuccessRate
        FROM 
            Industries i
        JOIN 
            CompanyIndustry ci ON i.IndustryID = ci.IndustryID
        JOIN 
            Companies c ON ci.CompanyID = c.CompanyID
        GROUP BY 
            i.IndustryName
        HAVING 
            TotalStartups > 5
        ORDER BY 
            SuccessRate DESC, TotalStartups DESC
        LIMIT 20;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def query3(connection):
    query_school = """
        SELECT 
            COALESCE(s.SchoolName, 'Unknown') AS Institution,
            COUNT(f.FounderID) AS TotalFounders,
            SUM(CASE WHEN c.Status IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) AS SuccessfulFounders,
            ROUND(SUM(CASE WHEN c.Status IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) * 100.0 / COUNT(f.FounderID), 2) AS SuccessRate
        FROM 
            Founders f
        JOIN 
            Companies c ON f.CompanyID = c.CompanyID
        LEFT JOIN 
            Schools s ON f.FounderID = s.FounderID
        GROUP BY 
            s.SchoolName
        HAVING 
            COUNT(DISTINCT f.FounderID) > 5
        ORDER BY 
            COUNT(DISTINCT f.FounderID) DESC, SuccessRate DESC
        LIMIT 20;
    """
    
    query_pc = """
        SELECT 
            COALESCE(pc.CompanyName, 'Unknown') AS PriorCompany,
            COUNT(DISTINCT f.FounderID) AS TotalFounders,
            SUM(CASE WHEN c.Status IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) AS SuccessfulFounders,
            ROUND(SUM(CASE WHEN c.Status IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT f.FounderID), 2) AS SuccessRate
        FROM 
            Founders f
        JOIN 
            Companies c ON f.CompanyID = c.CompanyID
        LEFT JOIN 
            FounderPriorCompanies fpc ON f.FounderID = fpc.FounderID
        LEFT JOIN 
            PriorCompanies pc ON fpc.PriorCompanyID = pc.PriorCompanyID
        GROUP BY 
            pc.CompanyName
        HAVING 
            COUNT(DISTINCT f.FounderID) > 5
        ORDER BY 
            COUNT(DISTINCT f.FounderID) DESC, SuccessRate DESC
        LIMIT 20;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query_school)
        query_school_result = cursor.fetchall()
        cursor.execute(query_pc)
        query_pc_result = cursor.fetchall()
        return query_school_result, query_pc_result


def query4(connection):
    query = """
    WITH FounderPairs AS (
        SELECT 
            f1.FounderID AS Founder1ID,
            f2.FounderID AS Founder2ID,
            f1.CompanyID,
            c.Status AS CompanyStatus
        FROM 
            Founders f1
        JOIN 
            Founders f2 ON f1.CompanyID = f2.CompanyID AND f1.FounderID < f2.FounderID
        JOIN 
            Companies c ON f1.CompanyID = c.CompanyID
        ),
    SharedBackground AS (
        SELECT 
            fp.Founder1ID,
            fp.Founder2ID,
            fp.CompanyID,
            fp.CompanyStatus,
            CASE 
                WHEN s1.SchoolName = s2.SchoolName THEN 1 
                ELSE 0 
            END AS SharedSchool,
            CASE 
                WHEN pc1.CompanyName = pc2.CompanyName THEN 1 
                ELSE 0 
            END AS SharedPriorCompany
        FROM 
            FounderPairs fp
        LEFT JOIN 
            Schools s1 ON fp.Founder1ID = s1.FounderID
        LEFT JOIN 
            Schools s2 ON fp.Founder2ID = s2.FounderID
        LEFT JOIN 
            FounderPriorCompanies fpc1 ON fp.Founder1ID = fpc1.FounderID
        LEFT JOIN 
            FounderPriorCompanies fpc2 ON fp.Founder2ID = fpc2.FounderID
        LEFT JOIN 
            PriorCompanies pc1 ON fpc1.PriorCompanyID = pc1.PriorCompanyID
        LEFT JOIN 
            PriorCompanies pc2 ON fpc2.PriorCompanyID = pc2.PriorCompanyID
    )
    SELECT 
        CASE 
            WHEN SharedSchool = 1 AND SharedPriorCompany = 1 THEN 'Shared School and Company'
            WHEN SharedSchool = 1 THEN 'Shared School Only'
            WHEN SharedPriorCompany = 1 THEN 'Shared Company Only'
            ELSE 'No Shared Background'
        END AS FounderRelationship,
        COUNT(*) AS TotalPairs,
        SUM(CASE WHEN CompanyStatus IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) AS SuccessfulPairs,
        ROUND(SUM(CASE WHEN CompanyStatus IN ('Active', 'Acquired', 'Public') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS SuccessRate
    FROM 
        SharedBackground
    GROUP BY 
        CASE 
            WHEN SharedSchool = 1 AND SharedPriorCompany = 1 THEN 'Shared School and Company'
            WHEN SharedSchool = 1 THEN 'Shared School Only'
            WHEN SharedPriorCompany = 1 THEN 'Shared Company Only'
            ELSE 'No Shared Background'
        END
    ORDER BY 
        SuccessRate DESC;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

if __name__ == "__main__":
    connection = get_connection()
    query1_result = query1(connection)
    table1 = tabulate(query1_result, headers="keys", tablefmt="grid")
    print(table1)
    print("\n\n\n")
    query2_result = query2(connection)
    table2 = tabulate(query2_result, headers="keys", tablefmt="grid")
    print(table2)
    print("\n\n\n")
    query3_result_school, query3_result_pc = query3(connection)
    table3_school = tabulate(query3_result_school, headers="keys", tablefmt="grid")
    print(table3_school)
    print("\n")
    table3_pc = tabulate(query3_result_pc, headers="keys", tablefmt="grid")
    print(table3_pc)
    print("\n\n\n")
    query4_result = query4(connection)
    table4 = tabulate(query4_result, headers="keys", tablefmt="grid")
    print(table4)
    connection.close()