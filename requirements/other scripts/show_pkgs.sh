rm show1.txt
for p in `pip freeze | cut -d'=' -f1`; do pip show $p >> show1.txt; echo '----' >> show1.txt; done;

