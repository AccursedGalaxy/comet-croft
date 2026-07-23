data modify storage gm4_guidebook:temp unlocking.uuid set from entity @s UUID
data modify storage gm4_guidebook:temp unlocking.name set value "desire_lines"
data modify storage gm4_guidebook:temp unlocking.target_page set value 1
data modify storage gm4_guidebook:temp unlocking.lectern_target_page set value 6
data modify storage gm4_guidebook:temp unlocking.source_page set value "trampling_foliage-boots_of_ostara-metallurgy"
function gm4_guidebook:player_db/update with storage gm4_guidebook:temp unlocking
data remove storage gm4_guidebook:temp unlocking
