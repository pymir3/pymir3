import sys
import numpy as np

def update_folds(fl, content, lineno, last_tag):

    print content[lineno]

    for i in range(lineno, min(lineno+100, len(content)  )):
        if (": %s" % last_tag) in content[i]:
            acc = float(content[i+1])
        if "avg / total" in content[i]:
            partes = content[i].split(" ")
            partes = filter(None, partes)
            precision = partes[3]
            recall = partes[4]
            f1 = partes[5]
        if "maxresident" in content[i]:
            #print content[i]
            pass

    fl.append ( [acc, precision, recall, f1] )

def update_train_folds(fl, content, lineno):
    
    i = lineno
    while "testing model" not in content[i]:

        if "training took" in content[i]:
            d = content[i].split(" ")
            train_time = float(d[3])
        
        if "for ANOVA" in content[i]:
            d = content[i].split(" ")
            anova_pct = int(d[7].strip())
            

        if "for SVM" in content[i]:
            d = content[i].split(" ")
            c = d[7].strip()
            gamma = d[10].strip()

        if "maxresident" in content[i]:
            d = content[i].split(" ")
            user_time = float(d[0].split("user")[0])
            system_time = float(d[1].split("system")[0])
            elapsed_time = d[2].split("elapsed")[0]
            cpu = int(d[3].split("%CPU")[0])
            maxresident =int(d[5].split("maxresident")[0])

        if "pagefaults" in content[i]:
            
            d = content[i].replace('(', '').replace(')', '').split(" ")
            inputs = int(d[0].split("+")[0].split("inputs")[0])
            outputs = int(d[0].split("+")[1].split("outputs")[0])
            major_pf = int(d[1].split("+")[0].split("major")[0])
            minor_pf = int(d[1].split("+")[1].split("minor")[0])

        i+=1

    total_time = float(elapsed_time.split(":")[0]) * 60 + float(elapsed_time.split(":")[1].split(".")[0]) + float(elapsed_time.split(":")[1].split(".")[1]) * .01

    fl.append( [c, gamma, anova_pct,  train_time, user_time, system_time, total_time, cpu, maxresident, inputs, outputs, major_pf, minor_pf] )

def print_results(folds):

    results = evaluate_folds(folds)
    print "acc = ",  round(results[0][0],2)
    print "precision = ", round(results[0][1],2)
    print "recall = ", round(results[0][2],2)
    print "f1 = ", round(results[0][3],2)

    return results

def print_train_results(train):
    m = np.array (train, dtype=object)
    d = m[:,2:].astype("float64")
    mean = np.round(np.mean(d, axis=0), decimals=2)
    stdev = np.round(np.std(d, axis=0), decimals=2)
    
    d2 = m[:,:2]
    
    return (mean, stdev, d2)

def evaluate_folds(folds):
    m = np.array(folds, dtype=np.float64)
    return  np.round(np.mean(m, axis=0), decimals=2), np.round(np.std(m, axis=0), decimals=2)

if __name__ == "__main__":
    
    if len(sys.argv) != 4:
        print("usage: %s experiment_output_file csv_file last_tag" % sys.argv[0])
        exit(1)

    with open(sys.argv[1]) as f:
        content = f.readlines() 
    
    current_exp = ""
    current_var = ""

    fold_results = []
    train_results = []
    
    final_train_results = []
    results = []

    lineno = 0
    for l in content:
        if "Error" in l:
            print ("ERROR in line %d: %s" % (lineno, l))
            break

        if "###" in l:
            if fold_results != []:
                r = print_results(fold_results)
                results.append( (current_exp, current_var, r ))
                fold_results = []

                r = print_train_results(train_results)
                final_train_results.append( (current_exp, current_var, r) )
                train_results = []

            print "\n", l
            current_exp = l.replace("###", "").replace(",", " ")

        if "testing model" in l:
            update_folds(fold_results, content, lineno, sys.argv[3])

        if "*** FOLD" in l:
            update_train_folds(train_results, content, lineno)

        if "!!!" in l:
            if fold_results != []:
                r = print_results(fold_results)
                results.append((current_exp, current_var, r ))
                fold_results = []

                r = print_train_results(train_results)
                final_train_results.append( (current_exp, current_var, r) )
                train_results = []

            #print l
            current_var = l.replace("!!!", "").replace(",", " ")
            
        lineno+=1

    r = print_results(fold_results)
    results.append((current_exp, current_var, r ))

    r = print_train_results(train_results)
    final_train_results.append( (current_exp, current_var, r))

    #print final_train_results

    output = open(sys.argv[2], "w")

    output.write("exp;var;accuracy;precision;recall;f1-score;\n")

    #print results

    #for i in results:
    #    output.write("%s;%s;%.2f;%.2f;%.2f;%.2f\n" % ( i[0].replace("\n", ""), i[1].replace("\n", ""), i[2][0], i[2][1], i[2][2], i[2][3] )  )

    for i in results:
        output.write( "%s;%s;" %(i[0].strip(), i[1].strip()))
        for k in xrange(len(i[2][0])):
            output.write("%.2f +- %.2f;" % ( i[2][0][k], i[2][1][k] ))
        output.write("\n")


    output.write("\n\n\n")

    output.write("exp;var;anova_pct;train_time;user_time;system_time;wall_time;cpu_usage;maxresident(k);inputs;outputs;majpf;minpf\n")

    for i in final_train_results:
        output.write( "%s;%s;" %(i[0].strip(), i[1].strip()))
        for k in xrange(len(i[2][0])):
            output.write("%.2f +- %.2f;" % ( i[2][0][k], i[2][1][k] ))
        output.write("\n")


    output.close()
