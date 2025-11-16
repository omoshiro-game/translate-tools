
# How to use

```
python tools\stg4_tool.py export data\stg4\MyStage.stg4_1020 # and every other stages, one call per stage
python tools\keys_extract.py data\stg4
python tools\translate_pre.py data\stg4

# Translate the _todo.json here

python tools\translate_post.py data\stg4
python tools\keys_apply.py data\stg4
python tools\stg4_tool.py import data\stg4\MyStage.stg4_1020.json # for every json
```


# KeyExtract and KeyApply 
`python keys_extract.py path/to/your/json_folder`

recursive :
`python keys_extract.py -r path/to/your/json_folder`

Apply changes:
`python keys_apply.py path/to/your/json_folder`
