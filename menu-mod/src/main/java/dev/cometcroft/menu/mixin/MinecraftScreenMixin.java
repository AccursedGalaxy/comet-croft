package dev.cometcroft.menu.mixin;

import dev.cometcroft.menu.screen.CometCroftTitleScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import org.spongepowered.asm.mixin.Mixin;
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

    @ModifyVariable(method = "setScreen", at = @At("HEAD"), argsOnly = true)
    private Screen cometcroft$swapOnSet(Screen screen) {
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
}
