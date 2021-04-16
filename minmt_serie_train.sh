#!/bin/bash


josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/

vocab=$PWD/minmt-vocab.py
setup=$PWD/minmt-setup.py
train=$PWD/minmt-train.py      # j'ai modifié certains fichiers par rapport au Git
avrge=$PWD/minmt-average.py
trans=$PWD/minmt-translate.py

tokenizer=$josep/MiNMT/tools/tokenizer.py
data=$josep/data
stovec=$josep/stovec

echo tokenizer
cat $setup

    dir=$josep/minmt_base
    dnet=$PWD/model_serie

    if true; then
	python3 $setup -dnet $dnet -src_voc $dir/enfr.BPE.32k.voc -tgt_voc $dir/enfr.BPE.32k.voc

	echo setup ok

mkdir "data_corpus"

	for corpus in ECB EMEA Europarl ; do
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



  	echo debut du training

	CUDA_VISIBLE_DEVICES=0 python3 $train -dnet $dnet -src_train data_corpus/trn_src  -sim_train data_corpus/trn_sim  -pre_train data_corpus/trn_pre  -tgt_train data_corpus/trn_tgt  -src_valid data_corpus/val_src  -sim_valid data_corpus/val_sim  -pre_valid data_corpus/val_pre  -tgt_valid data_corpus/val_tgt -max_steps 450000 -loss KLDiv -cuda -log_file $dnet/log

		echo fin du training

fi