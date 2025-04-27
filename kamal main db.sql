-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: kamal
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `a_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` varchar(50) DEFAULT 'REGULAR',
  PRIMARY KEY (`a_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'GST Colour Chemical','REGULAR'),(2,'Process','PROCESS'),(3,'Other','REGULAR');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bill_items`
--

DROP TABLE IF EXISTS `bill_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill_items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `bill_s_no` int NOT NULL,
  `product_id` int NOT NULL,
  `qty` decimal(10,2) NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `sub_total` decimal(10,2) NOT NULL,
  `gst_percent` decimal(5,2) NOT NULL,
  `sgst_amount` decimal(10,2) NOT NULL,
  `cgst_amount` decimal(10,2) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  KEY `item_id` (`item_id`),
  KEY `product_id` (`product_id`),
  KEY `idx_bill_items_bill` (`bill_s_no`),
  CONSTRAINT `bill_items_ibfk_1` FOREIGN KEY (`bill_s_no`) REFERENCES `incoming_bills` (`s_no`) ON DELETE CASCADE,
  CONSTRAINT `bill_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `prod_master` (`prod_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill_items`
--

LOCK TABLES `bill_items` WRITE;
/*!40000 ALTER TABLE `bill_items` DISABLE KEYS */;
INSERT INTO `bill_items` VALUES (1,1,1,100.00,2300.00,230000.00,18.00,20700.00,20700.00,271400.00),(1,2,8,50.00,275.00,13750.00,5.00,343.75,343.75,14437.50),(1,3,9,165.00,115.00,18975.00,5.00,474.38,474.38,19923.75),(1,4,10,21.00,1610.00,33810.00,0.00,0.00,0.00,33810.00),(1,5,10,21.00,1610.00,33810.00,0.00,0.00,0.00,33810.00),(1,6,11,300.00,291.00,87300.00,18.00,6992.73,6992.73,91682.46),(1,7,12,500.00,261.00,130500.00,18.00,10453.05,10453.05,137051.10),(1,8,13,40.00,170.00,6800.00,18.00,612.00,612.00,8024.00),(2,8,14,50.00,110.00,5500.00,18.00,495.00,495.00,6490.00),(3,8,15,25.00,220.00,5500.00,18.00,495.00,495.00,6490.00),(1,9,16,50.00,230.00,11500.00,18.00,1035.00,1035.00,13570.00),(1,9,17,50.00,220.00,11000.00,18.00,990.00,990.00,12980.00),(1,10,18,100.00,65.00,6500.00,18.00,585.00,585.00,7670.00),(1,11,19,50.00,270.00,13500.00,18.00,1124.97,1124.97,14749.59),(1,12,20,100.00,630.00,63000.00,18.00,5670.00,5670.00,74340.00),(1,12,21,50.00,730.00,36500.00,18.00,3285.00,3285.00,43070.00),(1,13,18,100.00,65.00,6500.00,18.00,585.00,585.00,7670.00),(1,14,22,30.00,495.00,14850.00,18.00,1336.50,1336.50,17523.00),(1,15,17,100.00,220.00,22000.00,18.00,1980.00,1980.00,25960.00),(1,16,23,100.00,165.00,16500.00,18.00,1485.00,1485.00,19470.00),(1,17,1,50.00,2375.00,118750.00,18.00,10687.50,10687.50,140125.00),(1,18,1,20.00,2380.00,47600.00,18.00,4284.00,4284.00,56168.00),(1,19,24,69.00,130.00,8970.00,0.00,0.00,0.00,8970.00),(1,20,25,100.00,90.00,9000.00,18.00,769.50,769.50,10089.00),(1,20,26,50.00,70.00,3500.00,18.00,299.25,299.25,3923.50),(1,20,27,50.00,200.00,10000.00,18.00,855.00,855.00,11210.00),(1,21,28,26.00,310.69,8077.94,18.00,727.01,727.01,9531.97),(1,22,2,2080.00,7.90,16432.00,18.00,1478.88,1478.88,19389.76),(1,23,3,138.00,70.00,9660.00,5.00,241.50,241.50,10143.00),(1,24,1,50.00,2375.00,118750.00,18.00,10687.50,10687.50,140125.00),(1,25,29,12.00,230.00,2760.00,5.00,69.00,69.00,2898.00),(1,26,17,150.00,220.00,33000.00,18.00,2970.00,2970.00,38940.00),(1,26,5,150.00,155.00,23250.00,18.00,2092.50,2092.50,27435.00),(1,27,6,150.00,530.00,79500.00,18.00,7155.00,7155.00,93810.00),(1,27,7,125.00,180.00,22500.00,18.00,2025.00,2025.00,26550.00),(1,28,17,30.00,205.00,6150.00,18.00,553.50,553.50,7257.00),(1,28,30,30.00,205.00,6150.00,18.00,553.50,553.50,7257.00),(1,29,10,21.00,1207.50,25357.50,0.00,0.00,0.00,25357.50),(1,30,10,21.00,1207.50,25357.50,0.00,0.00,0.00,25357.50),(1,31,31,250.00,405.00,101250.00,18.00,9112.50,9112.50,119475.00),(1,31,32,100.00,425.00,42500.00,18.00,3825.00,3825.00,50150.00),(1,32,17,150.00,205.00,30750.00,18.00,2767.50,2767.50,36285.00),(1,32,33,30.00,275.00,8250.00,18.00,742.50,742.50,9735.00),(1,33,34,30.00,360.00,10800.00,18.00,972.00,972.00,12744.00),(1,34,35,9.00,250.00,2250.00,5.00,56.25,56.25,2362.50),(1,35,36,25.00,450.00,11250.00,18.00,1012.50,1012.50,13275.00),(1,35,20,25.00,100.00,2500.00,18.00,225.00,225.00,2950.00);
/*!40000 ALTER TABLE `bill_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cash_purchase_items`
--

DROP TABLE IF EXISTS `cash_purchase_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cash_purchase_items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `purchase_id` int NOT NULL,
  `product_id` int DEFAULT NULL,
  `description` varchar(255) NOT NULL,
  `qty` decimal(10,2) NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `gst_percent` decimal(5,2) DEFAULT '0.00',
  `gst_amount` decimal(10,2) DEFAULT '0.00',
  `total_amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `purchase_id` (`purchase_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cash_purchase_items_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `cash_purchases` (`purchase_id`) ON DELETE CASCADE,
  CONSTRAINT `cash_purchase_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `prod_master` (`prod_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cash_purchase_items`
--

LOCK TABLES `cash_purchase_items` WRITE;
/*!40000 ALTER TABLE `cash_purchase_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cash_purchase_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cash_purchases`
--

DROP TABLE IF EXISTS `cash_purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cash_purchases` (
  `purchase_id` int NOT NULL AUTO_INCREMENT,
  `party_id` int DEFAULT NULL,
  `purchase_date` date NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_mode` varchar(50) NOT NULL,
  `reference_no` varchar(100) DEFAULT NULL,
  `remarks` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`purchase_id`),
  KEY `party_id` (`party_id`),
  CONSTRAINT `cash_purchases_ibfk_1` FOREIGN KEY (`party_id`) REFERENCES `party_master` (`p_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cash_purchases`
--

LOCK TABLES `cash_purchases` WRITE;
/*!40000 ALTER TABLE `cash_purchases` DISABLE KEYS */;
/*!40000 ALTER TABLE `cash_purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `incoming_bills`
--

DROP TABLE IF EXISTS `incoming_bills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incoming_bills` (
  `s_no` int NOT NULL AUTO_INCREMENT,
  `inv_id` varchar(50) NOT NULL,
  `party_id` int NOT NULL,
  `account_id` int NOT NULL,
  `bill_date` date NOT NULL,
  `final_amount` decimal(10,2) NOT NULL,
  `tds_percent` decimal(5,2) DEFAULT '0.00',
  `tds_amount` decimal(10,2) DEFAULT '0.00',
  `discount_percent` decimal(5,2) DEFAULT '0.00',
  `discount_amount` decimal(10,2) DEFAULT '0.00',
  `remarks` text,
  PRIMARY KEY (`s_no`),
  KEY `party_id` (`party_id`),
  CONSTRAINT `incoming_bills_ibfk_1` FOREIGN KEY (`party_id`) REFERENCES `party_master` (`p_id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_bills`
--

LOCK TABLES `incoming_bills` WRITE;
/*!40000 ALTER TABLE `incoming_bills` DISABLE KEYS */;
INSERT INTO `incoming_bills` VALUES (1,'2',10,1,'2025-04-01',271400.00,NULL,NULL,0.00,0.00,NULL),(2,'1',11,2,'2025-04-01',14437.50,1.00,137.50,0.00,0.00,NULL),(3,'1652',12,3,'2025-04-01',19923.75,NULL,NULL,0.00,0.00,NULL),(4,'8174',13,3,'2025-03-31',33810.00,NULL,NULL,0.00,0.00,NULL),(5,'8175',13,3,'2025-03-31',33810.00,NULL,NULL,0.00,0.00,NULL),(6,'32',14,1,'2025-04-04',91682.46,NULL,0.00,11.00,9603.00,''),(7,'46',14,1,'2025-04-04',137051.10,NULL,0.00,11.00,14355.00,''),(8,'9',9,1,'2025-04-02',21004.00,NULL,0.00,0.00,0.00,''),(9,'6',8,1,'2025-04-02',26550.00,NULL,0.00,0.00,0.00,''),(10,'8',16,1,'2025-04-01',7670.00,NULL,0.00,0.00,0.00,''),(11,'3',17,1,'2025-04-01',14749.59,NULL,0.00,7.41,1000.35,''),(12,'3',18,1,'2025-04-01',117410.00,NULL,0.00,0.00,0.00,''),(13,'28',16,1,'2025-04-05',7670.00,NULL,0.00,0.00,0.00,''),(14,'5',19,1,'2025-04-01',17523.00,NULL,0.00,0.00,0.00,''),(15,'55',8,1,'2025-04-09',25960.00,NULL,0.00,0.00,0.00,''),(16,'1106',20,1,'2025-04-02',19470.00,NULL,0.00,0.00,0.00,''),(17,'7',3,1,'2025-04-08',140125.00,NULL,0.00,0.00,0.00,''),(18,'14683',2,1,'2025-04-06',56168.00,NULL,0.00,0.00,0.00,''),(19,'111',4,1,'2025-04-05',8970.00,NULL,0.00,0.00,0.00,''),(20,'1632',21,1,'2025-04-07',25222.50,NULL,0.00,5.00,1125.00,''),(21,'74',7,3,'2025-04-08',9531.97,NULL,0.00,0.00,0.00,''),(22,'28',5,1,'2025-04-07',19389.76,NULL,0.00,0.00,0.00,''),(23,'15',6,2,'2025-04-05',10143.00,2.00,193.20,0.00,0.00,'RENU AND MIX BLEACHING'),(24,'11',3,1,'2025-04-14',140125.00,0.00,0.00,0.00,0.00,''),(25,'7',22,3,'2025-04-05',2898.00,0.00,0.00,0.00,0.00,''),(26,'80',8,1,'2025-04-14',66375.00,0.00,0.00,0.00,0.00,''),(27,'64',9,1,'2025-04-14',120360.00,0.00,0.00,0.00,0.00,''),(28,'50',19,1,'2025-04-07',14514.00,0.00,0.00,0.00,0.00,''),(29,'114',13,3,'2025-04-16',25357.50,0.00,0.00,0.00,0.00,'G1-95'),(30,'113',13,3,'2025-04-16',25357.50,0.00,0.00,0.00,0.00,'G-1-94'),(31,'24',18,1,'2025-04-14',169625.00,0.00,0.00,0.00,0.00,''),(32,'109',19,1,'2025-04-19',46020.00,0.00,0.00,0.00,0.00,''),(33,'114',19,1,'2025-04-21',12744.00,0.00,0.00,0.00,0.00,''),(34,'19',22,3,'2025-04-19',2362.50,0.00,0.00,0.00,0.00,''),(35,'140',8,1,'2025-04-25',16225.00,0.00,0.00,0.00,0.00,'');
/*!40000 ALTER TABLE `incoming_bills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outgoing_bill_items`
--

DROP TABLE IF EXISTS `outgoing_bill_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outgoing_bill_items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `bill_s_no` int NOT NULL,
  `product_id` int NOT NULL,
  `qty` decimal(10,2) NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `sub_total` decimal(10,2) NOT NULL,
  `gst_percent` decimal(5,2) NOT NULL,
  `sgst_amount` decimal(10,2) NOT NULL,
  `cgst_amount` decimal(10,2) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `bill_s_no` (`bill_s_no`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `outgoing_bill_items_ibfk_1` FOREIGN KEY (`bill_s_no`) REFERENCES `outgoing_bills` (`s_no`) ON DELETE CASCADE,
  CONSTRAINT `outgoing_bill_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `prod_master` (`prod_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_bill_items`
--

LOCK TABLES `outgoing_bill_items` WRITE;
/*!40000 ALTER TABLE `outgoing_bill_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `outgoing_bill_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outgoing_bills`
--

DROP TABLE IF EXISTS `outgoing_bills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outgoing_bills` (
  `s_no` int NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(50) NOT NULL,
  `party_id` int NOT NULL,
  `bill_date` date NOT NULL,
  `account_id` int DEFAULT NULL,
  `tds_percent` decimal(5,2) DEFAULT NULL,
  `tds_amount` decimal(10,2) DEFAULT NULL,
  `final_amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`s_no`),
  KEY `party_id` (`party_id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `outgoing_bills_ibfk_1` FOREIGN KEY (`party_id`) REFERENCES `party_master` (`p_id`),
  CONSTRAINT `outgoing_bills_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`a_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_bills`
--

LOCK TABLES `outgoing_bills` WRITE;
/*!40000 ALTER TABLE `outgoing_bills` DISABLE KEYS */;
/*!40000 ALTER TABLE `outgoing_bills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `party_master`
--

DROP TABLE IF EXISTS `party_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `party_master` (
  `p_id` int NOT NULL AUTO_INCREMENT,
  `party` varchar(255) NOT NULL,
  `gstin` varchar(15) DEFAULT NULL,
  `address` text,
  PRIMARY KEY (`p_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `party_master`
--

LOCK TABLES `party_master` WRITE;
/*!40000 ALTER TABLE `party_master` DISABLE KEYS */;
INSERT INTO `party_master` VALUES (2,'Maa Kripa Dyes','08ASXPS8106L1ZR','207, GHARWALA JAV, PALI'),(3,'Praveen Dye Chem','08AQUPS6331A1ZM','360-361, ANAND NAGAR MANDIA ROAD, PALI-MARWAR'),(4,'SIDDHI VINAYAK SALT SUPPLIERS','NIL','11, RAM LEELA MAIDAN ROAD, PALI-MARWAR'),(5,'SUPEREME RASAYAN','08AWZPK5845N1ZD','PUNAYTA INDUSTRIAL AREA'),(6,'GANDHI FAB TEX','08AAPFG2167F1Z9','F-79 MANDIA ROAD'),(7,'OM MACHINERY STORE','08ABSPS1120Q1Z1','MANDIA ROAD, PALI'),(8,'Rounak Chemicals','08AALPD6383N1Z4','73,74 Ambavadi Gadhi Nagar, Mandia Road Pali-Marwar'),(9,'Maruti Dye Chem','08AAPFK2310Q1ZX','71, 72 Ambavadi Gadhi Nagar, Mandia Road Pali-Marwar'),(10,'Trishul Enterprises','08AHEPB5402E2ZZ','135, VD Nagar, Pali'),(11,'Shree Vishnu Laxmi Industries','08OPRPS1015F1ZG','G-102, PUNAYTA INDUSTRIAL AREA, PALI'),(12,'Rajmal Magaji','08ABAHS3019J1Z4','30, GANCHO KA BAS, MANDIA ROAD, PALI'),(13,'CETP','08AAHCC3642E1ZV','CETP MANDIA ROAD'),(14,'MURLIWALA ENTERPRISES','08AAPFK2310Q1ZX','104, GURU PUSHKAR MARG MANDIA ROAD, PALI'),(15,'Color Plus','08AAPFK2310Q1ZX','104, MAHAVEER GAH, MANDIA ROAD'),(16,'Kedia Organic','08ABDPG9531A1Z2','Khopra Katla, Pali'),(17,'Kedia Chemical','08ABDPG9532D1ZV','Khopra Katla, Pali'),(18,'Kedia Rasayan','08ADGPG2211E1Z8','Khopra Katla, Pali'),(19,'Kedia Agencies','08AAWPG5102G1ZO','Khopra Katla, pali'),(20,'PINKY CHEMICAL','08AAXPP4984H1ZQ','GOKULWARI, PALI'),(21,'BALAJI CHEMICAL','08AVZPJ8375P1Z5','374, MG COLONY, RAMDEV ROAD'),(22,'Rathi Yarn & threads','08BXHPR0214G1ZN','167, SHREEE BALAJI NAGAR, PUNAYTA INDUSTRIAL AREA');
/*!40000 ALTER TABLE `party_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `payment_date` date NOT NULL,
  `payment_type` enum('vendor','misc') NOT NULL,
  `vendor_id` int DEFAULT NULL,
  `payment_for` varchar(255) DEFAULT NULL,
  `payment_mode` enum('cash','bank','upi','cheque') NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `narration` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `party_master` (`p_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prod_master`
--

DROP TABLE IF EXISTS `prod_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prod_master` (
  `prod_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `hsn_code` varchar(50) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`prod_id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prod_master`
--

LOCK TABLES `prod_master` WRITE;
/*!40000 ALTER TABLE `prod_master` DISABLE KEYS */;
INSERT INTO `prod_master` VALUES (1,'Caustic Soda Flakes','2815110','Chemical'),(2,'HYPO','28289090','CHEMICAL'),(3,'BLEACHING (ONLY WASHING)','998821','PROCESS'),(5,'Yellow HRDF','320416','Colour Chemical'),(6,'F Scarlet G Base','320416','Colour Chemical'),(7,'F Scarlet Rc','320416','Colour Chemical'),(8,'Dyeing Services','998821','Dyeing'),(9,'Adaan Baas','1401','Other Purchse'),(10,'EFFLUENT TREATMENT CHARGE','999432','OTHER'),(11,'CHROMAZOL TURQOISE BLUE G','320416','COLOUR CHEMICAL'),(12,'BLACK GDN','320416','COLOUR CHEMICAL'),(13,'Chrysopinen G','3204','Colour Chemical'),(14,'Fast Yellow GC','3204','Colour Chemical'),(15,'Yellow M4R','3204','Colour Chemical'),(16,'Red M5B Crude','320416','Colour Chemical'),(17,'Golden Yellow MERL','320416','Colour Chemical'),(18,'Sodium Nitrate','28341010','Chemical'),(19,'Turqioise Blue  H5G RE','3204','Colour Chemical'),(20,'Naphtol ASBS','3204','Colour Chemical'),(21,'Naphtol ASG','3204','Colour Chemical'),(22,'BLUE MR RE','320416','Colour Chemical'),(23,'2908 IMR LFF50%','34029099','CHEMICAL'),(24,'SALT','-','CHEMICAL'),(25,'LDP','3809900','Chemical'),(26,'DL30 DESIZE','35079010','Chemical'),(27,'MR 369 MERASIN','38099190','CHEMICAL'),(28,'VARIOUS OM MACHINERY','-','OTHER'),(29,'No. 24 Vardhaman Cotton yarn','5204','Other'),(30,'Yellow CRD RE','320416','Colour Chemical'),(31,'Naphtol AS H/C','3204','Colour Chemical'),(32,'F Red B Base','3204','Colour Chemical'),(33,'Black N-150 H/C','320416','Colour Chemical'),(34,'Lemon WLT','320416','Colour Chemical'),(35,'No. 10 Vardhaman Thread','5204','Other'),(36,'Orange M2R','32041620','Colour Chemical');
/*!40000 ALTER TABLE `prod_master` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-27  8:10:22
