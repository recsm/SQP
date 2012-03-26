# vim: set fileencoding=utf-8 :
"""
The ``walk_and_run`` module works by following these steps:

    #. Walk a directory tree, looking for LISREL input files;
    #. If an input file is encountered:

        #. Modify the input so that the needed estimates will be
          written to files;
        #. Run this modified input using the LISREL executable 
          (application);
        #. Retrieve the standardized estimates and perform an 'action'
          on them. Currently available 'actions' are:

            * Selecting the MTMM validity and reliability coefficients
              from the appropriate group, inserting them into a MySQL database 
              table, retrieving their variance-covariance matrix and 
              writing them to a file (this matrix is needed in order to 
              perform meta-analyses);
            * Just printing the standardized estimates.

Most of the above procedures use the module ``parse_lisrel``.
"""
#!/usr/bin/python
import os, tempfile, sys, re
import MySQLdb
from parse_lisrel import LisrelInput
from parse_lisrel import solution_obtained

import numpy as np
from scipy import io

from sqp_project.sqp.models import MTMMModel, MTMMModelType, Item, \
        ItemParameter, ParameterName, \
        ItemParameterCovariance, ParameterName, Experiment, Trait, Question

epstol = np.finfo(float).eps # about 2e-16 both on work box and server
#sys.stderr = file('walk_and_run-logfile', 'w')
sys.stderr = sys.stdout # DEBUG

def float_to_decimal(fnum):
    """Creates a decimal from a float in such a way as to minimize the number
    of garbage digits used."""
    from decimal import Decimal
    # use the negative exponent from epstol to determine the 
    #  number of significant digits (note this is a maximum precision)
    num_digits = str(epstol).split('-')[1]
    format_string = "%." + num_digits + "f"

    return(Decimal(format_string % fnum))

def write_tuple_to_file(tup, path, sep='\r'):
    """takes a (multidimensional) tuple and writes it to a file at path"""
    if type(path) == tuple:
       path = os.path.join(path[0], path[1])
    outfile = open(path, 'w')
    for elem in tup:
        if type(elem) == tuple:
            for subel in elem:
                outfile.write(subel + sep)
        else:
            outfile.writeline(elem)
    outfile.close()
    sys.stderr.write('Wrote tuple to file %s.\n' % path)


def default_action(matrix, **kwargs):
    """By default the standardized matrices encountered by walk_and_run are 
       just printed"""
    print matrix

def save_estimates(input_path, experiment, country, study, val, rel, met, 
        varnum, update_or_insert = 'insert'):
    """Writes one row of estimates data to the database. Returns True if all
       is well, False if an exception occurs (exception is not thrown 
       directly to ensure that the database connection is closed)."""
    try:
        conn = MySQLdb.connect (host = "localhost",
                               user = "automtmm",
                               passwd = "automtmm",
                               db = "automtmm")
    except MySQLdb.Error, e:
        sys.stderr.write( "MySQL error %d: %s\n" % (e.args[0], e.args[1]))
        return False
    cursor = conn.cursor()
    try:
        if update_or_insert == 'insert':
            sql = """INSERT INTO estimates (input_path, experiment, country, 
                    study, validity_coef, reliability_coef, method_coef, 
                    var_num ) VALUES
                        ('%s', '%s', '%s', '%s', %2.16f, %2.16f, %2.16f, %d)
                    """ % (input_path, experiment, country, study, val, rel, 
                            met, varnum) 
        elif update_or_insert == 'update':
            sql = """UPDATE estimates SET reliability_coef=%2.16f
                     WHERE
                        input_path='%s' and experiment='%s' and country='%s' 
                    and study='%s' and var_num=%d """ % (rel, input_path, 
                        experiment, country, study, varnum) 
            
        sys.stderr.write(sql + "\n")
        cursor.execute(sql)
        conn.commit()
        
    except MySQLdb.Error, e:
        sys.stderr.write( "MySQL error %d: %s\n" % (e.args[0], e.args[1]))
        return False
    finally:
        conn.close()
    return True

