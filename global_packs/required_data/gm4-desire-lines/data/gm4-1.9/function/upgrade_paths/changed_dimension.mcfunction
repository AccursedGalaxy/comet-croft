# @s = player who just changed dimension
# at @s
# run from gm4-1.9:upgrade_paths/changed_dimension advancement
advancement revoke @s only gm4-1.9:upgrade_paths/changed_dimension
tag @s add gm4_running_upgrade_path
function gm4-1.9:upgrade_paths/run_when_loaded
