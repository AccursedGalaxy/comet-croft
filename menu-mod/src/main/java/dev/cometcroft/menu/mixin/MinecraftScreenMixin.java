package dev.cometcroft.menu.mixin;

import dev.cometcroft.menu.screen.CometCroftTitleScreen;
import dev.cometcroft.menu.screen.CometLoadingOverlay;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.LoadingOverlay;
import net.minecraft.client.gui.screens.Overlay;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.multiplayer.ClientLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Takes over the vanilla title screen. Whenever the game asks to show a
 * {@link TitleScreen}, we swap in our bespoke {@link CometCroftTitleScreen}
 * instead — before {@code setScreen} does anything with it.
 *
 * <p>We match the vanilla class exactly ({@code == TitleScreen.class}) so we
 * never hijack a modded subclass, and so our own screen (not a TitleScreen)
 * passes straight through.
 */
@Mixin(Minecraft.class)
public class MinecraftScreenMixin {

    @Shadow public ClientLevel level;
    @Shadow private boolean clientLevelTeardownInProgress;

    /**
     * {@code setScreen(null)} outside a world (the default {@link Screen#onClose()}
     * of every screen that doesn't track a parent) makes vanilla build a fresh
     * {@code new TitleScreen()} INSIDE setScreen — after any head injection could
     * see it. Supplying our screen up front for that exact case keeps the vanilla
     * fallback branch dead. Teardown-in-progress stays null so vanilla's
     * "return to in-game GUI during disconnection" guard still fires.
     */
    @ModifyVariable(method = "setScreen", at = @At("HEAD"), argsOnly = true)
    private Screen cometcroft$swapOnSet(Screen screen) {
        if (screen == null && this.level == null && !this.clientLevelTeardownInProgress) {
            return new CometCroftTitleScreen();
        }
        return cometcroft$maybeSwap(screen);
    }

    @ModifyVariable(method = "setScreenAndShow", at = @At("HEAD"), argsOnly = true)
    private Screen cometcroft$swapOnShow(Screen screen) {
        return cometcroft$maybeSwap(screen);
    }

    @Unique
    private static Screen cometcroft$maybeSwap(Screen screen) {
        if (screen != null && screen.getClass() == TitleScreen.class) {
            return new CometCroftTitleScreen();
        }
        return screen;
    }

    /**
     * Takes over the boot loading overlay the same way: match the vanilla
     * class exactly, rebuild ours around the same reload + callback. While a
     * loading-screen mod (e.g. Drippy) is installed its overlay is a different
     * class, so this swap stays dormant — remove that mod and ours takes over
     * on the next launch, no config needed.
     */
    @ModifyVariable(method = "setOverlay", at = @At("HEAD"), argsOnly = true)
    private Overlay cometcroft$swapOverlay(Overlay overlay) {
        if (overlay != null && overlay.getClass() == LoadingOverlay.class) {
            LoadingOverlayAccessor acc = (LoadingOverlayAccessor) overlay;
            return new CometLoadingOverlay((Minecraft) (Object) this,
                    acc.cometcroft$reload(), acc.cometcroft$onFinish(), acc.cometcroft$fadeIn());
        }
        return overlay;
    }
}
