%% language = \{ w\#w \mid w \in \{0,1\}^\ast \}
%% question = Give a Turing Machine that generates the language $@language@$.

initial q1
accept q_accept
input_symbols 0 1 #
tape_symbols 0 1 # x □
q1 q2 0x,R
q1 q3 1x,R
q1 q8 ##,R
q2 q2 00,R 11,R
q2 q4 ##,R
q3 q3 00,R 11,R
q3 q5 ##,R
q4 q4 xx,R
q4 q6 0x,L
q5 q5 xx,R
q5 q6 1x,L
q6 q6 00,L 11,L xx,L
q6 q7 ##,L
q7 q7 00,L 11,L
q7 q1 xx,R
q8 q8 xx,R
q8 q_accept □□,R
