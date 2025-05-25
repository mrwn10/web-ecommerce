-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 25, 2025 at 07:37 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ecommerce_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `cart_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `price_at_add` int(250) DEFAULT NULL,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart`
--

INSERT INTO `cart` (`cart_id`, `user_id`, `product_id`, `quantity`, `price_at_add`, `added_at`) VALUES
(59, 2, 70, 1, 457, '2025-05-19 08:12:42'),
(61, 2, 52, 1, 500, '2025-05-22 00:54:10'),
(62, 10, 62, 2, 1044, '2025-05-22 00:54:30'),
(63, 2, 54, 6, 4200, '2025-05-22 00:54:53'),
(64, 2, 52, 1, 500, '2025-05-22 01:05:04');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `price_at_add` decimal(10,2) DEFAULT NULL,
  `order_status` enum('pending','processing','shipped','delivered','cancelled') DEFAULT 'pending',
  `ordered_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `user_id`, `product_id`, `quantity`, `price_at_add`, `order_status`, `ordered_at`) VALUES
(69, 2, 72, 1, 789.00, 'delivered', '2025-05-19 08:13:11'),
(70, 2, 77, 1, 999.00, 'delivered', '2025-05-19 08:13:55'),
(71, 2, 53, 1128, 225600.00, 'delivered', '2025-05-19 08:16:56'),
(73, 2, 52, 1, 500.00, 'delivered', '2025-05-19 10:12:30'),
(74, 2, 52, 1, 500.00, 'delivered', '2025-05-19 17:00:36'),
(75, 2, 92, 1, 450.00, 'delivered', '2025-05-19 17:01:00'),
(76, 2, 92, 1, 450.00, 'delivered', '2025-05-19 17:01:00'),
(77, 2, 54, 1, 700.00, 'delivered', '2025-05-19 17:02:26'),
(78, 2, 94, 1, 650.00, 'delivered', '2025-05-19 17:02:35'),
(79, 2, 52, 1, 500.00, 'delivered', '2025-05-22 00:25:29'),
(80, 2, 52, 1, 500.00, 'delivered', '2025-05-22 00:25:52'),
(81, 2, 52, 1, 500.00, 'delivered', '2025-05-22 01:04:14'),
(82, 2, 52, 3, 1500.00, 'delivered', '2025-05-22 01:06:32'),
(83, 2, 93, 2, 500.00, 'delivered', '2025-05-22 01:07:30'),
(84, 45, 92, 3, 1350.00, 'delivered', '2025-05-24 14:42:08');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `product_price` decimal(10,2) NOT NULL,
  `quantity_status` int(250) DEFAULT NULL,
  `delivery_status` varchar(250) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `image` varchar(250) DEFAULT NULL,
  `seller_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `product_name`, `description`, `product_price`, `quantity_status`, `delivery_status`, `category`, `image`, `seller_id`, `created_at`) VALUES
