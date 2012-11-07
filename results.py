
import MySQLdb
import sys
import pickle

#use the file?
SOURCE_FILE = 1
SOURCE_SQL = 2

dataSource = SOURCE_SQL

#test number
testNumber = 3

#all votes, a list of the class structure below
votes =[]

#dump the SQL?
dumpSQL = True

#+-----------+--------------+------+-----+---------+----------------+
#| Field     | Type         | Null | Key | Default | Extra          |
#+-----------+--------------+------+-----+---------+----------------+
#| id        | mediumint(9) | NO   | PRI | NULL    | auto_increment |
#| test_id   | mediumint(9) | NO   |     | NULL    |                |
#| pair_id   | mediumint(9) | NO   |     | NULL    |                |
#| time_disp | text         | YES  |     | NULL    |                |
#| time_vote | text         | YES  |     | NULL    |                |
#| vote      | text         | YES  |     | NULL    |                |
#| voter     | text         | YES  |     | NULL    |                |
#| comment_a | text         | YES  |     | NULL    |                |
#| comment_b | text         | YES  |     | NULL    |                |
#+-----------+--------------+------+-----+---------+----------------+

class Vote: #from the database above
   def __init__( self, id, test_id, pair_id, time_disp, time_vote, vote, voter, comment_a, comment_b ):
      self.id = id
      self.test_id = test_id
      self.pair_id = pair_id
      self.time_disp = time_disp
      self.time_vote = time_vote
      self.vote = vote
      self.voter = voter
      self.comment_a = comment_a
      self.comment_b = comment_b

#+----------+--------------+------+-----+---------+----------------+
#| Field    | Type         | Null | Key | Default | Extra          |
#+----------+--------------+------+-----+---------+----------------+
#| id       | mediumint(9) | NO   | PRI | NULL    | auto_increment |
#| test_id  | mediumint(9) | NO   |     | NULL    |                |
#| image_a  | text         | YES  |     | NULL    |                |
#| image_b  | text         | YES  |     | NULL    |                |
#| comments | text         | YES  |     | NULL    |                |
#+----------+--------------+------+-----+---------+----------------+


class Image: #from above
   def __init__( self, id, test_id, image_a, image_b, comments ):
      self.id = id
      self.test_id = test_id
      self.image_a = image_a
      self.image_b = image_b
      self.comments = comments

      self.votes_a = 0
      self.votes_b = 0
      self.votes_eq = 0


#+-------------+--------------+------+-----+---------+----------------+
#| Field       | Type         | Null | Key | Default | Extra          |
#+-------------+--------------+------+-----+---------+----------------+
#| id          | mediumint(9) | NO   | PRI | NULL    | auto_increment |
#| name        | text         | NO   |     | NULL    |                |
#| description | text         | YES  |     | NULL    |                |
#| active      | tinyint(4)   | YES  |     | 0       |                |
#| descr_a     | text         | YES  |     | NULL    |                |
#| descr_b     | text         | YES  |     | NULL    |                |
#+-------------+--------------+------+-----+---------+----------------+

class Test: #from above
   def __init__( self, id, name, description, active, descr_a, descr_b ):
      self.id = id
      self.name = name
      self.description = description
      self.active = active
      self.descr_a = descr_a
      self.descr_b = descr_b



def SQL_Print_Version( con ):
   cur = con.cursor()
   cur.execute("SELECT VERSION()")
   result = cur.fetchone()
   print "MySQL version: %s" % result
   cur.close()

def SQL_Get_Votes( con ):
    cur = con.cursor()
    cur.execute("use wordpress;")
    cur.execute("show tables;")
    cur.execute("select * from android_wp_brcm_pt_votes")
    rows = cur.fetchall()
    cur.close()

    _votes = []
    for row in rows:
        _votes.append( Vote( row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8] ) )
    return _votes


def SQL_Get_Images( con ):
    cur = con.cursor()
    cur.execute("use wordpress;")
    cur.execute("show tables;")
    cur.execute("select * from android_wp_brcm_pt_photos")
    rows = cur.fetchall()
    cur.close()

    _images = []
    for row in rows:
        _images.append( Image( row[0], row[1], row[2], row[3], row[4] ) )
    return _images


