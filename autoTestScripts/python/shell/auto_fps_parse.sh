#!/bin/sh

function file_exist() {
    if [ -e $file ];then
    echo "$file exist"
    else
        echo "$file not exist"
    fi
}


function getdir(){
 echo $1
 fps_file=""
 parse_file=""
 parse_dir=""
 # shellcheck disable=SC2045

 for element in $(ls $1);
 do
  dir_or_file=$1"/"$element
  echo "start ------ $dir_or_file"
  if [ -d $dir_or_file ]
  then
#  cd $dir_or_file;
#  parse_dir=$dir_or_file
#  echo "start parse_dir------ $parse_dir"
  getdir $dir_or_file
  else
#  echo $dir_or_file
echo "start parse_dir------ $1"
    if [ "fps_info_parse.sh" == "$element" ]
    then
      parse_file=$dir_or_file
    fi

    if [ "fps_temp.txt" == "$element" ]
    then
      fps_file=$dir_or_file
    fi

    echo "$fps_file,$parse_file"
    if [ -n "$fps_file" -a -n "$parse_file" ]
    then
      echo "succuss"
      sh $parse_file "$TYPE_COMMAND" $fps_file $1
    fi
    echo "next"
  fi
 done
}
root_dir="."
TYPE_COMMAND=$1
if [ -z "$TYPE_COMMAND" ]; then
  TYPE_COMMAND=""
fi
echo "TYPE_COMMAND:"$TYPE_COMMAND
  getdir $root_dir





