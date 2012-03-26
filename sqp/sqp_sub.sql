
CREATE TABLE `sqp_label` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(150) NOT NULL,
    `code` varchar(10) NULL,
    `characteristic_id` integer NOT NULL,
    `compute` bool NOT NULL
)
;
ALTER TABLE `sqp_label` ADD CONSTRAINT characteristic_id_refs_id_2886bae7 FOREIGN KEY (`characteristic_id`) REFERENCES `sqp_characteristic` (`id`);
