package dev.cometcroft.menu.mixin;

import java.util.Optional;
import java.util.function.Consumer;

import net.minecraft.client.gui.screens.LoadingOverlay;
import net.minecraft.server.packs.resources.ReloadInstance;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Reads the vanilla {@link LoadingOverlay}'s private constructor state so the
 * swap-in mixin can rebuild a {@code CometLoadingOverlay} around the same
 * reload instance and completion callback.
 */
@Mixin(LoadingOverlay.class)
public interface LoadingOverlayAccessor {

    @Accessor("reload")
    ReloadInstance cometcroft$reload();

    @Accessor("onFinish")
    Consumer<Optional<Throwable>> cometcroft$onFinish();

    @Accessor("fadeIn")
    boolean cometcroft$fadeIn();
}
