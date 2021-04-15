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

mkdir "data_corpus"
dnet=$PWD/model_serie_true


	for corpus in ECB EMEA Europarl; do
	    echo $corpus
      echo train ...
	    fsrc=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.src
      ftgt=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.tgt
	    fsim=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.sim
	    fpre=$stovec/clean.$corpus.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.pre
	    cat $fsrc >> data_corpus/trn_src
	    cat $ftgt >> data_corpus/trn_tgt
	    cat $fsim >> data_corpus/trn_sim
	    cat $fpre >> data_corpus/trn_pre
	    echo train ok

	    echo val ...
	    fsrc=$stovec/clean.$corpus.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.src
	    ftgt=$stovec/clean.$corpus.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.tgt
	    fsim=$stovec/clean.$corpus.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.sim
	    fpre=$stovec/clean.$corpus.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.pre
	    cat $fsrc >> data_corpus/val_src
	    cat $ftgt >> data_corpus/val_tgt
	    cat $fsim >> data_corpus/val_sim
	    cat $fpre >> data_corpus/val_pre
	    echo val ok

	    echo test ...
	    fsrc_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.src
	    ftgt_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.tgt
	    fsim_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.sim
	    fpre_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.pre
	    cat $fsrc >> data_corpus/tst_src
	    cat $ftgt >> data_corpus/tst_tgt
	    cat $fsim >> data_corpus/tst_sim
	    cat $fpre >> data_corpus/tst_pre
	    echo test ok

   echo corpus suivant :

  done