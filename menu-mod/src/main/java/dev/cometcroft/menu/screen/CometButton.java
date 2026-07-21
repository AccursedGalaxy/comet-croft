package dev.cometcroft.menu.screen;

import java.util.function.Consumer;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.input.InputWithModifiers;
import net.minecraft.network.chat.Component;
import org.joml.Matrix3x2fStack;

/**
 * The pack's bespoke pixel-bevel button, built to the menu design system:
 * warm-dark gradient fill, light top/left + dark bottom bevel edges, lantern
 * hover glow, and a double-ring lantern focus outline. Keyboard/controller
 * activation, click sound, and cursor handling are inherited from
 * {@link AbstractButton}.
 */
final class CometButton extends AbstractButton {

    enum Style { HERO, PRIMARY, UTILITY, UTILITY_WARN, CONFIRM_ACCENT, CONFIRM_QUIET }

    // palette (ARGB)
    private static final int FOCUS_OUTER = 0xFFFFB454; // lantern
    private static final int FOCUS_INNER = 0xFF0B1120; // night ink

    private final Style style;
    private final String sub;          // flavor / meta line (nullable)
    private final Consumer<CometButton> onPress;

    CometButton(int x, int y, int w, int h, Style style, Component label, String sub,
                Consumer<CometButton> onPress) {
        super(x, y, w, h, label);
        this.style = style;
        this.sub = sub;
        this.onPress = onPress;
    }

    @Override
    public void onPress(InputWithModifiers input) {
        this.onPress.accept(this);
    }

    @Override
    protected void updateWidgetNarration(NarrationElementOutput output) {
        this.defaultButtonNarrationText(output);
    }

    @Override
    protected void extractContents(GuiGraphicsExtractor gfx, int mouseX, int mouseY, float partialTick) {
        int x = getX(), y = getY(), w = getWidth(), h = getHeight();
        boolean hot = isHoveredOrFocused() && this.active;

        int fillTop, fillBottom, edgeLight, labelColor, subColor;
        switch (style) {
            case HERO -> {
                fillTop = hot ? 0xF25A3C1E : 0xE64A3018;
                fillBottom = hot ? 0xF2382416 : 0xF02C1C10;
                edgeLight = 0x47FFCE8C;
                labelColor = 0xFFFFF3DC;
                subColor = 0xFFE7C79A;
            }
            case PRIMARY -> {
                fillTop = hot ? 0xE62E2820 : 0xD11E1914;
                fillBottom = hot ? 0xF01E1914 : 0xE6120F0C;
                edgeLight = 0x1FFFECCD;
                labelColor = 0xFFEEF1F7;
                subColor = 0xFF8592B0;
            }
            case UTILITY_WARN -> {
                fillTop = hot ? 0xD1382220 : 0xB8261412;
                fillBottom = hot ? 0xD1261412 : 0xB81C0F0E;
                edgeLight = 0x24FF9678;
                labelColor = hot ? 0xFFFFB0A0 : 0xFFD79A8C;
                subColor = 0xFF8592B0;
            }
            case CONFIRM_ACCENT -> {
                fillTop = hot ? 0xFFFFC26E : 0xFFFFB454;
                fillBottom = hot ? 0xFFFA9E4C : 0xFFF4913E;
                edgeLight = 0x66FFF3DC;
                labelColor = 0xFF2A1206;
                subColor = 0xFF2A1206;
            }
            default -> { // UTILITY / CONFIRM_QUIET
                fillTop = hot ? 0xD1242C48 : 0xB8141A2C;
                fillBottom = hot ? 0xD1141A2C : 0xB80E1322;
                edgeLight = 0x1AFFECCD;
                labelColor = 0xFFCFD6E6;
                subColor = 0xFF8592B0;
            }
        }
        if (!this.active) {
            labelColor = 0xFF6F7C9B;
            subColor = 0xFF55617D;
        }

        // drop shadow under the bevel
        gfx.fill(x + 1, y + h, x + w + 1, y + h + 2, 0x66000000);
        // fill
        gfx.fillGradient(x, y, x + w, y + h, fillTop, fillBottom);
        // bevel: light top/left, dark right/bottom (thick bottom edge)
        gfx.fill(x, y, x + w, y + 1, edgeLight);
        gfx.fill(x, y, x + 1, y + h, edgeLight);
        gfx.fill(x + w - 1, y + 1, x + w, y + h, 0x73000000);
        gfx.fill(x + 1, y + h - 2, x + w, y + h, 0x99000000);

        // hover: lantern inner outline
        if (hot) {
            gfx.outline(x, y, w, h, 0x59FFB454);
        }
        // focus: double ring, drawn outside the button
        if (isFocused()) {
            gfx.outline(x - 2, y - 2, w + 4, h + 4, FOCUS_INNER);
            gfx.outline(x - 3, y - 3, w + 6, h + 6, FOCUS_OUTER);
        }

        Font font = Minecraft.getInstance().font;
        Matrix3x2fStack pose = gfx.pose();
        String label = getMessage().getString();

        switch (style) {
            case HERO -> {
                // lantern marker
                int mx = x + 10, my = y + h / 2;
                gfx.fill(mx, my - 3, mx + 6, my + 3, 0xFFFFB454);
                gfx.fill(mx + 1, my - 4, mx + 5, my + 4, 0x66FFB454);
                // label at 2x, flavor line beneath
                pose.pushMatrix();
                pose.translate(x + 24, y + (h - (18 + (sub != null ? 11 : 0))) / 2f);
                pose.scale(2.0f);
                gfx.text(font, label, 0, 0, labelColor);
                pose.popMatrix();
                if (sub != null) {
                    gfx.text(font, sub, x + 24, y + (h - 29) / 2 + 20, subColor);
                }
                gfx.text(font, ">", x + w - 12, y + (h - 8) / 2, subColor);
            }
            case PRIMARY -> {
                gfx.fill(x + 9, y + h / 2 - 2, x + 13, y + h / 2 + 2, 0xFFFFB454);
                pose.pushMatrix();
                pose.translate(x + 22, y + (h - 12) / 2f);
                pose.scale(1.34f);
                gfx.text(font, label, 0, 0, labelColor);
                pose.popMatrix();
                // right-aligned flavor text, only when it fits clear of the label
                if (sub != null && 22 + font.width(label) * 1.34f + 14 + font.width(sub) + 8 < w) {
                    gfx.text(font, sub, x + w - 8 - font.width(sub), y + (h - 8) / 2 + 1, subColor);
                }
            }
            case CONFIRM_ACCENT, CONFIRM_QUIET -> {
                gfx.centeredText(font, label, x + w / 2, y + (h - 8) / 2, labelColor);
            }
            default -> { // UTILITY / UTILITY_WARN
                int tw = font.width(label);
                gfx.text(font, label, x + (w - tw) / 2, y + (h - 8) / 2, labelColor);
            }
        }
    }
}
