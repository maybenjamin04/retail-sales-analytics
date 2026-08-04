# this file should run everything at once

# WORKFLOW

# CLEAN DATA WITH dataCleaning.py

# load to postgres with loadToPostgreSQL.py
import dataCleaning, loadToPostgreSQL

#RUN IT
if __name__ == '__main__':
    dataCleaning()
    loadToPostgreSQL()