scoreboard players enable @a nv
execute as @a[scores={nv=1..}] run function cometcroft:nv_toggle
# Re-apply each tick so night vision survives death and milk for tagged players.
effect give @a[tag=cc_nv] minecraft:night_vision infinite 0 true
