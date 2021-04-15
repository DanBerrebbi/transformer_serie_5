josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/

vocab=$PWD/minmt-vocab.py
setup=$PWD/minmt-setup.py
train=$PWDT/minmt-train.py
avrge=$PWD/minmt-average.py
trans=$PWD/minmt-translate.py

tokenizer=$josep/MiNMT/tools/tokenizer.py
data=$josep/data
stovec=$josep/stovec

dir=$josep/minmt_base

dir_dan = /data_corpus
dnet=$PWD/model_serie_true


	for corpus in ECB ; do
	    echo $corpus

	    fsrc=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.src
      ftgt=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.tgt
	    fsim=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.sim
	    fpre=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.pre

	    cat $fsrc >> trn_src
	    cat $ftgt >> $dir_dan/trn_tgt
	    cat $fsim >> $dir_dan/trn_sim
	    cat $fpre >> $dir_dan/trn_pre
   echo ok

  done