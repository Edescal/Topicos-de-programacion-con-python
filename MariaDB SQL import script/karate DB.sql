-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         11.5.2-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para karate
DROP DATABASE IF EXISTS `karate`;
CREATE DATABASE IF NOT EXISTS `karate` /*!40100 DEFAULT CHARACTER SET armscii8 COLLATE armscii8_bin */;
USE `karate`;

-- Volcando estructura para tabla karate.alumnos
DROP TABLE IF EXISTS `alumnos`;
CREATE TABLE IF NOT EXISTS `alumnos` (
  `ID_alumno` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Nombres` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Apellido_paterno` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Apellido_materno` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Edad` int(11) unsigned NOT NULL,
  `Fecha_nac` date NOT NULL,
  `Asistencias` int(11) unsigned NOT NULL,
  `ID_cinta` int(11) unsigned NOT NULL,
  `ID_estatus` int(11) unsigned NOT NULL,
  `ID_user` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci DEFAULT NULL,
  PRIMARY KEY (`ID_alumno`),
  KEY `FK_alumnos_cintas` (`ID_cinta`),
  KEY `FK_alumnos_estatus` (`ID_estatus`),
  KEY `FK_alumnos_users` (`ID_user`),
  CONSTRAINT `FK_alumnos_cintas` FOREIGN KEY (`ID_cinta`) REFERENCES `cintas` (`ID_cinta`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_alumnos_estatus` FOREIGN KEY (`ID_estatus`) REFERENCES `estatus` (`ID_estatus`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_alumnos_users` FOREIGN KEY (`ID_user`) REFERENCES `users` (`Username`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.alumnos: ~5 rows (aproximadamente)
DELETE FROM `alumnos`;
INSERT INTO `alumnos` (`ID_alumno`, `Nombres`, `Apellido_paterno`, `Apellido_materno`, `Edad`, `Fecha_nac`, `Asistencias`, `ID_cinta`, `ID_estatus`, `ID_user`) VALUES
	(3, 'Eduardo', 'Escalante', 'Pacheco', 14, '2010-08-15', 3, 8, 1, 'admin'),
	(4, 'Carlos Eduardo', 'Bojórquez', 'Ruiz', 19, '2005-07-07', 0, 1, 1, 'admin'),
	(5, 'Fernando', 'Pech', 'Martínez', 18, '2006-10-07', 0, 1, 1, 'admin'),
	(6, 'Carlos Eduardo', 'Valencia', 'Hernández', 21, '2003-10-09', 0, 2, 2, 'admin'),
	(7, 'Fernando Ignacio', 'Bojórquez', 'Pacheco', 13, '2011-06-21', 0, 6, 2, 'admin');

-- Volcando estructura para tabla karate.asistencias
DROP TABLE IF EXISTS `asistencias`;
CREATE TABLE IF NOT EXISTS `asistencias` (
  `ID_asistencia` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL,
  `ID_alumno` int(11) unsigned NOT NULL,
  `ID_clase` int(11) unsigned NOT NULL,
  PRIMARY KEY (`ID_asistencia`),
  KEY `FK_asistencias_alumnos` (`ID_alumno`),
  KEY `FK_asistencias_clases` (`ID_clase`),
  CONSTRAINT `FK_asistencias_alumnos` FOREIGN KEY (`ID_alumno`) REFERENCES `alumnos` (`ID_alumno`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_asistencias_clases` FOREIGN KEY (`ID_clase`) REFERENCES `clases` (`ID_clase`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.asistencias: ~3 rows (aproximadamente)
DELETE FROM `asistencias`;
INSERT INTO `asistencias` (`ID_asistencia`, `Fecha`, `ID_alumno`, `ID_clase`) VALUES
	(5, '2024-10-07', 3, 1),
	(6, '2024-10-02', 3, 7),
	(7, '2024-10-08', 3, 4);

-- Volcando estructura para tabla karate.cintas
DROP TABLE IF EXISTS `cintas`;
CREATE TABLE IF NOT EXISTS `cintas` (
  `ID_cinta` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Color` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  PRIMARY KEY (`ID_cinta`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.cintas: ~8 rows (aproximadamente)
DELETE FROM `cintas`;
INSERT INTO `cintas` (`ID_cinta`, `Color`) VALUES
	(1, 'Blanco'),
	(2, 'Amarillo'),
	(3, 'Naranja'),
	(4, 'Morado'),
	(5, 'Azúl'),
	(6, 'Verde'),
	(7, 'Café'),
	(8, 'Rojo'),
	(9, 'Negro');

-- Volcando estructura para tabla karate.clases
DROP TABLE IF EXISTS `clases`;
CREATE TABLE IF NOT EXISTS `clases` (
  `ID_clase` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ID_dia_semana` int(11) unsigned NOT NULL,
  `ID_hora` int(11) unsigned NOT NULL,
  PRIMARY KEY (`ID_clase`),
  KEY `FK_clases_dias_semana` (`ID_dia_semana`),
  KEY `FK_clases_horas` (`ID_hora`),
  CONSTRAINT `FK_clases_dias_semana` FOREIGN KEY (`ID_dia_semana`) REFERENCES `dias_semana` (`ID_dia`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_clases_horas` FOREIGN KEY (`ID_hora`) REFERENCES `horas` (`ID_hora`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.clases: ~15 rows (aproximadamente)
DELETE FROM `clases`;
INSERT INTO `clases` (`ID_clase`, `ID_dia_semana`, `ID_hora`) VALUES
	(1, 1, 16),
	(2, 1, 18),
	(3, 1, 20),
	(4, 2, 18),
	(5, 2, 20),
	(6, 3, 16),
	(7, 3, 18),
	(8, 3, 20),
	(9, 4, 18),
	(10, 4, 20),
	(11, 5, 18),
	(12, 5, 20),
	(13, 6, 14),
	(14, 6, 16),
	(15, 6, 18);

-- Volcando estructura para tabla karate.dias_semana
DROP TABLE IF EXISTS `dias_semana`;
CREATE TABLE IF NOT EXISTS `dias_semana` (
  `ID_dia` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Dia` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  PRIMARY KEY (`ID_dia`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.dias_semana: ~7 rows (aproximadamente)
DELETE FROM `dias_semana`;
INSERT INTO `dias_semana` (`ID_dia`, `Dia`) VALUES
	(1, 'Lunes'),
	(2, 'Martes'),
	(3, 'Miércoles'),
	(4, 'Jueves'),
	(5, 'Viernes'),
	(6, 'Sábado'),
	(7, 'Domingo');

-- Volcando estructura para tabla karate.estatus
DROP TABLE IF EXISTS `estatus`;
CREATE TABLE IF NOT EXISTS `estatus` (
  `ID_estatus` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.estatus: ~3 rows (aproximadamente)
DELETE FROM `estatus`;
INSERT INTO `estatus` (`ID_estatus`, `Descripcion`) VALUES
	(1, 'ACTIVO'),
	(2, 'PENDIENTE'),
	(3, 'BAJA');

-- Volcando estructura para tabla karate.historial_abonos
DROP TABLE IF EXISTS `historial_abonos`;
CREATE TABLE IF NOT EXISTS `historial_abonos` (
  `ID_abono` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Fecha_abono` date NOT NULL,
  `ID_pago_alumno` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ID_abono`),
  KEY `FK_historial_abonos_pago_alumno` (`ID_pago_alumno`),
  CONSTRAINT `FK_historial_abonos_pago_alumno` FOREIGN KEY (`ID_pago_alumno`) REFERENCES `pago_alumno` (`ID_pago_alumno`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.historial_abonos: ~1 rows (aproximadamente)
DELETE FROM `historial_abonos`;
INSERT INTO `historial_abonos` (`ID_abono`, `Fecha_abono`, `ID_pago_alumno`) VALUES
	(1, '2024-10-01', 1);

-- Volcando estructura para tabla karate.historial_adeudos
DROP TABLE IF EXISTS `historial_adeudos`;
CREATE TABLE IF NOT EXISTS `historial_adeudos` (
  `ID_adeudo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Fecha_adeudo` date NOT NULL,
  `ID_pago_alumno` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ID_adeudo`),
  KEY `FK_historial_adeudos_pago_alumno` (`ID_pago_alumno`),
  CONSTRAINT `FK_historial_adeudos_pago_alumno` FOREIGN KEY (`ID_pago_alumno`) REFERENCES `pago_alumno` (`ID_pago_alumno`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.historial_adeudos: ~0 rows (aproximadamente)
DELETE FROM `historial_adeudos`;

-- Volcando estructura para tabla karate.horas
DROP TABLE IF EXISTS `horas`;
CREATE TABLE IF NOT EXISTS `horas` (
  `ID_hora` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Hora` varchar(5) NOT NULL DEFAULT '00:00',
  PRIMARY KEY (`ID_hora`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.horas: ~24 rows (aproximadamente)
DELETE FROM `horas`;
INSERT INTO `horas` (`ID_hora`, `Hora`) VALUES
	(1, '01:00'),
	(2, '02:00'),
	(3, '03:00'),
	(4, '04:00'),
	(5, '05:00'),
	(6, '06:00'),
	(7, '07:00'),
	(8, '08:00'),
	(9, '09:00'),
	(10, '10:00'),
	(11, '11:00'),
	(12, '12:00'),
	(13, '13:00'),
	(14, '14:00'),
	(15, '15:00'),
	(16, '16:00'),
	(17, '17:00'),
	(18, '18:00'),
	(19, '19:00'),
	(20, '20:00'),
	(21, '21:00'),
	(22, '22:00'),
	(23, '23:00'),
	(24, '24:00');

-- Volcando estructura para tabla karate.pagos
DROP TABLE IF EXISTS `pagos`;
CREATE TABLE IF NOT EXISTS `pagos` (
  `ID_pago` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Monto` decimal(20,6) unsigned NOT NULL,
  `Fecha_pago` date NOT NULL,
  `Fecha_corte` date NOT NULL,
  PRIMARY KEY (`ID_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.pagos: ~1 rows (aproximadamente)
DELETE FROM `pagos`;
INSERT INTO `pagos` (`ID_pago`, `Monto`, `Fecha_pago`, `Fecha_corte`) VALUES
	(1, 300.000000, '2024-10-07', '2024-11-01');

-- Volcando estructura para tabla karate.pago_alumno
DROP TABLE IF EXISTS `pago_alumno`;
CREATE TABLE IF NOT EXISTS `pago_alumno` (
  `ID_pago_alumno` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Abono` decimal(20,6) unsigned NOT NULL,
  `Adeudo` decimal(20,6) unsigned NOT NULL,
  `Meses_abono` int(10) unsigned NOT NULL,
  `Meses_adeudo` int(10) unsigned NOT NULL,
  `Estatus` int(10) unsigned NOT NULL,
  `ID_pago` int(10) unsigned NOT NULL,
  `ID_alumno` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ID_pago_alumno`),
  KEY `FK_pago_alumno_alumnos` (`ID_alumno`),
  KEY `FK_pago_alumno_pagos` (`ID_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.pago_alumno: ~1 rows (aproximadamente)
DELETE FROM `pago_alumno`;
INSERT INTO `pago_alumno` (`ID_pago_alumno`, `Abono`, `Adeudo`, `Meses_abono`, `Meses_adeudo`, `Estatus`, `ID_pago`, `ID_alumno`) VALUES
	(1, 300.000000, 0.000000, 1, 0, 1, 1, 3);

-- Volcando estructura para tabla karate.telefonos
DROP TABLE IF EXISTS `telefonos`;
CREATE TABLE IF NOT EXISTS `telefonos` (
  `ID_telefono` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Numero` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_telefono`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.telefonos: ~5 rows (aproximadamente)
DELETE FROM `telefonos`;
INSERT INTO `telefonos` (`ID_telefono`, `Numero`) VALUES
	(3, '9999999889'),
	(4, '9992948522'),
	(5, '9983235322'),
	(6, '9992939232'),
	(7, '9999912443');

-- Volcando estructura para tabla karate.users
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `Username` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Password` varchar(162) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `Nombres` varchar(25) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Apellido_paterno` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Apellido_materno` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_spanish_ci NOT NULL,
  `Fecha_creacion` date NOT NULL DEFAULT curdate(),
  PRIMARY KEY (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=armscii8 COLLATE=armscii8_bin;

-- Volcando datos para la tabla karate.users: ~1 rows (aproximadamente)
DELETE FROM `users`;
INSERT INTO `users` (`Username`, `Password`, `Email`, `Nombres`, `Apellido_paterno`, `Apellido_materno`, `Fecha_creacion`) VALUES
	('admin', 'scrypt:32768:8:1$1NmgiKEmquxHg2Kj$d634bd568c7e53cd81170f8d3d48cc280434a5613e6611ed42beb11eeef97e7a1d09edbb67f845be23bc86e1cdf4b484e65d46d2277d0463bd4b34abc4352514', 'admin@senshi.karate.com', 'Narcisso', 'Anasui', 'Brando', '2000-08-15');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
