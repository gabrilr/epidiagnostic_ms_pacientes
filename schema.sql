-- Schema DDL para el Microservicio de pacientes (EpiDiagnostic-Maya)
-- Motor de Base de Datos: MySQL / MariaDB

CREATE DATABASE IF NOT EXISTS pacientes_db;
USE pacientes_db;

-- -------------------------------------------------------------
-- Tabla: pacientes
-- -------------------------------------------------------------
CREATE TABLE `pacientes` (
  `id` CHAR(36) NOT NULL,
  `curp` VARCHAR(18) NOT NULL,
  `nombre_completo` VARCHAR(255) NOT NULL,
  `fecha_nacimiento` DATE NOT NULL,
  `sexo` VARCHAR(1) NOT NULL,
  `comunidad` VARCHAR(255) NOT NULL,
  `municipio` VARCHAR(255) NOT NULL,
  `lengua_materna` VARCHAR(100) DEFAULT NULL,
  `contacto_emergencia` VARCHAR(255) DEFAULT NULL,
  `device_generated_id` VARCHAR(36) DEFAULT NULL,
  `creado_en` DATETIME NOT NULL,
  `actualizado_en` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_pacientes_curp` (`curp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Tabla: antecedentes_medicos
-- -------------------------------------------------------------
CREATE TABLE `antecedentes_medicos` (
  `id` CHAR(36) NOT NULL,
  `paciente_id` CHAR(36) NOT NULL,
  `descripcion` VARCHAR(500) NOT NULL,
  `tipo` VARCHAR(50) NOT NULL,
  `fecha_registro` DATETIME NOT NULL,
  `origen_atencion_id` VARCHAR(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_antecedentes_medicos_paciente_id` (`paciente_id`),
  CONSTRAINT `antecedentes_medicos_ibfk_1` FOREIGN KEY (`paciente_id`) REFERENCES `pacientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Tabla: personal_medico
-- -------------------------------------------------------------
CREATE TABLE `personal_medico` (
  `id` CHAR(36) NOT NULL,
  `nombre_completo` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(20) NOT NULL,
  `comunidad` VARCHAR(255) NOT NULL,
  `municipio` VARCHAR(255) NOT NULL,
  `cedula_profesional` VARCHAR(50) DEFAULT NULL,
  `correo` VARCHAR(255) NOT NULL,
  `contrasena_hash` VARCHAR(255) NOT NULL,
  `activo` TINYINT(1) NOT NULL,
  `creado_en` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_personal_medico_correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Tabla: solicitudes_premium
-- -------------------------------------------------------------
CREATE TABLE `solicitudes_premium` (
  `id` CHAR(36) NOT NULL,
  `personal_id` CHAR(36) NOT NULL,
  `numero_cedula` VARCHAR(10) NOT NULL,
  `nombre_en_cedula` VARCHAR(200) NOT NULL,
  `especialidad` VARCHAR(100) DEFAULT NULL,
  `estado` ENUM('pendiente', 'aprobada', 'rechazada') NOT NULL DEFAULT 'pendiente',
  `admin_id` CHAR(36) DEFAULT NULL,
  `motivo_rechazo` TEXT DEFAULT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_solicitudes_premium_personal_id` (`personal_id`),
  KEY `ix_solicitudes_premium_admin_id` (`admin_id`),
  CONSTRAINT `solicitudes_premium_ibfk_1` FOREIGN KEY (`personal_id`) REFERENCES `personal_medico` (`id`),
  CONSTRAINT `solicitudes_premium_ibfk_2` FOREIGN KEY (`admin_id`) REFERENCES `personal_medico` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
