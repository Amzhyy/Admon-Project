-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema admon_project
-- -----------------------------------------------------
-- save
-- 

-- -----------------------------------------------------
-- Schema admon_project
--
-- save
-- 
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `admon_project` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `admon_project` ;

-- -----------------------------------------------------
-- Table `admon_project`.`campaign`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admon_project`.`campaign` (
  `id_campaign` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `attack_type` ENUM('password_reset', 'fake_invoice', 'urgent_request', 'survey_reward', 'attachment_malware') NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `stauts` ENUM('active', 'finished') NOT NULL,
  PRIMARY KEY (`id_campaign`),
  UNIQUE INDEX `id_campaign_UNIQUE` (`id_campaign` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `admon_project`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admon_project`.`user` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(60) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `rol` ENUM('admin', 'analyst', 'marketing') NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_user`),
  UNIQUE INDEX `id_user_UNIQUE` (`id_user` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `admon_project`.`email`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admon_project`.`email` (
  `id_email` INT NOT NULL AUTO_INCREMENT,
  `id_user` INT NOT NULL,
  `id_campaign` INT NOT NULL,
  PRIMARY KEY (`id_email`),
  UNIQUE INDEX `id_email_UNIQUE` (`id_email` ASC) VISIBLE,
  INDEX `id_user_idx` (`id_user` ASC) VISIBLE,
  INDEX `id_campaign_idx` (`id_campaign` ASC) VISIBLE,
  CONSTRAINT `id_campaign`
    FOREIGN KEY (`id_campaign`)
    REFERENCES `admon_project`.`campaign` (`id_campaign`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `id_user`
    FOREIGN KEY (`id_user`)
    REFERENCES `admon_project`.`user` (`id_user`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `admon_project`.`result`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admon_project`.`result` (
  `id_result` INT NOT NULL AUTO_INCREMENT,
  `id_email` INT NOT NULL,
  `clic` INT NOT NULL,
  `report` VARCHAR(300) NOT NULL,
  PRIMARY KEY (`id_result`),
  UNIQUE INDEX `id_result_UNIQUE` (`id_result` ASC) VISIBLE,
  INDEX `id_email_idx` (`id_email` ASC) VISIBLE,
  CONSTRAINT `id_email`
    FOREIGN KEY (`id_email`)
    REFERENCES `admon_project`.`email` (`id_email`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