(52, 'Baby Boy Dinosaur Shirt & Pants', 'Baby boy dinosaur clothing, Small and Medium', 500.00, 156, NULL, 'baby_clothes_accessories', 'static\\uploads\\Baby Boy Dinosaut print Bow front, Shirt Bodysuit & Pinafore shorts.jpg', 3, '2025-05-13 03:48:28'),
(53, 'Baby Girl Spring Head Wraps', 'baby girl head wraps ribbon for girls', 200.00, 0, NULL, 'baby_clothes_accessories', 'static\\uploads\\Baby girl spring head wraps.jpg', 3, '2025-05-13 03:49:42'),
(54, 'Carton bear baby romper with hat', 'Baby romper with hat with bear design', 700.00, 581, NULL, 'baby_clothes_accessories', 'static\\uploads\\Cartoon Bear baby Romper with Hat.jpg', 3, '2025-05-13 03:51:04'),
(55, 'Cute Bear Baby Hat', 'Cute baby hat bear design', 450.00, 870, NULL, 'baby_clothes_accessories', 'static\\uploads\\Cute Bear-ear baby hat.jpg', 3, '2025-05-13 03:52:06'),
(56, 'Cute dress clothes for girls', 'Cute dress clothes for growing girls', 720.00, 608, NULL, 'baby_clothes_accessories', 'static\\uploads\\Cute Clothes for Girls.jpg', 3, '2025-05-13 03:53:36'),
(57, 'Cutesie Bootsie ruffle sock boots', 'Cute boots with ruffle socks for babies', 850.00, 0, NULL, 'baby_clothes_accessories', 'static\\uploads\\Cutesie bootsie ruffle sock boots.jpg', 3, '2025-05-13 03:54:51'),
(58, 'Floral lace bow head', 'Floral lace bow head for baby girls', 250.00, 1561, NULL, 'baby_clothes_accessories', 'static\\uploads\\Floral Lace Bow headband.jpg', 3, '2025-05-13 03:56:42'),
(59, 'Korean style baby bucket hat', 'Baby bucket hat on Korean design for babies', 445.00, 1287, NULL, 'baby_clothes_accessories', 'static\\uploads\\Korean style baby bucket hat.jpg', 3, '2025-05-13 03:57:48'),
(60, 'Little Baby Classic Hoodie Jumpsuit', 'Hoodie jumpsuit for baby', 1099.00, 998, NULL, 'baby_clothes_accessories', 'static\\uploads\\Little B\'s Classic Hoodie Jumpsuit.jpg', 3, '2025-05-13 03:59:15'),
(61, 'Short sleeve ribbed bodysuit', 'Short sleeve ribbed bodysuits for baby', 679.00, 0, NULL, 'baby_clothes_accessories', 'static\\uploads\\Short sleeve ribbed bodysuits.jpg', 3, '2025-05-13 04:01:03'),
(62, '7 in 1 Wooden Puzzle Toy', '7 in 1 wooden puzzle toy for children and growing baby', 522.00, 340, NULL, 'educational_materials', 'static\\uploads\\7 in 1 wooden puzzle toy for children.jpg', 3, '2025-05-13 04:03:44'),
(63, 'Animal Puzzle for Toddler', 'Cute animal puzzle toy for toddle', 199.00, 756, NULL, 'educational_materials', 'static\\uploads\\Animal puzzle for toddleer.jpg', 3, '2025-05-13 04:04:53'),
(64, 'Clever puzzle for kids and toddler', 'Puzzle for clever/smart kids', 499.00, 0, NULL, 'educational_materials', 'static\\uploads\\Clever Puzzle for kids.jpg', 3, '2025-05-13 04:09:19'),
(65, 'Fruits 3D flashcards', '3D flashcards with fruits content', 299.00, 499, NULL, 'educational_materials', 'static\\uploads\\Fruits 3D flashcards.jpg', 3, '2025-05-13 04:10:41'),
(66, 'Janod sweet cocoon alphabet', 'Alphabet toys for kids', 369.00, 700, NULL, 'educational_materials', 'static\\uploads\\Janod sweet cocoon alphabet.jpg', 3, '2025-05-13 04:12:14'),
(67, 'Tiny wooden baby pusher for developing kids', 'Tiny wooden baby pusher', 1299.00, 627, NULL, 'educational_materials', 'static\\uploads\\Tiny Land Wooden Baby Walker, Baby Push Walker, Montessori Walker Toy, Adjustable Speed Baby Walker for Boys and Girls, Baby Activity Center, Push Toys for Kids Development.jpg', 3, '2025-05-13 04:15:18'),
(68, 'Wooden Shape sorter for kids', 'Different wooden shape sorter for education', 399.00, 0, NULL, 'educational_materials', 'static\\uploads\\Wodoen Shape sorter for Kids.jpg', 3, '2025-05-13 04:17:01'),
(69, 'Wood Stacking Toy Pyramid', 'Wooden stacking toy with different shapes for educational kids', 259.00, 898, NULL, 'educational_materials', 'static\\uploads\\Wood stacking toy pyramid.jpg', 3, '2025-05-13 04:19:17'),
(70, 'Wooden Farming toy set', 'Wooden farming toy set for kids', 457.00, 1001, NULL, 'educational_materials', 'static\\uploads\\Wooden Farm toy set.jpg', 3, '2025-05-13 04:20:23'),
(71, 'Wooden geometric shape puzzle blocks', 'Wooden geometric shapes puzzle for educational purposes', 339.00, 710, NULL, 'educational_materials', 'static\\uploads\\Wooden geometric shape puzzle blocks.jpg', 3, '2025-05-13 04:21:46'),
(72, 'Child rocking wheel', 'Rocking wheel for children', 789.00, 306, NULL, 'nursery_furniture', 'static\\uploads\\Child rocking wheel.jpg', 3, '2025-05-13 04:23:21'),
(73, 'Convertible baby crib and for growing toddlers', 'Baby crib for growing toddlers', 1499.00, 174, NULL, 'nursery_furniture', 'static\\uploads\\Convertible baby crib and for growing toddlers.jpg', 3, '2025-05-13 04:24:08'),
(74, 'Crib nursery mobile for babies', 'Mobile crib for babies and toddlers ', 899.00, 0, NULL, 'nursery_furniture', 'static\\uploads\\Crib nursery mobile for babies.jpg', 3, '2025-05-13 04:25:41'),
(75, 'Ergonmic baby chairs', 'Baby chair for dining and alike', 560.00, 677, NULL, 'nursery_furniture', 'static\\uploads\\Ergonomics Baby chairs.jpg', 21, '2025-05-13 04:31:25'),
(76, 'Harwell Dresser changer for babies', 'Dresser changer for babies', 701.00, 220, NULL, 'nursery_furniture', 'static\\uploads\\Harwell Dresser Changer for babies.jpg', 21, '2025-05-13 04:32:23'),
(77, 'Kids and Babies indoor play gym', 'A small indoor play gym for kids and babies', 999.00, 209, NULL, 'nursery_furniture', 'static\\uploads\\Kids and Babies Indoor play gym.jpg', 21, '2025-05-13 04:33:07'),
(78, 'Piggy storage rack and riding for kids', 'Storage rack and riding for kids, piggy design', 699.00, 422, NULL, 'nursery_furniture', 'static\\uploads\\Piggy storage rack and riding for kids.jpg', 21, '2025-05-13 04:33:58'),
(79, 'Stackable bear bookshelf', 'Bear Bookshelf, stackable, kids furniture', 479.00, 570, NULL, 'nursery_furniture', 'static\\uploads\\Stackable bear bookshelf, Kids furniture.jpg', 21, '2025-05-13 04:35:18'),
(80, 'Toddler Dinosaur rocking chair', 'Rocking chair for toddler\'s dinosaur design', 788.00, 0, NULL, 'nursery_furniture', 'static\\uploads\\toddlers rocking dinosaur.jpg', 21, '2025-05-13 04:36:14'),
(81, 'Wooden cradle grows on babies', 'Wooden cradle for growing babies', 777.00, 123, NULL, 'nursery_furniture', 'static\\uploads\\Wooden Cradle grows on babies.jpg', 21, '2025-05-13 04:37:04'),
(82, 'Baby Banana Toothbrush', 'cute banana toothbrush', 120.00, 3101, NULL, 'safety_and_health', 'static\\uploads\\Baby banana tootbrush.jpg', 22, '2025-05-13 04:39:13'),
(83, 'Baby Blow Nose', 'Nose of the baby blow', 120.00, 0, NULL, 'safety_and_health', 'static\\uploads\\Baby blow nose.jpg', 22, '2025-05-13 04:39:54'),
(84, 'Baby Care and Essentials', 'baby kits in 1 package', 490.00, 2313, NULL, 'safety_and_health', 'static\\uploads\\Baby care and essentials.jpg', 22, '2025-05-13 04:40:25'),
(85, 'Baby Lotions', 'Diddies strongest equipment', 120.00, 403, NULL, 'safety_and_health', 'static\\uploads\\Baby lotions.jpg', 22, '2025-05-13 04:41:18'),
(86, 'Baby Nasal Aspirator', 'baby nose aspirator', 320.00, 1230, NULL, 'safety_and_health', 'static\\uploads\\Baby nasal aspirator.jpg', 22, '2025-05-13 04:41:44'),
(87, 'Baby Plastic Bathub', 'portable bathub', 850.00, 302, NULL, 'safety_and_health', 'static\\uploads\\Baby plastic bathtub.jpg', 22, '2025-05-13 04:42:16'),
(88, 'Baby Wipes', 'wipes of the baby cutie patootie 123', 49.00, 3094, NULL, 'safety_and_health', 'static\\uploads\\Baby wipes.jpg', 22, '2025-05-13 04:42:51'),
(89, 'Cotton Bee Back Harness', 'cotton bee back harness for babies 4-8 years old', 240.00, 2139, NULL, 'safety_and_health', 'static\\uploads\\Cotton Bee back harness for babies.jpg', 22, '2025-05-13 04:43:36'),
(90, 'Knee Pads for Babies', 'knee grow goods for kids', 320.00, 0, NULL, 'safety_and_health', 'static\\uploads\\Cotton knee pads for babies.jpg', 22, '2025-05-13 04:44:21'),
(91, 'Medicine Injecting Pacifier', 'pacifier for kids cute', 320.00, 2311, NULL, 'safety_and_health', 'static\\uploads\\Medicine injecting pacifier for babies.jpg', 22, '2025-05-13 04:44:53'),
(92, 'Baby Car Seat Belt', 'Fasten the seat belt of your babies!', 450.00, 95, NULL, 'strollers_gears', 'static\\uploads\\Baby car seatbelt.jpg', 15, '2025-05-13 04:48:25'),
(93, 'Baby Carrier', 'Cary your baby with ease', 250.00, 198, NULL, 'strollers_gears', 'static\\uploads\\Baby carrier.jpg', 15, '2025-05-13 04:49:07'),
(94, 'Bike stroller', 'Can be used when you\'re outside', 650.00, 99, NULL, 'strollers_gears', 'static\\uploads\\Bike stroller for toddlers.jpg', 15, '2025-05-13 04:51:15'),
(95, 'Blue jeep Stroller', 'Can be used when you\'re outside', 800.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Blue jeep stroller.jpg', 15, '2025-05-13 04:52:13'),
(96, 'Circular baby walker', 'baby mong pawalk', 200.00, 200, NULL, 'strollers_gears', 'static\\uploads\\Circular baby walker.jpg', 15, '2025-05-13 04:52:52'),
(97, 'Baby litter box', 'Automatic waste collector ni baby', 300.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Cute baby potty.jpg', 15, '2025-05-13 04:56:49'),
(98, 'Double Baby stroller', 'Stroller for your twin babies', 400.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Double baby stroller.jpg', 15, '2025-05-13 04:57:33'),
(99, 'Double deck stroller', 'Just like your bed', 450.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Double Deck stroller.jpg', 15, '2025-05-13 04:58:21'),
(100, 'Baby\'s personal toilet', 'Baby\'s Personal toilet that only him can access', 450.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Fully Set baby potty.jpg', 15, '2025-05-13 05:01:55'),
(101, 'Square Baby walker', 'Help your babies to walk on their own feet', 200.00, 100, NULL, 'strollers_gears', 'static\\uploads\\Square baby walker.jpg', 15, '2025-05-13 05:03:31'),
(102, 'baby  push walkers', 'strollers', 10.00, 50, NULL, 'toys_and_games', 'static\\uploads\\Baby push walkers.jpg', 23, '2025-05-13 05:07:56'),
(103, 'Bag', 'bag for animals', 5.00, 0, NULL, 'toys_and_games', 'static\\uploads\\Bag of animals for toddlers.jpg', 23, '2025-05-13 05:08:55'),
(104, 'Bag', 'Bag for building toys', 5.00, 0, NULL, 'toys_and_games', 'static\\uploads\\Building toy blocks for kids.jpg', 23, '2025-05-13 05:09:39'),
(105, 'teddy bears', 'fluffy cotton bear', 8.00, 143, NULL, 'toys_and_games', 'static\\uploads\\Fluffy cotton bear.jpg', 23, '2025-05-13 05:10:40'),
(106, 'castle', 'folding castle', 9.00, 54, NULL, 'toys_and_games', 'static\\uploads\\Folding castle stacking toys.jpg', 23, '2025-05-13 05:11:18'),
(107, 'dinasour scooter', 'green scotter for 5-8 years old', 15.00, 57, NULL, 'toys_and_games', 'static\\uploads\\Green Dinosaur Scooter for kids.jpg', 23, '2025-05-13 05:12:06'),
(108, 'nursery playset', 'kids and baby nursery playset', 13.00, 77, NULL, 'toys_and_games', 'static\\uploads\\Kids baby nursery playset.jpg', 23, '2025-05-13 05:13:31'),
(109, 'Guitar', 'Musical instruments', 6.00, 69, NULL, 'toys_and_games', 'static\\uploads\\Musical instrument for toddlers.jpg', 23, '2025-05-13 05:14:18'),
(110, 'Car toy', 'Car tower toy', 8.00, 67, NULL, 'toys_and_games', 'static\\uploads\\Toddlers car tower toy.jpg', 23, '2025-05-13 05:14:55'),
(111, 'MIni guitar', 'Wooden instrument for kids', 12.00, 54, NULL, 'toys_and_games', 'static\\uploads\\Wooden mini instrument for kids.jpg', 23, '2025-05-13 05:15:29');

-- --------------------------------------------------------

--
-- Table structure for table `riders`
--

CREATE TABLE `riders` (
  `rider_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `earnings` decimal(10,2) NOT NULL DEFAULT 0.00,
  `total_orders` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `riders`
--

INSERT INTO `riders` (`rider_id`, `user_id`, `earnings`, `total_orders`) VALUES
(1, 4, 2100.00, 29),
(2, 20, 200.00, 3),
(3, 13, 200.00, 4);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `account_status` enum('active','restricted','banned') NOT NULL DEFAULT 'active',
  `restricted_at` timestamp NULL DEFAULT NULL,
  `restriction_days` int(11) NOT NULL DEFAULT 7,
  `role` enum('buyer','seller','admin','rider') DEFAULT 'buyer',
  `province` varchar(255) DEFAULT NULL,
  `municipal` varchar(255) DEFAULT NULL,
  `barangay` varchar(255) DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `failed_attempts` int(11) NOT NULL DEFAULT 0,
  `last_failed_attempt` datetime DEFAULT NULL,
  `account_locked_until` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `account_status`, `restricted_at`, `restriction_days`, `role`, `province`, `municipal`, `barangay`, `contact_number`, `password`, `failed_attempts`, `last_failed_attempt`, `account_locked_until`) VALUES
(1, 'marwin', 'admin@gmail.com', 'active', NULL, 7, 'admin', 'Laguna', 'Pila', 'Pansol', '09474371682', '123', 0, NULL, NULL),
(2, 'buyer', 'marwindalin1@gmail.com', 'active', NULL, 7, 'buyer', 'Laguna', 'Pila', 'Pansol', '09108735236', 'Clintl', 0, NULL, NULL),
(3, 'seller', 'ksapareto@gmail.com', 'active', NULL, 7, 'seller', 'Laguna', 'Pila', 'Pansol', '09474371682', '123', 0, NULL, NULL),
(4, 'rider', 'rider@gmail.com', 'active', NULL, 7, 'rider', 'Laguna', 'Pila', 'Pansol', '09108735230', '123', 0, NULL, NULL),
(9, 'sda', 'sadd@gmail.com', 'active', NULL, 7, 'buyer', 'Bulacan', 'Obando', 'Binuangan', '09442371682', '123', 0, NULL, NULL),
(10, 'waew', 'yo@gmail.com', 'active', NULL, 7, 'buyer', 'Laguna', 'Pila', 'Pansol', '09108735236', '123', 0, NULL, NULL),
(12, 'marwim', 'mariwn', 'active', NULL, 7, 'rider', 'paguna', 'jwwj', 'shhss', '09108735236', '12345', 0, NULL, NULL),
(13, 'nibbe', 'marwin@gmail.com', 'active', NULL, 7, 'rider', 'Laguna', 'Pila', 'Pansol', '09432371682', '123', 0, NULL, NULL),
(14, 'marwinbading', 'mark@gmail.com', 'active', NULL, 7, 'buyer', 'laguna', 'santa cruz', 'palasan', '0923456789', 'password123', 0, NULL, NULL),
(15, 'mark', 'markk@gmail.com', 'active', NULL, 7, 'seller', 'laguna', 'santa cruz', 'palasan', '09123456789', '123', 0, NULL, NULL),
(16, 'labo', 'labo@gmail.com', 'active', NULL, 7, 'buyer', 'laguna', 'santa cruz', 'patimbao', '09123456789', '123', 0, NULL, NULL),
(18, 'Cjlopez', 'lop@gmail.com', 'active', NULL, 7, 'buyer', 'Laguna', 'Calauan', 'Dayap', '09124256789', 'Betatester123', 0, NULL, NULL),
(19, 'yo', 'yoyi@gmail.com', 'active', NULL, 7, 'rider', 'Laguna', 'Pila', 'Pansol', '09', '123', 0, NULL, NULL),
(20, 'mark123', 'mark123@gmail.com', 'active', NULL, 7, 'rider', 'Laguna', 'santa cruz', 'palasan', '09123456789', 'password', 0, NULL, NULL),
(21, 'CJ Shop Slop', 'johnclintlopez@gmail.com', 'active', NULL, 7, 'seller', 'Laguna', 'Calauan', 'Dayap', '09757217450', '08082001', 0, NULL, NULL),
(22, 'marwino', 'marwindalinmarwin@gmail.com', 'active', NULL, 7, 'seller', 'Laguna', 'Pila', 'Pansol', '09474371682', '12345678', 0, NULL, NULL),
(23, 'ella', 'ellabianca@gmail.com', 'active', NULL, 7, 'seller', 'Bataan', 'Samal', 'Santa Lucia', '09208853099', 'ellaganda', 0, NULL, NULL),
(35, 'waka', 'wakaranaii@gmail.com', 'active', NULL, 7, 'buyer', 'Cagayan', 'Lal-Lo', 'Catugan', '09108735236', 'Marwi', 0, NULL, NULL),
(45, 'waka123', 'marwindali@gmail.com', 'active', NULL, 7, 'buyer', 'Laguna', 'Pila', 'Pansol', '09474371681', 'Marw', 0, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`cart_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `riders`
--
ALTER TABLE `riders`
  ADD PRIMARY KEY (`rider_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `cart_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=112;

--
-- AUTO_INCREMENT for table `riders`
--
ALTER TABLE `riders`
  MODIFY `rider_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `fk_seller_product` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `riders`
--
ALTER TABLE `riders`
  ADD CONSTRAINT `riders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
