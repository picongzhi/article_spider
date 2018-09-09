/*
 Navicat Premium Data Transfer

 Source Server         : docker-mysql
 Source Server Type    : MySQL
 Source Server Version : 50722
 Source Host           : localhost:3306
 Source Schema         : article_spider

 Target Server Type    : MySQL
 Target Server Version : 50722
 File Encoding         : 65001

 Date: 09/09/2018 11:50:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for jobbole_article
-- ----------------------------
DROP TABLE IF EXISTS `jobbole_article`;
CREATE TABLE `jobbole_article` (
  `title` varchar(200) NOT NULL,
  `create_date` date DEFAULT NULL,
  `url` varchar(300) NOT NULL,
  `url_object_id` varchar(50) NOT NULL,
  `front_image_url` varchar(300) DEFAULT NULL,
  `front_image_path` varchar(200) DEFAULT NULL,
  `comment_nums` int(11) NOT NULL,
  `fav_nums` int(11) NOT NULL,
  `praise_nums` int(11) NOT NULL,
  `tags` varchar(200) DEFAULT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`url_object_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
