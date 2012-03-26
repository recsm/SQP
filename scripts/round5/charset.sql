-- MySQL dump 10.13  Distrib 5.1.41, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: sqp
-- ------------------------------------------------------
-- Server version	5.1.41-3ubuntu12.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `sqp_characteristicset_branches`
--

DROP TABLE IF EXISTS `sqp_characteristicset_branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sqp_characteristicset_branches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `characteristicset_id` int(11) NOT NULL,
  `branch_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `characteristicset_id` (`characteristicset_id`,`branch_id`),
  KEY `branch_id_refs_id_7d0f4ce1` (`branch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12112 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sqp_characteristicset_branches`
--

LOCK TABLES `sqp_characteristicset_branches` WRITE;
/*!40000 ALTER TABLE `sqp_characteristicset_branches` DISABLE KEYS */;
INSERT INTO `sqp_characteristicset_branches` VALUES (4,2), (4,3), (4,4), (4,10), (4,11), (4,12), (4,13), (4,14), (4,16), (4,17), (4,18), (4,19), (4,20), (4,21), (4,22), (4,24), (4,25), (4,26), (4,27), (4,28), (4,29), (4,30), (4,31), (4,32), (4,33), (4,34), (4,35), (4,36), (4,37), (4,38), (4,39), (4,40), (4,41), (4,42), (4,43), (4,44), (4,45), (4,46), (4,47), (4,48), (4,49), (4,50), (4,51), (4,52), (4,53), (4,54), (4,55), (4,56), (4,57), (4,58), (4,59), (4,60), (4,61), (4,62), (4,63), (4,64), (4,65), (4,66), (4,67), (4,68), (4,69), (4,70), (4,71), (4,72), (4,73), (4,74), (4,75), (4,76), (4,77), (4,78), (4,79), (4,80), (4,81), (4,82), (4,83), (4,84), (4,85), (4,86), (4,87), (4,88), (4,89), (4,90), (4,91), (4,92), (4,93), (4,94), (4,95), (4,96), (4,97), (4,98), (4,99), (4,100), (4,101), (4,102), (4,103), (4,104), (4,105), (4,106), (4,107), (4,108), (4,109), (4,110), (4,111), (4,112), (4,113), (4,114), (4,115), (4,116), (4,117), (4,118), (4,119), (4,120), (4,121), (4,122), (4,123), (4,124), (4,125), (4,126), (4,127), (4,128), (4,129), (4,130), (4,131), (4,132), (4,133), (4,134), (4,135), (4,136), (4,137), (4,138), (4,139), (4,140), (4,141), (4,142), (4,143), (4,144), (4,145), (4,146), (4,147), (4,148), (4,149), (4,150), (4,151), (4,152), (4,153), (4,154), (4,155), (4,156), (4,157), (4,158), (4,159), (4,160), (4,161), (4,162), (4,163), (4,164), (4,165), (4,166), (4,167), (4,168), (4,169), (4,170), (4,171), (4,172), (4,173), (4,174), (4,175), (4,176), (4,177), (4,178), (4,179), (4,180), (4,181), (4,182), (4,183), (4,184), (4,185), (4,186), (4,187), (4,188), (4,189), (4,190), (4,191), (4,192), (4,193), (4,194), (4,196), (4,197), (4,198), (4,199), (4,200), (4,201), (4,202), (4,203), (4,204), (4,205), (4,206), (4,207), (4,210), (4,211), (4,212), (4,213), (4,214), (4,215), (4,216), (4,217), (4,218), (4,219), (4,220), (4,221), (4,222), (4,223), (4,224), (4,225), (4,226), (4,227), (4,230), (4,231), (4,232), (4,233), (4,234), (4,235), (4,236), (4,237), (4,238), (4,239), (4,240), (4,241), (4,242), (4,243), (4,244), (4,245), (4,246), (4,247), (4,248), (4,249), (4,250), (4,251), (4,252), (4,253), (4,254), (4,255), (4,256), (4,257), (4,258), (4,260), (4,261), (4,262), (4,263), (4,264), (4,265), (4,266), (4,267), (4,268), (4,270), (4,271), (4,272), (4,273), (4,274), (4,275), (4,276), (4,277), (4,278), (4,279), (4,280), (4,281), (4,282), (4,283), (4,284), (4,285), (4,286), (4,287), (4,288), (4,289), (4,290), (4,291), (4,292), (4,293), (4,294), (4,295); 


/*!40000 ALTER TABLE `sqp_characteristicset_branches` ENABLE KEYS */; UNLOCK TABLES; /*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */; 
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-07-08 12:31:28
