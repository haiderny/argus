YES/NO question answering
=========================

Run:

	python web_interface.py

then open http://0.0.0.0:5500/

Setup
-----

	python -m nltk.downloader maxent_treebank_pos_tagger

Testing
-------
With mTurk output files present in tests/batches, running

	python batch_test.py

will create output.tsv in tests folder  
!!! Guardian API permits only 5000 searches per day !!!

Algorithm
---------

We extract keywords (mostly names and other nouns) from given question, then ask The Guardian for articles containing all keywords.  
We expand the keywords by adding non-stop-words verbs. Then we check if we covered all non-stop-words; if we didn't the answer is "Didn't understand the question". Otherwise we continue evaluating.  
We then divide the first found article into sentences and look for a sentence with all the keywords in it. If we can't find one, our answer is 'Not sure'. If we do, we evaluate sentiment(sum of emotionaly colored words) of the question, sentence and headline. Sentiments are then input to a logistic regression classifier.
