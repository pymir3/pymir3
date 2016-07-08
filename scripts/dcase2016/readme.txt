A idéia é que os experimentos sejam realizados pelo script experimento.py.

##############A R Q U I V O S    D E    E N T R A D A (D A T A S E T S)################

Na raíz foi criada uma pasta mirex, contendo arquivos de entrada para experimentos train/test compatíveis com o formato de entrada do mirex.

Na pasta Mirex há duas subpastas: file_lists e gen_lists. 

A pasta file_lists contém os arquivos usados por experimento.py para realizar os experimentos. Para cada dataset são necessários dois arquivos com o mesmo prefixo (representando o dataset), sendo um deles com o sufixo _labels. O arquivo sem o sufixo _labels representa o arquivo mirex para extração de características, e deve conter o caminho completo de todos os arquivos do dataset, um por linha. O arquivo com o sufixo _labels é do mesmo formato que o arquivo de treinamento do mirex (nome_do_arquivo\tclass_label), no entanto deve conter uma linha para cada arquivo do dataset. Isto é devido ao fato que estamos usando cross-validation, logo, todos os exemplos são usados pra treinar e pra testar.

A pasta gen_lists contém scripts que geram os dois arquivos descritos acima, bastando informar o diretório raíz do dataset na variável dataset_dir. Como cada dataset tem seu próprio formato, é necessário escrever um script pra cada dataset. Inicialmente, gen_gtzan.py possui um script que gera file_lists pro dataset Genres, do Tzanetakis (apenas com os áudios convertidos para .wav).

CONVENÇÃO: É importante que os arquivos não contenham o caractere "." (ponto). Também é importante que o arquivo com as labels tenha exatamente o mesmo prefixo que a lista de arquivos do dataset correspondente. Exemplo: gtzan.txt (lista de arquivos para extração de features contendo todos os arquivos do dataset) e gtzan_labels.txt (lista com as labels de todos os arquivos do dataset). Esta convenção é obrigatória e o script não funciona sem ela.

##############E X E C U T A N D O     O S    E X P E R I M E N T O S###########

O script experimento.py recebe como entrada os datasets e os tipos de experimentos que devem ser realizados e devolve arquivos
descrevendo as features extraídas e os resultados do processo de treinamento e teste.

Use a opção -h para saber como executar o script e suas opções.

O script retorna 3 arquivos por configuração de separação em bandas (iterador,n_bandas):

-> um .fm (pymir3 feature matrix) contendo as features extraídas do dataset. Embora o script já faça o treinamento e a avaliação, pode acontecer algo que interrompa a execução durante estas tarefas. Desta forma, com o arquivo .fm em mãos é possível realizar as análises por meio do script train_and_classify manualmente, poupando um pouco de tempo.

-> um .csv que contém acurácia, precisão, recall e suporte dos pipelines executados.

-> um .txt que contém as matrizes de confusão e, novamente, acurácia, precisão, recall e suporte dos pipelines executados.


Exemplo de experimento:

./experimento.py -d /home/juliano/Dropbox/Doutorado/birdclef/pymir3/mirex/file_lists -p gtzan.txt -o fm -e bands

Neste caso, 
	os file_lists estão em /home/juliano/Dropbox/Doutorado/birdclef/pymir3/mirex/file_lists (note o caminho completo)
	quero rodar apenas o dataset gtzan.txt (-p)
	é pra colocar as saídas no diretório fm (-o)
	é pra executar os experimentos das bandas (-e). Vale lembrar que o script gera os 3 arquivos descritos acima para cada configuração (iterador_de_banda,numero_de_bandas)


