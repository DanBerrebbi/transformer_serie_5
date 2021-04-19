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
dnet=$PWD/model_serie


fmod=$dnet/network.checkpoint_00450000.pt ####### A MODIF


	    fsrc=src_debug_bleu
	    ftgt=tgt_debug_bleu
	    fsim=sim_debug_bleu
	    fpre=pre_debug_bleu
      fout=traduction_debug_bleu
      CUDA_VISIBLE_DEVICES=0 python3 $trans -dnet $dnet -m $fmod -batch_size 10 -beam_size 5 -alpha 0.7 -i_src $fsrc -i_sim $fsim -i_pre $fpre -o $fout -cuda -log_file $fout.log &