def entry_exists(input_path, experiment, country, study, varnum):
    """Checks whether the entry with the given characteristics 
       is already in the database."""
    try:
        conn = MySQLdb.connect (host = "localhost",
                               user = "automtmm",
                               passwd = "automtmm",
                               db = "automtmm")
    except MySQLdb.Error, e:
        sys.stderr.write( "MySQL error %d: %s\n" % (e.args[0], e.args[1]))
        return False
    cursor = conn.cursor()
    try:
        sql = """SELECT * FROM estimates WHERE
                        input_path='%s' and experiment='%s' and country='%s' and
                        study='%s' and var_num=%d
                    """ % (input_path, experiment, country, study, varnum) 
        sys.stderr.write(sql + "\n")
        cursor.execute(sql)
        if cursor.fetchone():
            return True
    except MySQLdb.Error, e:
        sys.stderr.write( "MySQL error %d: %s\n" % (e.args[0], e.args[1]))
    finally:
        conn.close()
    return False

def save_parameter(estimate, parameter_name, question, lisfile):
    """Saves an item parameter estimate of type parameter_name, 
    for item corresponding to question_id and model with model_path, 
    creating the MTMMmodel if necessary.  In that case mtmm_model_input 
    should be set."""

    # Get the model object or create it if necessary
    mtmm_model, model_created = MTMMModel.objects.get_or_create(\
            path = lisfile.path, 
            defaults={'input': lisfile.input_text})

    if model_created:
        sys.stdout.write("Inserted new MTMM model '%s'\n" % mtmm_model.path)

    # Update or insert the parameter corresponding to model, type, and question
    parameter_name_obj = ParameterName.objects.get(short_name = parameter_name)
    item_parameter, param_created = ItemParameter.objects.get_or_create(\
            question = question, model = mtmm_model, 
            parameter_name = parameter_name_obj,
            defaults = {'estimate':float_to_decimal(estimate)})
    # Use the float_to_decimal function to save only sensible digits in 
    #   a bid to make future calculations as clean as possible
    item_parameter.estimate = float_to_decimal(estimate)
    try:
        item_parameter.save() 
        if param_created:
            sys.stdout.write("""Inserted new item parameter of type 
                    %s for question "%s"\n"""% \
                    (str(parameter_name), str(question)))
    except Exception, e:
        sys.stderr.write( "Error on saving item parameter:\n\t%s\n" % str(e) )


def get_data_from_path(path):
    "Parses a path to yield study, country, language, experiment"
    # Round-specific code to translate the filesystem logic into database object
    if path.find('analysesround4') != -1:
        country, language, ex_short_name = \
                path[path.find('analysesround4'):].split(os.sep)[1:4]
    
    experiment = Experiment.objects.get(short_name = ex_short_name)
    return country, language, experiment # will raise ex. if not found

def get_par_name(matrix_name, row, column, num_traits):
    """Takes a LISREL matrix element name such as LY 1 1 1 and returns 
     a parameter name such as rel_coef. Num_traits is needed to figure
     out whether a Gamma parameter is a validity or a method effect."""
    sys.stderr.write("""Trying to save element %s %d %d,
        ntraits is %d\n""" % (matrix_name, row+1, column+1, num_traits))
    if matrix_name.upper() == 'LY': # LY always represents reliability coefficients
        return 'rel_coef'
    elif matrix_name.upper() == 'GA': # for gamma, depends where the effect comes from
        if (column+1) > num_traits: # traits are always on the left partition of GA
            return 'met_coef'
        else:
            return 'val_coef'
    return False # failed


