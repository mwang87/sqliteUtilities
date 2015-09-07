#!/usr/bin/python


import sys
import getopt
import os
import ming_fileio_library
from subprocess import call


def create_sqlite_file(input_tsv_filename, output_sqlite_filename):
    temp_sql_populate_filename = "./temp.sqlite"

    sql_reserved_words = ["unique"]


    temp_sql_populate_file = open(temp_sql_populate_filename, "w")


    rows, table_data = ming_fileio_library.parse_table_with_headers(input_tsv_filename)
    headers = table_data.keys()

    #Writing the Schema
    create_table_sql = "CREATE TABLE MyData("


    for header in headers:
        if header in sql_reserved_words:
            continue
        #We should do some inference on the types, we probably should only support floats, strings, and ints
        create_table_sql += header.replace(":", "_").replace("-", "_").replace("#", "_").replace("(", "_").replace(")", "_") + " " + "varchar(255)" + ", "

    create_table_sql = create_table_sql[:-2]
    create_table_sql += ");\n"

    temp_sql_populate_file.write(create_table_sql)

    #Writing the Data
    batch_insert_size = 500
    for i in range(rows):
        row_insert_statement = ""
        for header in headers:
            if header in sql_reserved_words:
                continue
            row_insert_statement += "'" + table_data[header][i] + "',"
        row_insert_statement = row_insert_statement[:-1]
        row_insert_statement += ""

        if i % batch_insert_size == 0:
            insert_statement = "INSERT INTO MyData SELECT "
            if i != 0:
                temp_sql_populate_file.write(";\n")
            temp_sql_populate_file.write(insert_statement)

        if i < (rows - 1) and ( (i + 1) % batch_insert_size != 0):
            row_insert_statement += " UNION ALL SELECT "
        temp_sql_populate_file.write(row_insert_statement)
    temp_sql_populate_file.write(";\n")

    temp_sql_populate_file.close()

    populate_db_cmd = "sqlite3 " + output_sqlite_filename + " < " + temp_sql_populate_filename
    call(populate_db_cmd,  shell=True)
    os.remove(temp_sql_populate_filename)



def usage():
    print "<input file>"



def main():
    input_filename = sys.argv[1]
    output_sqlite_filename = sys.argv[2]

    input_filenames = []

    #Check if this is an input file or a folder
    if os.path.isdir(input_filename):
        input_filenames = ming_fileio_library.list_files_in_dir(input_filename)
    else:
        input_filenames.append(input_filename)


    for input_tsv in input_filenames:
        create_sqlite_file(input_tsv, output_sqlite_filename)



    exit(0)






if __name__ == "__main__":
    main()
