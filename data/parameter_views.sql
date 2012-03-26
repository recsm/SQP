-- phpMyAdmin SQL Dump
-- version 3.4.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Aug 09, 2011 at 12:39 PM
-- Server version: 5.1.52
-- PHP Version: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `sqp`
--

--
-- Dumping data for table `sqp_parameter`
--
INSERT INTO `sqp_parameter` VALUES 
(1,'Reliability ','Reliability of the Question',0),
(2,'Validity','Validity of the question',0),
(3,'Quality','Quality of the question',0),
(4,'Reliability Coefficient ','The reliablity coefficient for the question',0),
(5,'Validity Coefficient','The Validity Coefficient for the Question',0),
(6,'Quality Coefficient','The Quality Coefficient for the Question',0),
(7,'Common method variance','r^2 * m^2',0),
(8,'Method Effect','Method Effect Coefficient',0);

--
-- Dumping data for table `sqp_prediction`
--

INSERT INTO `sqp_prediction` VALUES 
(1,1,1,'question_reliability','question_reliability'),
(2,2,1,'question_validity','question_validity'),
(3,3,1,'question_quality','question_quality'),
(4,4,1,'question_reliability_coefficient','question_reliability_coefficient'),
(5,5,1,'question_validity_coefficient','question_validity_coefficient'),
(6,6,1,'question_quality_coefficient','question_quality_coefficient'),
(7,1,2,'question_reliability_interval','question_reliability_interval'),
(8,2,2,'question_validity_interval','question_validity_interval'),
(9,3,2,'question_quality_interval','question_quality_interval'),
(10,4,2,'question_reliability_coefficient_interval','question_reliability_coefficient_interval'),
(11,5,2,'question_validity_coefficient_interval','question_validity_coefficient_interval'),
(12,6,2,'question_quality_coefficient_interval','question_quality_coefficient_interval'),
(13,7,1,'common_method_variance','common_method_variance'),
(14,7,2,'common_method_variance_interval','common_method_variance_interval'),
(15,8,1,'method_effect_coefficient','method_effect_coefficient'),
(16,8,2,'method_effect_coefficient_interval','method_effect_coefficient_interval'),
(17,6,3,'question_quality_coefficient_standard_error','question_quality_coefficient_standard_error');

--
-- Dumping data for table `sqp_view`
--
INSERT INTO `sqp_view` VALUES 
(1,'Point estimate','prediction_view_single_parameter','float',0),
(2,'Quartiles','prediction_view_interval','tuple',0),
(3,'Standard error','prediction_view_single_parameter','float',3),
(4,'MAD','prediction_view_single_parameter','float',5),
(5,'Median','prediction_view_single_parameter','float',4);