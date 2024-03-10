# Football Manager - MongoDB

## Table of Contents
* [Technologies](#technologies)
* [Introduction](#introducion)
* [Database](#database)
* [Footballers](#footballers)
* [Clubs](#clubs)
* [Validation](#validation)
* [App](#app)
* [Presentation](#presentation)
* [Edition](#edition)
* [Restrictions](#restrictions)
* [Mechanisms](#mechanisms)
* [Add New Player](#add-new-player)
* [Requirements](#requirements)
* [Set up database](#set-up-database)
* [To run Application:](#to-run-application)
* [Requirements](#requirements)

## Technologies
* [MongoDB](https://www.mongodb.com/)
* [PyQt6](https://doc.qt.io/qtforpython-6/)

## Introduction
The purpose of the app is to present the user statistics about football players and football clubs. The user can add, modify and delete players and clubs. All the aforementioned actions have restrictions and limitations. The data is stored in a non-relational database, MongoDB.  

## Database
### Footballers   
The database includes footballers. Each footballer has characteristics such as name, nationality, monthly salary or preferred rate. In addition, the footballer is assigned the statistics he has played over his career. 

### Clubs
Each club must have information on which country its league matches are played in. In addition, each club has a history of the seasons, what statistics it had at the time and a list of the players who played for the club in that season.

### Validation
The structure of the database is best described by the validations I have implemented for each collection. Their schemas can be seen in the [folder](https://github.com/Gorwik/Football-Manager---MongoDB/tree/master/Validation).
## App

### Presentation
![image](https://github.com/Gorwik/Football-Manager---MongoDB/assets/101866409/6ea558a1-e6e3-4618-8fde-d6aa11a4694e)

![image](https://github.com/Gorwik/Football-Manager---MongoDB/assets/101866409/278c0c99-9ebc-41e7-88f2-875f2269a644)

The application allows the sorting of players according to selected criteria. After selecting a particular footballer from the table and pressing the "More data" button, the seasons played by the footballer are also presented along with their statistics. In this window, it is also possible to edit the player's data. 

### Edition
#### Restrictions
There are several restrictions which, if breached, do not allow modifications to be made:
1. One footballer can only play for one club per season.
2. A footballer can only be assigned to one season of a given year.

#### Mechanisms
In addition, the application has additional mechanisms:
1. If a footballer removes a season played, he is automatically removed from the list of footballers playing in that season for that club.
2. If a player is completely removed from the database, his id is automatically replaced by his name in the list of players playing in the given season at the given club. 


![image](https://github.com/Gorwik/Football-Manager---MongoDB/assets/101866409/ab0e52bc-4efc-439b-84be-89032fea0ef9)  

For the clubs, on the other hand, the seasons are displayed along with statistics and playing squads.

### Add New Player
![image](https://github.com/Gorwik/Football-Manager---MongoDB/assets/101866409/b9859a50-0e51-42bb-8219-9d39a48de974)  
![image](https://github.com/Gorwik/Football-Manager---MongoDB/assets/101866409/8a7d9f0a-9441-40ac-91d0-2586d7492cab)

It is possible to add a new footballer, bearing in mind that they must comply with the [rules mentioned above](#restrictions).
## Requirements:
- Python version 3.11
- Account on [MongoDB](https://www.mongodb.com/cloud/atlas/register)

### Set up database
1. Create your own database on MongoDB. 
2. Create three database collections:
  - club_teams
  - leagues
  - players
3. For each collection, implement the corresponding validations from the [folder](https://github.com/Gorwik/Football-Manager---MongoDB/tree/master/Validation).
4. Import the data into the appropriate collection or create your owm. You can find the data in the [folder](https://github.com/Gorwik/Football-Manager---MongoDB/tree/master/Collections).
  
### To run Application:
1. In root folder create .venv environment.  
``
python -m venv football-manager-env
``

1. Activate it.  
On Windows:  
``
football-manager-env\Scripts\activate
``  
On Unix or MacOS:  
``
source football-manager-env/bin/activate
``  

1. Install dependencies included in [requirements.txt](https://github.com/Gorwik/Football-Manager---MongoDB/blob/master/requirements.txt).   
``
pip install -r requirements.txt
``  

1. Set env variables.  
  - On Windows:  
    ``setx MDB_login "your-MongoDB-login-here"``  
    ``setx MDB_pass "your-MongoDB-password-here" ``  
    ``setx MDB_db_name "your-MongoDB-database-name-here"``  
  
  - On Unix or MacOS:  
    ``export MDB_login='your-MongoDB-login-here'``  
    ``export MDB_pass='your-MongoDB-password-here'``  
    ``export MDB_db_name='your-MongoDB-database-name-here'``

