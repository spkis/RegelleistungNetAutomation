# Overview
This repo includes scripts to download data from Regelleistung.net and uses telegraf configurations to automatically make the downloaded files to a influxDB database. 
You just need to configure your bucket/token/server and that's it - or you use file output.

After testing - make sure that you configure telegraf to only output the outputs, you actually want to have. 

If there are issues - feel free to reach out. Adding more scripts for other files as well eventually. 

# Telegraf
There is a general Telegraf Configuration, which works across each individual integration. It is in the root directory.