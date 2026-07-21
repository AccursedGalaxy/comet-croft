execute store result score @s cc_nv_tmp if entity @s[tag=cc_nv]
execute if score @s cc_nv_tmp matches 1 run function cometcroft:nv_off
execute if score @s cc_nv_tmp matches 0 run function cometcroft:nv_on
scoreboard players set @s nv 0