def save_parameter_covariance(vmat, vnames, lisfile):
    """Loops over the variance-covariance matrix values and for each element
    looks up the dictionary --> item and parameter name. Then country and language
    is used to retrieve the Question. Then question, model_path, and parameter_name
    are use to retrieve the item_parameter. This is done for the row and the column.
    Note that row and column may be equal, this would mean a parameter's variance.
    Then an ItemParameterCovariance object is created for this row and column and 
    the corresponding element in vmat is saved using float_to_decimal."""

    sys.stderr.write("Called save_parameter_covariance:\n\tpath: %s"%\
        lisfile.path)
    # extract country language and experiment from path
    country_iso, language_iso, experiment = get_data_from_path(lisfile.path)
    # get number of unique traits pertaining to this experiment
    num_traits = Trait.objects.filter(item__experiment = experiment).\
            distinct().count()
    # get items in this experiment, _using the ordering defined in Item_
    items = experiment.item_set.all()

    model = MTMMModel.objects.get(path = lisfile.path)
    vnames = flatten(vnames) # remove group information
    rows, columns = vmat.shape
    for i in range(rows):
        mat_name, mat_row, mat_col = vnames[i].strip().split(' ')
        mat_row, mat_col = int(mat_row) - 1 , int(mat_col) - 1
        row_param_name = get_par_name(mat_name, mat_row, mat_col, num_traits)
        row_question = Question.objects.get(item = items[mat_row], 
                language__iso = language_iso, country__iso = country_iso)
        try:
            row_parameter = ItemParameter.objects.get(question = row_question,
                model = model, parameter_name__short_name = row_param_name)
        except ItemParameter.DoesNotExist: continue

        for j in range(columns):
            mat_name, mat_row, mat_col = vnames[j].strip().split(' ')
            mat_row, mat_col = int(mat_row) - 1, int(mat_col) - 1
            col_param_name = get_par_name(mat_name, mat_row, mat_col, num_traits)
            col_question =  Question.objects.get(item = items[mat_row], 
                language__iso = language_iso, country__iso = country_iso)
            try:
                col_parameter = ItemParameter.objects.get(question = col_question, 
                    model = model, parameter_name__short_name = row_param_name)
            except ItemParameter.DoesNotExist: continue

            cov, created = ItemParameterCovariance.objects.get_or_create(\
                    parameter_row = row_parameter, 
                    parameter_column = col_parameter, 
                    defaults = {'estimate' : float_to_decimal(vmat[i, j]) }) 
            cov.estimate = float_to_decimal(vmat[i, j])

            try:
                cov.save() 
                if created:
                    sys.stdout.write("""Inserted new item parameter covariance\n
                            \trow: %s\n\tcol: %s\n"""% \
                            (str(row_parameter), str(col_parameter)))
            except Exception, e:
                sys.stderr.write("""Error on saving item parameter covariance:
                    \n\t%s\n""" % str(e) )


def save_matrix_parameters(matrix, **kwargs):
    """An 'action' that loops over the elements of the matrix and looks them up
    in a dictionary that contains the parameter name and item id for each 
    matrix element per group. 
    The language and country are then inferred from the path and
    a Question object is selected. If necessary the file contents of the input and
    output are passed to save_parameter."""
    group_num = kwargs['group_num'] 
    lisfile = kwargs['lisfile']
    matrix_name = kwargs['matname']

    # extract country language and experiment from path
    country_iso, language_iso, experiment = get_data_from_path(lisfile.path)
    # get unique traits pertaining to this experiment
    traits = Trait.objects.filter(item__experiment = experiment).distinct()
    # get items in this experiment, _using the ordering defined in Item_
    items = experiment.item_set.all()

    sys.stderr.write("Called save_mtmm_matrix:\n\tpath: %s"%\
        (lisfile.path))

    # loop over matrix elements
    rows, cols = matrix.shape
    for i in range(rows):
        for j in range(cols):
            # Check that entry is not zero
            if abs(matrix[i, j]) < epstol: continue
            # look up name group_num row column in dictionary
            parameter_name =  get_par_name(matrix_name, i, j, traits.count())
            if not parameter_name:
                stderr.write("Error trying to look up parameter. Skipping..\n")
                continue
            #   get the Question corresponding to the item, language, country
            #  items are in the same order and the row index is always the 
            #   observed variable index
            question =  Question.objects.get(item = items[i], 
                language__iso = language_iso, country__iso = country_iso)
            save_parameter(estimate = matrix[i, j], 
                    parameter_name = parameter_name, question = question, 
                    lisfile = lisfile)

