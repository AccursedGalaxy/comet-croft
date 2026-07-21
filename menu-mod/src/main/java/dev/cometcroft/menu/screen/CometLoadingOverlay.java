package dev.cometcroft.menu.screen;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.function.Consumer;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.LoadingOverlay;
import net.minecraft.network.chat.Component;
import net.minecraft.server.packs.resources.ReloadInstance;
import net.minecraft.util.FormattedCharSequence;

/**
 * The Comet Croft boot loading screen: the shared {@link CometSky} scene, a
 * lantern-gold progress bar, and a rotating onboarding tip — replacing the
 * vanilla Mojang logo overlay (and, by extension, any loading-screen mod).
 *
 * <p>Fade-in/out and completion semantics mirror vanilla {@link LoadingOverlay}:
 * smooth progress, a fade-out once the reload finishes, exceptions routed to
 * the {@code onFinish} callback, and the overlay clearing itself when done.
 *
 * <p>Tips are data, not code: read once from {@code config/cometcroft/tips.txt}
 * (one tip per line, {@code #} comments allowed), so copy edits ship with the
 * pack and never need a mod rebuild. A minimal built-in list is the fallback.
 */
public final class CometLoadingOverlay extends LoadingOverlay {

    // palette (design tokens, ARGB)
    private static final int BAR_FILL = 0xFFFFCB6E;
    private static final int BAR_BACK = 0xCC0E1636;
    private static final int BAR_EDGE = 0x40FFCD96;
    private static final int TIP_COLOR = 0xFFB9C2DA;
    private static final int MUTED = 0xFF7F8BAB;

    private static final float TIP_SECONDS = 8f;

    private static final String[] FALLBACK_TIPS = {
        "Open your inventory and hover an item, then press R to see how it's made. Press U to see what it's for.",
        "A croft is a small homestead. This one's yours.",
    };

    private final Minecraft minecraft;
    private final ReloadInstance reload;
    private final Consumer<Optional<Throwable>> onFinish;
    private final boolean fadeIn;

    private final CometSky sky = new CometSky();
    private final List<String> tips;
    private final Random tipRng = new Random();
    private int tipIndex;
    private float tipNextAt = TIP_SECONDS;

    private float progress;
    private long fadeInStart = -1L;
    private long fadeOutStart = -1L;

    public CometLoadingOverlay(Minecraft minecraft, ReloadInstance reload,
                               Consumer<Optional<Throwable>> onFinish, boolean fadeIn) {
        super(minecraft, reload, onFinish, fadeIn);
        this.minecraft = minecraft;
        this.reload = reload;
        this.onFinish = onFinish;
        this.fadeIn = fadeIn;
        this.tips = loadTips();
        this.tipIndex = tipRng.nextInt(this.tips.size());
    }

    private static List<String> loadTips() {
        try {
            Path path = FabricLoader.getInstance().getGameDir().resolve("config/cometcroft/tips.txt");
            List<String> lines = Files.readAllLines(path).stream()
                    .map(String::trim)
                    .filter(l -> !l.isEmpty() && !l.startsWith("#"))
                    .toList();
            if (!lines.isEmpty()) return lines;
        } catch (Throwable ignored) {
            // missing or unreadable file → fallback below
        }
        return List.of(FALLBACK_TIPS);
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor gfx, int mouseX, int mouseY, float partialTick) {
        int w = minecraft.getWindow().getGuiScaledWidth();
        int h = minecraft.getWindow().getGuiScaledHeight();
        long millis = System.currentTimeMillis();

        if (fadeIn && fadeInStart == -1L) fadeInStart = millis;
        float fadeOut = fadeOutStart > -1L ? (millis - fadeOutStart) / 300f : -1f;
        float fadeInT = fadeInStart > -1L ? (millis - fadeInStart) / 500f : -1f;

        // fully faded out → hand the frame back to whatever is beneath us
        if (fadeOut >= 1f) {
            if (minecraft.getOverlay() == this) minecraft.setOverlay(null);
            return;
        }

        // the living sky
        sky.tick(mouseX, mouseY, w, h);
        sky.render(gfx, w, h);

        // smoothed progress (vanilla's 0.95/0.05 blend)
        float actual = reload.getActualProgress();
        progress = Math.max(0f, Math.min(1f, progress * 0.95f + actual * 0.05f));

        // progress bar: bottom-centered, mirrors the pack's bar styling
        int bw = Math.min(364, w - 80);
        int bx = (w - bw) / 2;
        int by = h - 39;
        gfx.fill(bx, by, bx + bw, by + 10, BAR_BACK);
        gfx.outline(bx, by, bw, 10, BAR_EDGE);
        int fill = (int) ((bw - 4) * progress);
        if (fill > 0) gfx.fill(bx + 2, by + 2, bx + 2 + fill, by + 8, BAR_FILL);

        // rotating tip beneath the bar, wrapped and centered
        Font font = minecraft.font;
        if (sky.time() >= tipNextAt) {
            tipNextAt = sky.time() + TIP_SECONDS;
            if (tips.size() > 1) tipIndex = (tipIndex + 1 + tipRng.nextInt(tips.size() - 1)) % tips.size();
        }
        int ty = by + 14;
        for (FormattedCharSequence line : font.split(Component.literal(tips.get(tipIndex)), Math.min(480, w - 60))) {
            gfx.text(font, line, (w - font.width(line)) / 2, ty, TIP_COLOR, true);
            ty += font.lineHeight + 2;
        }

        // quiet footer, same voice as the title screen
        String brand = "Comet Croft";
        gfx.text(font, brand, (w - font.width(brand)) / 2, h - 14, MUTED, true);

        // completion: run callbacks once, then start the fade
        if (reload.isDone() && fadeOutStart == -1L) {
            fadeOutStart = millis;
            try {
                reload.checkExceptions();
                onFinish.accept(Optional.empty());
            } catch (Throwable t) {
                onFinish.accept(Optional.of(t));
            }
        }

        // fade-in scrim: night ink → scene. There is no fade-OUT scrim on
        // purpose: the title screen behind renders the same CometSky scene, so
        // the short hold (300ms) followed by a cut reads as one continuous sky.
        if (fadeOutStart == -1L && fadeIn && fadeInT < 1f) {
            int a = (int) ((1f - Math.max(0f, fadeInT)) * 255);
            gfx.fill(0, 0, w, h, (a << 24) | 0x070C18);
        }
    }

    @Override
    public boolean isPauseScreen() {
        return true;
    }
}
