# Bookstore Management System

Welcome to the Bookstore Management System! This repository contains the database schema required to manage a bookstore's operations effectively.

## How to Set Up the Database

To get started, follow these steps to create the required tables in MySQL:

1. **Open your MySQL Command Line Interface (CLI):**
   Make sure MySQL is installed and running on your system. Open the MySQL command-line interface and connect to your database.

2. **Create a Database:**
   First, create a new database for the project by executing:
   ```sql
   CREATE DATABASE BookstoreDB;
   USE BookstoreDB;

3 **Create the Tables:**
  Copy and paste the following SQL queries into your MySQL CLI to create the tables:
  '''sql
  CREATE TABLE auditlog (
      AuditID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      Action VARCHAR(255),
      TableName VARCHAR(255),
      ActionDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      Details TEXT
  );
  
  CREATE TABLE books (
      ISBN VARCHAR(17) NOT NULL PRIMARY KEY,
      Title VARCHAR(255) NOT NULL,
      Author VARCHAR(255) NOT NULL,
      Genre VARCHAR(100),
      Price DECIMAL(10,2) NOT NULL,
      Stock INT DEFAULT 0,
      Publisher VARCHAR(255),
      Year YEAR
  );
  
  CREATE TABLE borrowing (
      BorrowingID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      CustomerID INT,
      ISBN VARCHAR(13),
      DateBorrowed DATE,
      DueDate DATE,
      FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
      FOREIGN KEY (ISBN) REFERENCES books(ISBN)
  );
  
  CREATE TABLE customerorderssummary (
      CustomerID INT NOT NULL,
      Name VARCHAR(255) NOT NULL,
      TotalOrders BIGINT NOT NULL DEFAULT 0,
      TotalSpent DECIMAL(32,2),
      PRIMARY KEY (CustomerID)
  );
  
  CREATE TABLE customers (
      CustomerID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      Name VARCHAR(255) NOT NULL,
      Email VARCHAR(255) NOT NULL UNIQUE,
      Phone VARCHAR(15),
      MembershipDate DATE
  );
  
  CREATE TABLE orderdetails (
      OrderID INT NOT NULL,
      ISBN VARCHAR(17) NOT NULL,
      Quantity INT NOT NULL,
      Price DECIMAL(10,2) NOT NULL,
      PRIMARY KEY (OrderID, ISBN),
      FOREIGN KEY (OrderID) REFERENCES orders(OrderID),
      FOREIGN KEY (ISBN) REFERENCES books(ISBN)
  );
  
  CREATE TABLE orders (
      OrderID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      CustomerID INT,
      OrderDate DATETIME NOT NULL,
      TotalAmount DECIMAL(10,2) NOT NULL,
      FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
  );
  
  CREATE TABLE payments (
      PaymentID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      OrderID INT,
      PaymentDate DATETIME NOT NULL,
      Amount DECIMAL(10,2) NOT NULL,
      PaymentMethod VARCHAR(50),
      FOREIGN KEY (OrderID) REFERENCES orders(OrderID)
  );
  
  CREATE TABLE salesbygenreauthor (
      Genre VARCHAR(100),
      Author VARCHAR(255) NOT NULL,
      TotalSales DECIMAL(42,2)
  );
  
  CREATE TABLE shipments (
      ShipmentID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      OrderID INT,
      ShipmentDate DATETIME,
      DeliveryDate DATETIME,
      Status VARCHAR(50),
      FOREIGN KEY (OrderID) REFERENCES orders(OrderID)
  );
  
  CREATE TABLE suppliers (
      SupplierID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      Name VARCHAR(255) NOT NULL,
      Contact VARCHAR(15),
      Address TEXT
  );

5. **Verify Table Creation:**
  Use the SHOW TABLES; command to confirm that all tables are successfully created:
  '''sql
    SHOW TABLES;

6. **Start Using the Database:**
  You can now populate the tables with data and use them for managing your bookstore operations.
