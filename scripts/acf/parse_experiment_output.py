import sys
import numpy as np

def update_folds(fl, content, lineno):

    print content[lineno]

    for i in range(lineno, min(lineno+100, len(content)  )):
        if "9: rock" in content[i]:
            acc = float(content[i+1])
        if "avg / total" in content[i]:
            partes = content[i].split(" ")
            partes = filter(None, partes)
            precision = partes[3]
            recall = partes[4]
            f1 = partes[5]

    #print "acc = ", acc
    #print "precision = ", precision
    #print "recall = ", recall
    #print "f1 = ", f1
    
    fl.append ( [acc, precision, recall, f1] )

def print_results(folds):

    results = evaluate_folds(folds)
    print "acc = ",  round(results[0],2)
    print "precision = ", round(results[1],2)
    print "recall = ", round(results[2],2)
    print "f1 = ", round(results[3],2)

    return results

def evaluate_folds(folds):
    m = np.array(folds, dtype=np.float64)
    return  np.round(np.mean(m, axis=0), decimals=2)

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("usage: %s experiment_output_file csv_file" % sys.argv[0])
        exit(1)

    with open(sys.argv[1]) as f:
        content = f.readlines() 
    
    current_exp = ""
    current_var = ""

    fold_results = []

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
            print "\n", l
            current_exp = l.replace("###", "").replace(",", " ")

        if "testing" in l:
            update_folds(fold_results, content, lineno)

        if "!!!" in l:
            if fold_results != []:
                r = print_results(fold_results)
                results.append((current_exp, current_var, r ))
                fold_results = []
            print l
            current_var = l.replace("!!!", "").replace(",", " ")
            
        lineno+=1

    r = print_results(fold_results)
    results.append((current_exp, current_var, r ))

    output = open(sys.argv[2], "w")

    output.write("exp;var;accuracy;precision;recall;f1-score;\n")

    print results

    for i in results:
        output.write("%s;%s;%.2f;%.2f;%.2f;%.2f\n" % ( i[0].replace("\n", ""), i[1].replace("\n", ""), i[2][0], i[2][1], i[2][2], i[2][3] )  )

    output.close()