def run_input(inpath):
    """Utility function to run a lisrel input, writing the output to the 
        same directory with the same name but replacing LS8 by OUT.
        This is different from what is done in run_lisrel because there an 
        output is created in a temp directory and it probably has a lot more text
        than the original. 
        This function is dangerous in that it overwrites any previously existing
        LISREL outputs."""
    indir, infile = os.path.split(inpath)
    outfile = infile.replace(".LS8", '.OUT')
    curdir = os.getcwd()
    os.chdir(indir)
    cmd = 'wine Lisrel85.exe %s %s' % (infile, outfile)
    print("Running " + cmd + "...")
    retval = os.system(cmd)
    os.chdir(curdir)
    return retval
    

def walk_and_run_sqp(top_dir, tempdir='', action=save_matrix_parameters, 
        run_original = False):
    """recurse through directory structure, looking for .LS8 files.
       Each .LS8 file is run.
       """
    if tempdir == '': # let tempfile library choose a tempdir by default
        tempdir = tempfile.mkdtemp()
    sys.stderr.write( "Temporary directory will be %s.\n" % 
            os.path.abspath(tempdir) )
    top_dir = os.path.abspath(top_dir)
    not_converged = file('not_converged', 'w')

    for dirpath, dirnames, filenames in os.walk(top_dir):
        if (dirpath.find('mediaWRONG') != -1) or \
                (dirpath.find('lr') != -1) or (dirpath.find('soctrust') != -1) or\
                (dirpath.find('polor') != -1):
            continue
        sys.stderr.write( "Searching %s...\n" % dirpath )

        for filename in filenames:
            if filename.upper().endswith('LS8'):
                if run_original: run_input(os.path.join(dirpath, filename))
                sys.stderr.write( "Found %s.\n" % filename )
                lisfile = LisrelInput(os.path.join(dirpath, filename))
                # adjust input to output matrices separately
                lisfile.write_to_file(lisfile.get_modified_input())
                try:
                    lisfile.run_lisrel(tempdir) # run lisrel to write output to tempdir
                except:
                    print "LISREL encountered an error, skipping...\n"
                    break
                finally:
                    if os.path.exists(lisfile.path + '.backup'):
                        os.remove(lisfile.path)
                        os.rename(lisfile.path + '.backup', lisfile.path)
                    else:
                        sys.stderr.write('''WARNING: Could not restore backup 
                            LS8 file.\n''')
                if solution_obtained(os.path.join(tempdir, 'OUT')):
                    smats = lisfile.standardize_matrices()
                    for igrp in range(len(smats)):
                        for matname, stanmat in smats[igrp].iteritems():
                            sys.stderr.write( "INPUT %s, GROUP %d, MATRIX %s:" % \
                                    (filename, igrp+1, matname))
                            action(stanmat, matname=matname, group_num = igrp+1,
                                    lisfile = lisfile)

                #    try:
                    vnames, vmat = lisfile.get_var_standardized(path = \
                                tempdir)
                    save_parameter_covariance(vmat, vnames, lisfile)
                #    except Exception, e:
                #        sys.stderr.write("""ERROR saving vcov matrix of 
                #            standardized estimates . Error: %s\n""" % str(e))
                else:
                    print "No solution could be obtained, skipping...\n"
                    not_converged.write(os.path.join(dirpath, filename) + "\n")
    not_converged.close()


