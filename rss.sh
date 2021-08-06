destination_folder="D:/RSS"

checkers=10
transfers=10
timeoutn=7200

for ((i = 0; i < 9999999; i++)); do
    echo "########################### New turn ###########################"
    date
    starttime=`LC_TIME=en_US date`
    echo "rclone -v copy RSS gd:RSS --checkers ${checkers} --transfers ${transfers} --exclude *.!qB --exclude-from exclude-file.txt"
    rclone -v copy "${destination_folder}" gd:RSS --checkers ${checkers} --transfers ${transfers} --exclude *.!qB --exclude-from exclude-file.txt
    if [ $? -eq 0 ]
    then
        echo "Success: rclone finished successfully. Deleting all torrents before ${starttime}..."
        python qbit_auto.py "${starttime}"
        if [ $? -eq 0 ]
        then
            echo "Success: Deleting finished successfully."
        else
            echo "Failure: Deleting didn't finished." >&2
        fi
    else
        echo "Failure: rclone didn't finished." >&2
    fi
    echo "You can delete all torrents finished before ${starttime}" | tee -a rss.log
    echo "########################### Finished ###########################\n\n\n\n"
    sleep ${timeoutn}
done