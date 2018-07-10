import pymysql
from flask import *


def create_tables():
	connection = pymysql.connect(host='localhost',user='root',password='',db='andela')
	with connection.cursor() as cursor:
		cursor.execute("SHOW TABLES LIKE 'admin';")
		results=cursor.fetchone()
		if results is not None:
			pass
		else:
			cursor.execute("CREATE TABLE `admin` (`AdminID` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,`Username` varchar(32) NOT NULL,`Password` varchar(100) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1;")
			cursor.execute("INSERT INTO `admin`(`AdminID`,`Username`,`Password`)VALUES (1, 'admin','admin');")
			cursor.execute("CREATE TABLE `comments` (  `commentID` int(32) NOT NULL AUTO_INCREMENT PRIMARY KEY,  `comment` text NOT NULL,  `Time` datetime NOT NULL, `ID` int(11) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1;")
			cursor.execute("CREATE TABLE `users`  (  `ID` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, `Fname` varchar(32) NOT NULL,  `Lname` varchar(32) NOT NULL,  `Email` varchar(100) NOT NULL,`Username` varchar(50) NOT NULL,`Password` varchar(100) NOT NULL,  `Timestamp` int(14) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=latin1;")
	connection.commit()
	connection.close()