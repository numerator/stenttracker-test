# stenttracker-test

Usage:

$ python3 load_stories.py <args>
  
'args' can be the id of a story (e.g., u2, c3), a list of stories separated by spaces(?), or 'all'


The json messages in the stories folder map onto the stories described in this document: 

https://docs.google.com/document/d/1UaZW3kFvaPePGfNLEp8SYxABcuTc8hF3b9cDWeyMM8k/edit?usp=sharing

The file stories.csv contains metadata for each message that links them to the story. The most important function of this file is to indicate the time offset (ts_offset) for each message relative to the beginning of the story. The offset is expressed in days.


And a testing grid that was used to test the initial version is here: 

https://docs.google.com/document/d/18XcRjAVp0_qhhUJd0sbJyiRsuEUnTL5kPntvSxDPM6E/edit?usp=sharing


