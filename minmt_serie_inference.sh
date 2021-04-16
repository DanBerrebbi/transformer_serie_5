#!/bin/bash


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
#dnet=$PWD/model_serie
dnet=$PWD/model_checkpoint


	for corpus in ECB EMEA Europarl ; do
	    echo $corpus
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

echo debut de l inference


fmod=$dnet/network.checkpoint_00030000.pt ####### A MODIF
fout=$dnet/$corpus.out_k5_avg_alpha0.7
CUDA_VISIBLE_DEVICES=0 python3 $trans -dnet $dnet -m $fmod -batch_size 10 -beam_size 5 -alpha 0.7 -i_src data_corpus/tst_src -i_sim data_corpus/tst_sim -i_pre data_corpus/tst_pre -o $fout -cuda -log_file $fout.log

echo fin de l inference
