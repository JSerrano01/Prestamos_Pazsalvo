-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-08-2021 a las 00:05:00
-- Versión del servidor: 10.4.18-MariaDB
-- Versión de PHP: 7.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `flaskdb`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `id` int(255) NOT NULL,
  `fecha` date NOT NULL DEFAULT current_timestamp(),
  `nombre` varchar(255) NOT NULL,
  `cedula` varchar(255) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `depSolicitante` varchar(255) NOT NULL,
  `depPrestamo` varchar(255) NOT NULL,
  `prestamo` varchar(255) NOT NULL,
  `estado` varchar(255) NOT NULL,
  `observaciones` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `registros`
--

INSERT INTO `registros` (`id`, `fecha`, `nombre`, `cedula`, `correo`, `depSolicitante`, `depPrestamo`, `prestamo`, `estado`, `observaciones`) VALUES
(6, '2021-08-09', 'Juan', '1036651490', '', 'BIENESTAR INSTITUCIONAL', 'TECNOLOGIA DE INFORMACION Y COMUNICACION', 'Balón', 'Activo', ''),
(25, '2021-08-09', 'JUAN PABLO ROJAS MARIN', '1036651490', 'juan.rojas@colmayor.edu.co', 'TECNOLOGIA DE INFORMACION Y COMUNICACION', 'TECNOLOGIA DE INFORMACION Y COMUNICACION', 'Aula: C306 Horario: 4:00 p. m. - 6:00 p. m.', '2', 'Ninguna');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `dependencia` varchar(255) NOT NULL,
  `permisos` varchar(255) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id`, `nombre`, `email`, `password`, `dependencia`, `permisos`) VALUES
(1, 'Juan Pablo Rojas', 'juanrojasm21@gmail.com', '$2b$12$3EQtflyDQS/HAfZ8Uj6lSuml42lRj.xmvLvkqsVr72VC2Ed8.Zmd6', 'TECNOLOGIA DE INFORMACION Y COMUNICACION', 'admin'),
(2, 'Pedro Perez', 'pedro@gmail.com', '$2b$12$3EQtflyDQS/HAfZ8Uj6lSuml42lRj.xmvLvkqsVr72VC2Ed8.Zmd6', 'BIENESTAR INSTITUCIONAL', 'user');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `id` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
