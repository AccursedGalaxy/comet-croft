package dev.cometcroft.menu;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Client entrypoint for the Comet Croft custom main-menu mod.
 *
 * <p>This mod takes over the vanilla title screen and replaces it with a bespoke
 * screen built to the "homestead under a strange sky" identity. For now this
 * entrypoint just proves the jar loads in the dev instance; the title-screen
 * takeover mixin follows.
 */
public class CometCroftMenuClient implements ClientModInitializer {
    public static final String MOD_ID = "cometcroft";
    public static final Logger LOGGER = LoggerFactory.getLogger("CometCroft");

    @Override
    public void onInitializeClient() {
        LOGGER.info("[CometCroft] custom menu mod loaded — the lantern is lit.");
    }
}
