# week2FridayProject-challenge 10

User come in two forms; admin and normal user. A normal user can register, login, create comment, edit comment, delete his/her comment and view all comments and who posted the comments. An admin can delete and modify any comment. 
This project has been implemented using mySQL and PostgresSQL.
There are a total of 9 endpoints as follows.
* / - index page GET request
* /login POST request
* /register-POST request
* /post_comment',methods=['POST']
* /view_comments',methods=['GET'] to only see his/her comments
* /account',methods=['GET'] view account details
* /delete_comment/<int:commentID>',methods=['DELETE']-a user can delete a message corresponding to entered comment id and must correspond to his/her ID and only on session
* /allcomments/<int:commentID>',methods=['DELETE']-only admin authorized .admin can delete any message by only entering the corresponding commentID
* /view_all',methods=['GET'] , only admin can view all comments by all users.
to run the application, clone or download on git hub, install requirements file. For the mySQL version, make sure you have xampp installed on your computer
create a database named andela and run db_int python file. You can also click on the file to start localhost server.
on an API consumer like postman works best. click on the link given and paste on the url area with the corresponding endpoints.
make sure to start with index page. Post requests take in JSON formatted text formats and returns json formatted data.
Admin default credentials are  username:admin,password:admin,userType:admin.
