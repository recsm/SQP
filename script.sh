for i in `ls -aR |grep \.svn`
do
    rm $i -Rf 
done