def retrieve_mtmm(matrix, **kwargs):
    """An 'action' that collects the reliabilities, validities, and method 
       effects and writes them to a single MySQL table."""
    group_num = kwargs['group_num']
    dirpath = kwargs['dirpath']
    filename = kwargs['filename']
    path = os.path.splitext(dirpath)[0].split(os.sep)[-3:]
    experiment = path[-1]
    country = path[-2]
    study = path[-3]
    sys.stderr.write("Called retrieve_mtmm:\n\tdirpath: %s\n\tfilename: %s\n\t\
group: %d\n\texperiment: %s\n\tcountry: %s\n\tstudy: %s\n\n" % \
        (dirpath,filename,group_num,experiment,country,study))
    
    #nrows = matrix.shape[0]
    input_path = os.path.join(dirpath, filename)
    rows = range(3); rows.extend(map(lambda x: x+group_num*3, range(3)))
    for irow in rows: # loop only over variables that were observed in this group
        if kwargs['matname'] == 'GA':
            val, met = matrix[[irow, irow],[irow%3, (irow + 3)/3 + 2]].tolist()[0]
            if entry_exists(input_path, experiment, country, study, irow):
                res = save_estimates(input_path, 
                    experiment, country, study, val, -9.0, met, irow, 'update')
            else:
                res = save_estimates(input_path, 
                    experiment, country, study, val, -9.0, met, irow, 'insert')
        if kwargs['matname'] == 'LY':
            rel = matrix[irow, irow]
            if entry_exists(input_path, experiment, country, study, irow):
                res = save_estimates(os.path.join(dirpath, filename), 
                    experiment, country, study, -9.0, rel, -9.0, irow, 'update')
            else:
                res = save_estimates(os.path.join(dirpath, filename), 
                    experiment, country, study, -9.0, rel, -9.0, irow, 'insert')


def walk_and_run(top_dir, tempdir='', action=default_action):
    """recurse through directory structure, looking for .LS8 files.
       Each .LS8 file is run.
       """
    if tempdir == '': # let tempfile library choose a tempdir by default
        tempdir = tempfile.mkdtemp()
    sys.stderr.write( "Temporary directory will be %s.\n" % 
            os.path.abspath(tempdir) )
    top_dir = os.path.abspath(top_dir)
    not_converged = file('not_converged', 'w')

    for dirpath, dirnames, filenames in os.walk(top_dir):
        sys.stderr.write( "Searching %s...\n" % dirpath )
        for filename in filenames:
            if filename.upper().endswith('LS8'):
                sys.stderr.write( "Found %s.\n" % filename )
                lisfile = LisrelInput(os.path.join(dirpath, filename))
                # adjust input to output matrices separately
                lisfile.write_to_file(lisfile.get_modified_input())
                try:
                    lisfile.run_lisrel(tempdir) # run lisrel to write output to tempdir
                except:
                    print "LISREL encountered an error, skipping...\n"
                    break
                finally:
                    if os.path.exists(lisfile.path + '.backup'):
                        os.remove(lisfile.path)
                        os.rename(lisfile.path + '.backup', lisfile.path)
                    else:
                        sys.stderr.write('WARNING: Could not restore backup LS8 file.\n')
                if solution_obtained(os.path.join(tempdir, 'OUT')):
                    smats = lisfile.standardize_matrices()
                    for igrp in range(len(smats)):
                        for matname, stanmat in smats[igrp].iteritems():
                            sys.stderr.write( "INPUT %s, GROUP %d, MATRIX %s:" % \
                                    (filename, igrp+1, matname))
                            action(stanmat, matname=matname, group_num = igrp+1,
                                    filename=filename, dirpath=dirpath)
                    # try to write the variance matrix of 
                    #   the standardized estimates
                    try:
                        vnames, vmat = lisfile.get_var_standardized(path = \
                                tempdir)
                        vfile = open(os.path.join(dirpath, 
                                    'vcov_standardized.txt'), 'w')
                        io.write_array(vfile, vmat, separator='\t',
                                    linesep='\n', precision=10,) # closes vfile
                        write_tuple_to_file(vnames, 
                                    path=(dirpath, 'vcov_standardized.names'))
                    except:
                        sys.stderr.write('ERROR writing or getting vcov matrix of standardized estimates for group %d. Error: %s\n' % (igrp, str(e.args)))
                else:
                    print "No solution could be obtained, skipping...\n"
                    not_converged.write(os.path.join(dirpath, filename) + "\n")

    not_converged.close()

def flatten(l, ltypes=(list, tuple)):
    """Copied from 
    http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html"""
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

