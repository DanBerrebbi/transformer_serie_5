#!/bin/bash


josep=/nfs/RESEARCH/crego/projects/PrimingNMT-2/

vocab=$PWD/minmt-vocab.py
setup=$PWD/minmt-setup.py
train=$PWDT/minmt-train.py      # j'ai modifié certains fichiers par rapport au Git 
avrge=$PWD/minmt-average.py
trans=$PWD/minmt-translate.py

tokenizer=$josep/MiNMT/tools/tokenizer.py
data=$josep/data
stovec=$josep/stovec

echo tokenizer 
cat $setup

    dir=$josep/minmt_base
    dnet=$PWD/model_serie_true
    #rm -r $dnet

    if false; then
	python3 $setup -dnet $dnet -src_voc $dir/enfr.BPE.32k.voc -tgt_voc $dir/enfr.BPE.32k.voc 

	echo setup ok 
# je ne travaille que sur Europarl 

	fsrc=$stovec/clean.Europarl.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.src
	ftgt=$stovec/clean.Europarl.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.tgt
	fsim=$stovec/clean.Europarl.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.sim
	fpre=$stovec/clean.Europarl.en-fr.en.trn.bpe.vec.max_sim0.5_k5_n0_t0.8.pre 
	   
	fsrc_val=$stovec/clean.Europarl.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.src
	ftgt_val=$stovec/clean.Europarl.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.tgt
	fsim_val=$stovec/clean.Europarl.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.sim
	fpre_val=$stovec/clean.Europarl.en-fr.en.val.bpe.vec.sim0.5_k5_n0_t0.8.pre
	    
	echo debut du training
	    
	CUDA_VISIBLE_DEVICES=0 python3 $train -dnet $dnet -src_train $fsrc  -sim_train $fsim  -pre_train $fpre  -tgt_train $ftgt -src_valid $fsrc_val  -sim_valid $fsim_val -pre_valid $fpre_val -tgt_valid $ftgt_val -max_steps 400000 -loss KLDiv -cuda -log_file $dnet/log & 
		
		echo fin du training
    fi
    
    if true; then
	#python3 $avrge -dnet $dnet
	for corpus in Europarl ; do
	   # ftst=$data/clean.$corpus.en-fr.en.tst.bpe
	    fref=$data/clean.$corpus.en-fr.fr.tst
	    fsrc_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.src
	    ftgt_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.tgt
	    fsim_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.sim
	    fpre_tst=$stovec/clean.Europarl.en-fr.en.tst.bpe.vec.sim0.5_k5_n0_t0.8.pre
	    fmod=$dnet/network.checkpoint_00030000.pt ####### A MODIF 
	    fout=$dnet/$corpus.out_k5_avg_alpha0.7
	    CUDA_VISIBLE_DEVICES=0 python3 $trans -dnet $dnet -m $fmod -batch_size 10 -beam_size 5 -alpha 0.7 -i_src  $fsrc_tst -i_sim $fsim_tst -i_pre $fpre_tst -o $fout -cuda -log_file $fout.log &
	    sort -g $fout | cut -f 2 | python3 $tokenizer -tok_config $data/BPE_config -detok | sacrebleu --force $fref > $fout.bleu
	    cat $fout.bleu
	done
    fi