def SQL_Get_Tests( con ):
    cur = con.cursor()
    cur.execute("use wordpress;")
    cur.execute("show tables;")
    cur.execute("select * from android_wp_brcm_pt_tests")
    rows = cur.fetchall()
    cur.close()

    _tests = []
    for row in rows:
        _tests.append( Test( row[0], row[1], row[2], row[3], row[4], row[5] ) )
    return _tests



def Get_Voter_Names( votes ):
    #filter the test votes to find out unique user names
    voter_names = []
    for x in votes:
       if x.voter not in voter_names:
          voter_names.append( x.voter )
    return voter_names


#sanity check the results
def Sanity_Check( num_votes, unique_voters ):
   assert( (num_votes % unique_voters) != 0 )
   assert( (num_votes / unique_voters) == 22 )
   return num_votes / unique_voters


#function to add a vote
def Add_Vote( images, pair_id, vote_a, vote_b, vote_eq ):
   for x in images:
      if x.id == pair_id:
         x.votes_a += vote_a
         x.votes_b += vote_b
         x.votes_eq += vote_eq
         return
   assert( 0 )

#dump the tests
def Print_Tests( tests ):
   print "Active            Name"
   for x in tests:
      print  x.active, "               ", x.name

#dump the images
def Print_Images( images, a, b ):
   print "A == ", a
   print "B == ", b
   for x in images:
      print  x.id, " ", x.image_a, x.image_b, x.votes_a, x.votes_b, x.votes_eq


#dump the votes
def Print_Votes( votes ):
   for x in votes:
      print  x.id, x.test_id, x.pair_id, x.time_disp, x.time_vote, x.vote, x.voter, "Time taken = ", int(x.time_vote) - int(x.time_disp)

def Get_Data( ):
    global dataSource
    global dumpSQL

    if dataSource == SOURCE_SQL:
       con = MySQLdb.connect( host="android.broadcom.com", port=3306, user="readonly", db="wordpress" )
       SQL_Print_Version( con )

       votes = SQL_Get_Votes( con )
       images = SQL_Get_Images( con )
       tests = SQL_Get_Tests( con )
       con.close()

       if dumpSQL:
          pickle.dump(votes, file('votes.pickled', 'w'))
          pickle.dump(images, file('images.pickled', 'w'))
          pickle.dump(tests, file('tests.pickled', 'w'))

    else: # SOURCE_FILE
       votes = pickle.load(file('votes.pickled'))
       images = pickle.load(file('images.pickled'))
       tests = pickle.load(file('tests.pickled'))

    return votes, images, tests


def main():
    votes = []
    images = []
    tests = []
    
    #fetch the data
    votes, images, tests = Get_Data( )

    # Print_Tests( tests )

    assert( testNumber <= len(tests) )
    print tests[ testNumber - 1 ].name

    #filter the votes by test
    specific_test_votes = [x for x in votes if x.test_id == testNumber]

    #filter the images by est
    specific_images = [x for x in images if x.test_id == testNumber]

    #filter the test votes to find out unique user names
    voter_names = Get_Voter_Names( specific_test_votes )

    print "There are ", len(voter_names), " voters"

    #get a list of all votes to for A and B + EQ
    a_votes = [x for x in specific_test_votes if x.vote == "a"]
    b_votes = [x for x in specific_test_votes if x.vote == "b"]
    eq_votes = [x for x in specific_test_votes if x.vote == "eq"]

    print len(a_votes), " for A"
    print len(b_votes), " for B"
    print len(eq_votes), " were equal"

    #sanity check the results
    num_pictures = Sanity_Check( num_votes=len(specific_test_votes),
                                 unique_voters=len(voter_names) )

    #hacks...
    specific_test_votes = [x for x in specific_test_votes if x.voter != "npl"]
    specific_test_votes = [x for x in specific_test_votes if x.voter != "rouvinen"]

    # Print_Votes( specific_test_votes )

    for x in specific_test_votes:
       vote_a = 1 if x.vote == "a" else 0
       vote_b = 1 if x.vote == "b" else 0
       vote_eq = 1 if x.vote == "eq" else 0
       Add_Vote( specific_images, x.pair_id, vote_a, vote_b, vote_eq )

    #discount statistically 

    Print_Images( specific_images, tests[ testNumber - 1].descr_a, tests[ testNumber - 1].descr_b )

    return 0


#usual python main thing
if __name__ == "__main__":
    sys.exit(main())
