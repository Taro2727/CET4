-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: cet4
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cursos`
--

DROP TABLE IF EXISTS `cursos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cursos` (
  `id_cur` int NOT NULL AUTO_INCREMENT,
  `nom_cur` varchar(20) NOT NULL,
  `id_mod` int DEFAULT NULL,
  PRIMARY KEY (`id_cur`),
  KEY `fk_cursos_modalidad` (`id_mod`),
  CONSTRAINT `fk_cursos_modalidad` FOREIGN KEY (`id_mod`) REFERENCES `modalidad` (`id_mod`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cursos`
--

LOCK TABLES `cursos` WRITE;
/*!40000 ALTER TABLE `cursos` DISABLE KEYS */;
INSERT INTO `cursos` VALUES (1,'4to',1),(2,'4to',2),(3,'5to',1),(4,'5to',2),(5,'6to',1),(6,'6to',2),(7,'7mo',1),(8,'7mo',2);
/*!40000 ALTER TABLE `cursos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materias`
--

DROP TABLE IF EXISTS `materias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias` (
  `id_mat` int NOT NULL AUTO_INCREMENT,
  `nom_mat` varchar(30) NOT NULL,
  `id_cur` int DEFAULT NULL,
  PRIMARY KEY (`id_mat`),
  KEY `fk_materias_cursos` (`id_cur`),
  CONSTRAINT `fk_materias_cursos` FOREIGN KEY (`id_cur`) REFERENCES `cursos` (`id_cur`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias`
--

LOCK TABLES `materias` WRITE;
/*!40000 ALTER TABLE `materias` DISABLE KEYS */;
INSERT INTO `materias` VALUES (1,'lab_apps',1),(2,'lab_so',1),(3,'lab_hard',1),(4,'lab_prog',1),(5,'electronica',1),(6,'lab_apps',2),(7,'lab_so',2),(8,'lab_hard',2),(9,'lab_prog',2),(10,'electronica',2),(11,'lab_prog',3),(12,'lab_diseñoweb',3),(13,'sistemas_digitales',3),(14,'lab_bd',3),(15,'lab_redes',3),(16,'mod_sist',3),(17,'teleinform',4),(18,'lab_so',4),(19,'sistemas_digitales',4),(20,'lab_hard',4),(21,'lab_prog',4),(22,'lab_app',4),(23,'sist_gestion',5),(24,'web_dinam',5),(25,'sistemas_digitales',5),(26,'seg_inf',5),(27,'lab_prog',5),(28,'proc_ind',5),(29,'web_estat',5),(30,'lab_prog',6),(31,'lab_app',6),(32,'sistemas_digitales',6),(33,'inv_operativa',6),(34,'lab_hard',6),(35,'seg_inf',6),(36,'lab_so',6),(37,'org_metodos',7),(38,'modelos_sis',7),(39,'empr_prod_dl',7),(40,'eval_pytos',7),(41,'pyto_sistwd',7),(42,'pdi_sist_comp',7),(43,'pd_soft_p_mov',7),(44,'pract_prof',7),(45,'pyto_sis',8),(46,'myr_redes',8),(47,'mod_sist',8),(48,'eval_pytos',8),(49,'myr_sist',8),(50,'bd',8),(51,'empr_prod_dl',8),(52,'pract_prof',8);
/*!40000 ALTER TABLE `materias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modalidad`
--

DROP TABLE IF EXISTS `modalidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modalidad` (
  `id_mod` int NOT NULL AUTO_INCREMENT,
  `nom_mod` varchar(50) NOT NULL,
  PRIMARY KEY (`id_mod`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modalidad`
--

LOCK TABLES `modalidad` WRITE;
/*!40000 ALTER TABLE `modalidad` DISABLE KEYS */;
INSERT INTO `modalidad` VALUES (1,'Programacion'),(2,'informatica');
/*!40000 ALTER TABLE `modalidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preg`
--

DROP TABLE IF EXISTS `preg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preg` (
  `id_post` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(100) NOT NULL,
  `cont` text NOT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `id_usu` int DEFAULT NULL,
  `id_mat` int DEFAULT NULL,
  PRIMARY KEY (`id_post`),
  KEY `fk_post_usuario` (`id_usu`),
  KEY `fk_post_materias` (`id_mat`),
  CONSTRAINT `fk_post_materias` FOREIGN KEY (`id_mat`) REFERENCES `materias` (`id_mat`),
  CONSTRAINT `fk_post_usuario` FOREIGN KEY (`id_usu`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preg`
--

LOCK TABLES `preg` WRITE;
/*!40000 ALTER TABLE `preg` DISABLE KEYS */;
/*!40000 ALTER TABLE `preg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rta`
--

DROP TABLE IF EXISTS `rta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rta` (
  `id_com` int NOT NULL AUTO_INCREMENT,
  `cont` text NOT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `id_post` int DEFAULT NULL,
  `id_usu` int DEFAULT NULL,
  PRIMARY KEY (`id_com`),
  KEY `fk_com_post` (`id_post`),
  KEY `fk_com_postusu` (`id_usu`),
  CONSTRAINT `fk_com_post` FOREIGN KEY (`id_post`) REFERENCES `preg` (`id_post`),
  CONSTRAINT `fk_com_postusu` FOREIGN KEY (`id_usu`) REFERENCES `preg` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rta`
--

LOCK TABLES `rta` WRITE;
/*!40000 ALTER TABLE `rta` DISABLE KEYS */;
/*!40000 ALTER TABLE `rta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usu` int NOT NULL AUTO_INCREMENT,
  `nom_usu` varchar(30) NOT NULL,
  `email` varchar(50) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  PRIMARY KEY (`id_usu`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'TaylorSwift123','chau@gmail.com','hola'),(3,'hola','chauchi@gmail.com','hola'),(4,'intento123','iasgd@gmail.com','miedo'),(5,'pepeargento','hahga@gmail.com','hola'),(9,'monicaragento','moni@gmail.com','123');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usumod`
--

DROP TABLE IF EXISTS `usumod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usumod` (
  `id_usu` int NOT NULL,
  `id_mod` int NOT NULL,
  PRIMARY KEY (`id_usu`,`id_mod`),
  KEY `fk_modalidad_usumod` (`id_mod`),
  CONSTRAINT `fk_modalidad_usumod` FOREIGN KEY (`id_mod`) REFERENCES `modalidad` (`id_mod`),
  CONSTRAINT `fk_usumod_usuario` FOREIGN KEY (`id_usu`) REFERENCES `usuario` (`id_usu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usumod`
--

LOCK TABLES `usumod` WRITE;
/*!40000 ALTER TABLE `usumod` DISABLE KEYS */;
/*!40000 ALTER TABLE `usumod` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-19  0:16:32
