
import psycopg2
import psycopg2.extras

class Database(object):
    
    def __init__(self, debug=False):

        try:
           self.con = psycopg2.connect(database='MSA8010', user='postgres', password='password') 
           self.con.autocommit = True
           self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
           
           if debug:
               self.cur.execute('SELECT version()')          
               print self.cur.fetchone()
    
        except:
            print "Error: unable to connect to database"
            return False


    def read(self, sql, params=None, returnAll=True):

        try:
            #execute a sql select statement and return one or all rows        
            self.cur.execute(sql, params)
            if (returnAll):
                return self.cur.fetchall()
            else:
                return self.cur.fetchone()
        except:
            print "Database error"
            return False
           
           
    def execute(self, sql, params):
        try:
            #Execute a sql command (insert, update, delete)
            self.cur.execute(sql, params)
            return 
        
        except:
            print "Database error"
            return False
       
               
    def close(self):       
        # disconnect from server
        self.cur.close()
        

