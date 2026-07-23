execute if score gm4 load.status matches 1 if score gm4_minor load.status matches 9.. run scoreboard players set gm4_desire_lines load.status 1
execute if score gm4 load.status matches 1 if score gm4_minor load.status matches 9.. run scoreboard players set gm4_desire_lines_minor load.status 7
execute unless score gm4 load.status matches 1.. run data modify storage gm4:log queue append value {type:"missing",module:"Desire Lines",id:"gm4_desire_lines",require:"Gamemode 4 Base",require_id:"gm4"}
execute if score gm4 load.status matches 1.. unless score gm4 load.status matches 1 run data modify storage gm4:log queue append value {type:"version_conflict",module:"Desire Lines",id:"gm4_desire_lines",require:"Gamemode 4 Base",require_id:"gm4",require_ver:"1.9.0"}
execute if score gm4 load.status matches 1 unless score gm4_minor load.status matches 9.. run data modify storage gm4:log queue append value {type:"version_conflict",module:"Desire Lines",id:"gm4_desire_lines",require:"Gamemode 4 Base",require_id:"gm4",require_ver:"1.9.0"}
execute unless score gm4_desire_lines load.status matches 1.. run scoreboard players set gm4_desire_lines load.status -1

execute if score gm4_desire_lines load.status matches 1 run function gm4_desire_lines:init
execute unless score gm4_desire_lines load.status matches 1 run schedule clear gm4_desire_lines:tick
