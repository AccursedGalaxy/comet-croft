package dev.cometcroft.menu.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.lang.reflect.Field;

/**
 * Daily Quests draws collapsed quest entries as mini progress bars with no
 * option to hide them; we cancel the whole overlay while the list is
 * collapsed so `.` truly toggles the HUD. No compile-time dependency on the
 * mod: the target is named by string and the collapsed flag read via
 * reflection.
 */
@Pseudo
@Mixin(targets = "com.natamus.dailyquests_common_fabric.events.DailyQuestsClientEvents", remap = false)
public class DailyQuestsHudMixin {

    private static Field cometcroft$collapsedField;
    private static boolean cometcroft$lookupFailed;

    @Inject(method = "renderOverlay", at = @At("HEAD"), cancellable = true, require = 0)
    private static void cometcroft$hideWhenCollapsed(CallbackInfo ci) {
        if (cometcroft$isCollapsed()) {
            ci.cancel();
        }
    }

    private static boolean cometcroft$isCollapsed() {
        if (cometcroft$lookupFailed) {
            return false;
        }
        try {
            if (cometcroft$collapsedField == null) {
                Class<?> variables = Class.forName(
                        "com.natamus.dailyquests_common_fabric.data.VariablesClient");
                cometcroft$collapsedField = variables.getField("questListCollapsed");
            }
            return cometcroft$collapsedField.getBoolean(null);
        } catch (ReflectiveOperationException e) {
            cometcroft$lookupFailed = true;
            return false;
        }
    }
}
