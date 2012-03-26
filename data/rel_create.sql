ALTER TABLE `sqp_question` 
	ADD COLUMN `rel` DOUBLE NULL  AFTER `answer_text` , 
	ADD COLUMN `rel_lo` DOUBLE NULL  AFTER `rel` , 
	ADD COLUMN `rel_hi` DOUBLE NULL  AFTER `rel_lo` , 
	ADD COLUMN `relz` DOUBLE NULL  AFTER `rel_hi` , 
	ADD COLUMN `relz_se` DOUBLE NULL  AFTER `relz` ;