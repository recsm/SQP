ALTER TABLE `sqp_question` 
	ADD COLUMN `val` DOUBLE NULL  AFTER `answer_text` , 
	ADD COLUMN `val_lo` DOUBLE NULL  AFTER `val` , 
	ADD COLUMN `val_hi` DOUBLE NULL  AFTER `val_lo` , 
	ADD COLUMN `valz` DOUBLE NULL  AFTER `val_hi` , 
	ADD COLUMN `valz_se` DOUBLE NULL  AFTER `valz` ;