# DG_MI_model


This project induce dependency grammar in two ways: using Mutual Information and DMV algorithm. The code used for DMV can be found in this <a href="https://github.com/jxhe/struct-learning-with-flow/">repository</a>.




<h1>Indigenous Training</h1>

The training employs languages with a limited amount of data, and the original dataset lacks both a training and test set. Consequently, we conduct cross-validation using the available data. <br>


First, run the cv.py code to create cross validation data.


```
python3 cv.py --PATH_data ~/DG_MI_model/data --PATH_dest ~/DG_MI_model/data_cv
```


<h2>Training MI</h2>

Run run_MI.py. Max_d_r means the maximum distance between two token within the relation. Max_s is the maximum sentence distance allowed. The code run a combination of these configurations. <br>

```
python3 run_MI.py --PATH ~/DG_MI_model/data_cv/ --max_d_r 2,3,4,5 --max_s 10,40
```

The result is recorded on `MI_results/results_MI.txt`



<h2>Training DMV</h2>

Clone this <a href="https://github.com/jxhe/struct-learning-with-flow/">repository</a> and replace the code `replace_dmv_codes/modules/util.py`, `replace_dmv_codes/modules/dmv_viterbi_model.py` and `replace_dmv_codes/dmv_viterbi_code.py` by their respectives in the original repository. <br>


In the lines 124 you must change the maximum tokens per sentence in  `parse_args = init_config(40)` and `main(parse_args,40)` in line 125, for sentence at most 40 tokens. <br>

```
python dmv_viterbi_train.py --train_file ~/data_cv/Nheengatu/Nheengatu__0__train.conllu --test_file ~/data_cv/Nheengatu/Nheengatu__0__test.conllu > results_Nheengatu_0_40.txt
```
You need to run every folder from cross validation. <br>


Copy the files results to the `DMV_results/DMV_<size>` folder. <br>

To summarized the DMV results for each sentence, since the original code do note provide that information, you can run. <br>
```
python3 summarize_dmv_results.py --PATH_R ~/DG_MI_model/DMV_results/DMV_10/ --PATH_CV ~/ProjectGit/DG_MI_model/data_cv/
```
