import csv
import os 
import pymysql
from dotenv import load_dotenv

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


def drop_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("DROP TABLE IF EXISTS Badges")
        cursor.execute("DROP TABLE IF EXISTS Industries")
        cursor.execute("DROP TABLE IF EXISTS Tags")
        cursor.execute("DROP TABLE IF EXISTS Regions")
        cursor.execute("DROP TABLE IF EXISTS Companies")
        cursor.execute("DROP TABLE IF EXISTS CompanyBadges")
        cursor.execute("DROP TABLE IF EXISTS CompanyIndustry")
        cursor.execute("DROP TABLE IF EXISTS CompanyTag")
        cursor.execute("DROP TABLE IF EXISTS Founders")
        cursor.execute("DROP TABLE IF EXISTS PriorCompanies")
        cursor.execute("DROP TABLE IF EXISTS FounderPriorCompanies")
        cursor.execute("DROP TABLE IF EXISTS Schools")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        print("===== Tables Dropped =====")


def create_badges_table(connection):
    badges_create = """
        CREATE TABLE Badges (
            BadgeID INT AUTO_INCREMENT PRIMARY KEY,
            BadgeName VARCHAR(255) NOT NULL
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(badges_create)
        print("===== Badges Table Created =====")
        connection.commit()
    
        with open("data/badges.csv", encoding="utf-8-sig") as csvf:
            badges = list(csv.DictReader(csvf))
            unique_badges = []
            for row in badges:
                if row["badge"] not in unique_badges:
                    unique_badges.append(row["badge"])
            for badge in unique_badges:
                cursor.execute("INSERT INTO Badges (BadgeName) VALUES (%s);", (badge))
            print("===== Badges Data Inserted =====")
    
        connection.commit()
        

def create_industries_table(connection):
    industries_create = """
        CREATE TABLE Industries (
            IndustryID INT AUTO_INCREMENT PRIMARY KEY,
            IndustryName VARCHAR(255) NOT NULL
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(industries_create)
        print("===== Industries Table Created =====")
        connection.commit()
    
        with open("data/industries.csv", encoding="utf-8-sig") as csvf:
            industries = list(csv.DictReader(csvf))
            unique_industries = []
            for row in industries:
                if row["industry"] not in unique_industries:
                    unique_industries.append(row["industry"])
            for industry in unique_industries:
                cursor.execute("INSERT INTO Industries (IndustryName) VALUES (%s);", (industry))
            print("===== Industries Data Inserted =====")
    
        connection.commit()


def create_tags_table(connection):
    tags_create = """
        CREATE TABLE Tags (
            TagID INT AUTO_INCREMENT PRIMARY KEY,
            TagName VARCHAR(255) NOT NULL
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(tags_create)
        print("===== Tags Table Created =====")
        connection.commit()
    
        with open("data/tags.csv", encoding="utf-8-sig") as csvf:
            tags = list(csv.DictReader(csvf))
            unique_tags = []
            for row in tags:
                if row["tag"] not in unique_tags:
                    unique_tags.append(row["tag"])
            for tag in unique_tags:
                cursor.execute("INSERT INTO Tags (TagName) VALUES (%s);", (tag))
            print("===== Tags Data Inserted =====")
    
        connection.commit()

def create_regions_table(connection):
    regions = """
        CREATE TABLE Regions(
            RegionID INT AUTO_INCREMENT PRIMARY KEY,
            Region VARCHAR(255) NOT NULL,
            Country VARCHAR(255) NOT NULL,
            Address VARCHAR(500) NOT NULL    
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(regions)
        print("===== Regions Table Created =====")
        connection.commit()
    
        with open("data/regions.csv", encoding="utf-8-sig") as csvf:
            regions = list(csv.DictReader(csvf))
            unique_addresses = []
            address_regions = {}
            for row in regions:
                if row["address"] not in unique_addresses:
                    unique_addresses.append(row["address"])
                    address_regions[row["address"]] = [row["region"], row["country"]]
                    
            for address in unique_addresses:
                cursor.execute("INSERT INTO Regions (Region, Country, Address) VALUES (%s, %s, %s);", (address_regions[address][0], address_regions[address][1], address))
            print("===== Regions Data Inserted =====")
        
        connection.commit()

def create_companies_table(connection):
    companies_create = """
        CREATE TABLE Companies (
            CompanyID INT PRIMARY KEY,
            CompanyName VARCHAR(255) NOT NULL,
            Slug VARCHAR(255),
            Website VARCHAR(1500),
            SmallLogoUrl VARCHAR(1500),
            OneLiner VARCHAR(500),
            LongDescription TEXT,
            TeamSize INT,
            YCombUrl VARCHAR(1500) NOT NULL,
            Batch VARCHAR(10) NOT NULL,
            Status VARCHAR(255) NOT NULL,
            RegionID INT NOT NULL,
            FOREIGN KEY (RegionID) REFERENCES Regions(RegionID) ON DELETE RESTRICT ON UPDATE CASCADE
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(companies_create)
        print("===== Companies Table Created =====")
        connection.commit()
    
        with open("data/companies.csv", encoding="utf-8-sig") as csvf:
            companies = list(csv.DictReader(csvf))
            
        with open("data/regions.csv", encoding="utf-8-sig") as csvf:  
            regions = list(csv.DictReader(csvf))
            company_to_region_id = {}
            address_to_region_id = []
            
            for row in regions:
                if row["address"] not in address_to_region_id:
                    address_to_region_id.append(row["address"])
                    
            for row in regions:
                company_to_region_id[row["id"]] = str(address_to_region_id.index(row["address"]) + 1)
                
    
        for row in companies:
            cursor.execute("""
                INSERT INTO Companies 
                (CompanyID, CompanyName, Slug, Website, SmallLogoUrl, OneLiner, LongDescription, TeamSize, YCombUrl, Batch, Status, RegionID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                row["id"],
                row["name"],
                row["slug"],
                row["website"],
                row["smallLogoUrl"],
                row["oneLiner"],
                row["longDescription"],
                int(row["teamSize"]) if row["teamSize"] != "" else None,
                row["url"],
                row["batch"],
                row["status"],
                company_to_region_id[row["id"]] if row["id"] in company_to_region_id else None,
            ))
        print("===== Companies Data Inserted =====")
        
    connection.commit()
    

def create_company_badges_table(connection):
    company_badges_create = """
        CREATE TABLE CompanyBadges (
            CompanyID INT NOT NULL,
            BadgeID INT NOT NULL,
            FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (BadgeID) REFERENCES Badges(BadgeID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (CompanyID, BadgeID)
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(company_badges_create)
        print("===== Company Badges Table Created =====")
        connection.commit()
    
        with open("data/badges.csv", encoding="utf-8-sig") as csvf:
            company_badges = list(csv.DictReader(csvf))
            unique_badges = []
            for row in company_badges:
                if row["badge"] not in unique_badges:
                    unique_badges.append(row["badge"])
            badge_to_id = {}
            for idx, badge in enumerate(unique_badges):
                badge_to_id[badge] = str(idx + 1)
            
            for row in company_badges:
                cursor.execute("INSERT INTO CompanyBadges (CompanyID, BadgeID) VALUES (%s, %s);", (row["id"], badge_to_id[row["badge"]]))
            print("===== Company Badges Data Inserted =====")
        
        connection.commit()
    
        
def create_company_industry_table(connection):
    company_industry_create = """
        CREATE TABLE CompanyIndustry (
            CompanyID INT NOT NULL,
            IndustryID INT NOT NULL,
            FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (IndustryID) REFERENCES Industries(IndustryID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (CompanyID, IndustryID)
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(company_industry_create)
        print("===== Company Industry Table Created =====")
        connection.commit()
    
        with open("data/industries.csv", encoding="utf-8-sig") as csvf:
            company_industry = list(csv.DictReader(csvf))
            unique_industries = []
            for row in company_industry:
                if row["industry"] not in unique_industries:
                    unique_industries.append(row["industry"])
            industry_to_id = {}
            for idx, industry in enumerate(unique_industries):
                industry_to_id[industry] = str(idx + 1)
            
            for row in company_industry:
                cursor.execute("INSERT INTO CompanyIndustry (CompanyID, IndustryID) VALUES (%s, %s);", (row["id"], industry_to_id[row["industry"]]))
            print("===== Company Industry Data Inserted =====")
        
        connection.commit()


def create_company_tag_table(connection):
    company_tag_create = """
        CREATE TABLE CompanyTag (
            CompanyID INT NOT NULL,
            TagID INT NOT NULL,
            FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (TagID) REFERENCES Tags(TagID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (CompanyID, TagID)
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(company_tag_create)
        print("===== Company Tag Table Created =====")
        connection.commit()
    
        with open("data/tags.csv", encoding="utf-8-sig") as csvf:
            company_tag = list(csv.DictReader(csvf))
            unique_tags = []
            for row in company_tag:
                if row["tag"] not in unique_tags:
                    unique_tags.append(row["tag"])
            tag_to_id = {}
            for idx, tag in enumerate(unique_tags):
                tag_to_id[tag] = str(idx + 1)
            
            for row in company_tag:
                cursor.execute("INSERT INTO CompanyTag (CompanyID, TagID) VALUES (%s, %s);", (row["id"], tag_to_id[row["tag"]]))
            print("===== Company Tag Data Inserted =====")
        
        connection.commit()



def create_founders_tables(connection):
    founders = """
        CREATE TABLE Founders(
            FounderID VARCHAR(255) PRIMARY KEY,
            CompanyID INT NOT NULL,
            FirstName VARCHAR(255) NOT NULL,
            LastName VARCHAR(255) NOT NULL,
            AvatarUrl VARCHAR(1500),
            CurrentCompany VARCHAR(255),
            CurrentTitle VARCHAR(255),
            TopCompany TINYINT NOT NULL,
            FOREIGN KEY (CompanyID) REFERENCES Companies(CompanyID) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(founders)
        print("===== Founders Table Created =====")
        connection.commit()
    
        with open("data/companies.csv", encoding="utf-8-sig") as csvf:
            companies = list(csv.DictReader(csvf))
            company_slug_to_id = {}
            for row in companies:
                if row["slug"] != "":
                    company_slug_to_id[row["slug"]] = row["id"]
    
        with open("data/founders.csv", encoding="utf-8-sig") as csvf:
            founders = list(csv.DictReader(csvf))
            for row in founders:
                cursor.execute("""
                    INSERT INTO Founders 
                    (FounderID, CompanyID, FirstName, LastName, AvatarUrl, CurrentCompany, CurrentTitle, TopCompany)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    row["hnid"],
                    company_slug_to_id[row["company_slug"]],
                    row["first_name"],
                    row["last_name"],
                    row["avatar_thumb"],
                    row["current_company"],
                    row["current_title"],
                    1 if row["top_company"] == 'True' else 0,
                ))
            print("===== Founders Data Inserted =====")
        
        connection.commit()


def create_prior_companies_tables(connection):
    prior_companies = """
        CREATE TABLE PriorCompanies(
            PriorCompanyID INT AUTO_INCREMENT PRIMARY KEY,
            CompanyName VARCHAR(255) NOT NULL
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(prior_companies)
        print("===== Prior Companies Table Created =====")
        connection.commit()
    
        with open("data/prior_companies.csv", encoding="utf-8-sig") as csvf:
            prior_companies = list(csv.DictReader(csvf))
            prior_companies_unique = []
            for row in prior_companies:
                if row["company"] not in prior_companies_unique:
                    prior_companies_unique.append(row["company"])
            
            for company in prior_companies_unique:
                cursor.execute("INSERT INTO PriorCompanies (CompanyName) VALUES (%s);", (company))
                
            print("===== Prior Companies Data Inserted =====")
        
        connection.commit()


def create_founder_prior_companies_tables(connection):
    founder_prior_companies = """
        CREATE TABLE FounderPriorCompanies(
            FounderID VARCHAR(255) NOT NULL,
            PriorCompanyID INT NOT NULL,
            FOREIGN KEY (FounderID) REFERENCES Founders(FounderID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (PriorCompanyID) REFERENCES PriorCompanies(PriorCompanyID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (FounderID, PriorCompanyID)
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(founder_prior_companies)
        print("===== Founder Prior Companies Table Created =====")
        connection.commit()
    
        with open("data/prior_companies.csv", encoding="utf-8-sig") as csvf:
            founder_prior_companies = list(csv.DictReader(csvf))
            prior_companies_unique = []
            for row in founder_prior_companies:
                if row["company"] not in prior_companies_unique:
                    prior_companies_unique.append(row["company"])
                    
            prior_company_to_id = {}
            for idx, company in enumerate(prior_companies_unique):
                prior_company_to_id[company] = str(idx + 1)
            
            for row in founder_prior_companies:
                cursor.execute("INSERT INTO FounderPriorCompanies (FounderID, PriorCompanyID) VALUES (%s, %s);", (row["hnid"], prior_company_to_id[row["company"]]))   
            print("===== Founder Prior Companies Data Inserted =====")
        
        connection.commit()

def create_schools_tables(connection):
    schools = """
        CREATE TABLE Schools(
            SchoolID INT AUTO_INCREMENT PRIMARY KEY,
            FounderID VARCHAR(255) NOT NULL,
            SchoolName VARCHAR(500) NOT NULL,
            FieldOfStudy VARCHAR(500),
            YearGraduated INT NOT NULL,
            FOREIGN KEY (FounderID) REFERENCES Founders(FounderID) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    
    with connection.cursor() as cursor:
        cursor.execute(schools)
        print("===== Schools Table Created =====")
        connection.commit()
    
        with open("data/schools.csv", encoding="utf-8-sig") as csvf:
            schools = list(csv.DictReader(csvf))
            for row in schools:
                cursor.execute("INSERT INTO Schools (FounderID, SchoolName, FieldOfStudy, YearGraduated) VALUES (%s, %s, %s, %s);", (row["hnid"], row["school"], row["field_of_study"], row["year"]))
                
            print("===== Schools Data Inserted =====")
        
        connection.commit()


def initializeDB():
    connection = get_connection()
    drop_tables(connection)
    create_badges_table(connection)
    create_industries_table(connection)
    create_tags_table(connection)
    create_regions_table(connection)
    create_companies_table(connection)
    create_company_badges_table(connection)
    create_company_industry_table(connection)
    create_company_tag_table(connection)
    create_founders_tables(connection)
    create_prior_companies_tables(connection)
    create_founder_prior_companies_tables(connection)
    create_schools_tables(connection)
    connection.close()


if __name__ == "__main__":
    initializeDB()