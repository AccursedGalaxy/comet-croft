package dev.cometcroft.menu.screen;

import java.util.Random;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen;
import net.minecraft.client.gui.screens.options.AccessibilityOptionsScreen;
import net.minecraft.client.gui.screens.options.LanguageSelectScreen;
import net.minecraft.client.gui.screens.options.OptionsScreen;
import net.minecraft.client.gui.screens.worldselection.SelectWorldScreen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.network.chat.Component;
import org.joml.Matrix3x2fStack;

import com.mojang.realmsclient.RealmsMainScreen;

/**
 * The Comet Croft main menu — a homestead under a strange sky.
 *
 * <p>Built to the menu design system: an animated night sky (layered gradient,
 * parallax twinkling stars, constellations, a periodic comet, sparse meteors,
 * a procedural pixel moon) above a blocky lit-window horizon; a left-anchored
 * button stack with a hero Singleplayer action; and warm lantern accents
 * against deep night blues throughout.
 */
public class CometCroftTitleScreen extends Screen {

    // --- palette (design tokens, ARGB; sky tokens live in CometSky) ---
    private static final int CREAM = 0xFFF7EAD0;
    private static final int LANTERN = 0xFFFFB454;
    private static final int SPLASH_GOLD = 0xFFFFD152;
    private static final int SUBTITLE = 0xFFB9C2DA;
    private static final int MUTED = 0xFF8592B0;
    private static final int FOOTER = 0xFF7F8BAB;

    private static final String[] SPLASHES = {
        "look up.", "now with comets!", "vanilla++ & cozy", "mind the meteor shower",
        "a strange sky awaits", "no grind, just growth", "the lantern is lit", "best enjoyed slowly"
    };

    private final String splash;
    private final int modCount;

    // the shared animated scene (also used by the loading overlay)
    private final CometSky sky = new CometSky();

    // ui state
    private boolean quitOpen;
    private boolean helpOpen;
    private String toast;
    private float toastUntil;

    // the How to Play panel copy (council-reviewed, humanized). The renderer
    // draws the "R:"/"U:" keybind rows in lantern gold, the rest in subtitle blue.
    private static final String[] HELP_LINES = {
        "Comet Croft is a cozy homestead pack.",
        "Farm through the seasons, build your",
        "croft, and keep an eye on the sky.",
        "",
        "Two keys do most of the work. Open",
        "your inventory, hover an item, and:",
        "",
        "R:  how is this made?",
        "U:  what's it used for?",
        "",
        "That's the whole trick. (R and U are",
        "the defaults. If they do nothing, check",
        "Options → Controls.) Nearly everything",
        "else you can just try.",
        "",
        "New here? Open the Comet Croft Field",
        "Guide in your starting inventory.",
    };

    public CometCroftTitleScreen() {
        super(Component.literal("Comet Croft"));
        Random rng = new Random();
        this.splash = SPLASHES[rng.nextInt(SPLASHES.length)];
        this.modCount = FabricLoader.getInstance().getAllMods().size();
    }

    // --- layout + widgets ---

    @Override
    protected void init() {
        if (quitOpen) {
            initQuitConfirm();
        } else if (helpOpen) {
            initHelpPanel();
        } else {
            initMainMenu();
        }
    }

    /** Y where the header block (wordmark + subtitle) ends, in gui coords. */
    private int headerBottom() {
        int topY = Math.max(16, (int) (this.height * 0.085f));
        int scale = wordmarkScale();
        // two wordmark lines + subtitle line + breathing room
        return topY + (font.lineHeight * 2 + 2) * scale + 6 + font.lineHeight;
    }

    private int wordmarkScale() {
        return this.height < 300 ? 3 : 4;
    }

    /** The one shared left edge for header, button stack, and footer. */
    private int leftPad() {
        return Math.max(20, (int) (this.width * 0.065f));
    }

    private void initMainMenu() {
        Minecraft mc = Minecraft.getInstance();
        int bw = Math.max(240, Math.min(420, (int) (this.width * 0.36f)));
        int bx = leftPad();

        int heroH = 34, rowH = 24, utilH = 18, gap = 6;
        int total = heroH + gap + (rowH + gap) * 3 + 4 + (utilH + gap) + utilH;
        // never above the header block; otherwise vertically centered
        int by = Math.max(headerBottom() + 12, (this.height - total) / 2);

        var hero = addRenderableWidget(new CometButton(bx, by, bw, heroH, CometButton.Style.HERO,
                Component.literal("Singleplayer"), "return to the croft",
                b -> mc.setScreen(new SelectWorldScreen(this))));
        int y = by + heroH + gap;
        addRenderableWidget(new CometButton(bx, y, bw, rowH, CometButton.Style.PRIMARY,
                Component.literal("Multiplayer"), "visit distant hearths",
                b -> mc.setScreen(new JoinMultiplayerScreen(this))));
        y += rowH + gap;
        addRenderableWidget(new CometButton(bx, y, bw, rowH, CometButton.Style.PRIMARY,
                Component.literal("Realms"), "your shared sky",
                b -> mc.setScreen(new RealmsMainScreen(this))));
        y += rowH + gap;
        addRenderableWidget(new CometButton(bx, y, bw, rowH, CometButton.Style.PRIMARY,
                Component.literal("Mods"), "the pack's makings",
                b -> openModsScreen(mc)));
        y += rowH + gap + 4;

        // the onboarding touchpoint: full-width, always one glance below the stack
        addRenderableWidget(new CometButton(bx, y, bw, utilH, CometButton.Style.UTILITY,
                Component.literal("How to Play"), null,
                b -> { helpOpen = true; rebuildWidgets(); }));
        y += utilH + gap;

        // utility row: Options | language | accessibility | quit
        int quitW = 34, smallW = 34;
        int optW = bw - (smallW + quitW + smallW) - gap * 3;
        int x = bx;
        addRenderableWidget(new CometButton(x, y, optW, utilH, CometButton.Style.UTILITY,
                Component.literal("Options"), null,
                b -> mc.setScreen(new OptionsScreen(this, mc.options, false))));
        x += optW + gap;
        String lang = langCode(mc);
        addRenderableWidget(new CometButton(x, y, smallW, utilH, CometButton.Style.UTILITY,
                Component.literal(lang), null,
                b -> mc.setScreen(new LanguageSelectScreen(this, mc.options, mc.getLanguageManager()))));
        x += smallW + gap;
        addRenderableWidget(new CometButton(x, y, smallW, utilH, CometButton.Style.UTILITY,
                Component.literal("a11y"), null,
                b -> mc.setScreen(new AccessibilityOptionsScreen(this, mc.options))));
        x += smallW + gap;
        addRenderableWidget(new CometButton(x, y, quitW, utilH, CometButton.Style.UTILITY_WARN,
                Component.literal("Quit"), null,
                b -> { quitOpen = true; rebuildWidgets(); }));

        setInitialFocus(hero);
    }

    /** Height of the How to Play panel body (text lines only), in gui px. */
    private int helpBodyHeight() {
        return HELP_LINES.length * (font.lineHeight + 2);
    }

    private void initHelpPanel() {
        int pw = Math.min(300, this.width - 40);
        int ph = 24 + helpBodyHeight() + 30;
        int px = (this.width - pw) / 2;
        int py = Math.max(8, (this.height - ph) / 2);
        var back = addRenderableWidget(new CometButton(px + (pw - 140) / 2, py + ph - 26, 140, 20,
                CometButton.Style.CONFIRM_QUIET,
                Component.literal("back to the croft"), null,
                b -> { helpOpen = false; rebuildWidgets(); }));
        setInitialFocus(back);
    }

    // quit confirm panel geometry, shared between widget layout and chrome
    private static final int QUIT_PANEL_H = 92;
    private static final int QUIT_PANEL_PAD = 14;

    private int quitPanelW() {
        return Math.min(280, this.width - 40);
    }

    private int quitPanelY() {
        return this.height / 2 - QUIT_PANEL_H / 2 - 12;
    }

    private void initQuitConfirm() {
        int pw = quitPanelW();
        int px = (this.width - pw) / 2;
        int gap = 8;
        int half = (pw - QUIT_PANEL_PAD * 2 - gap) / 2;
        int by = quitPanelY() + QUIT_PANEL_H - QUIT_PANEL_PAD - 20;
        var stay = addRenderableWidget(new CometButton(px + QUIT_PANEL_PAD, by, half, 20,
                CometButton.Style.CONFIRM_QUIET,
                Component.literal("Stay a while"), null,
                b -> { quitOpen = false; rebuildWidgets(); }));
        addRenderableWidget(new CometButton(px + QUIT_PANEL_PAD + half + gap, by, half, 20,
                CometButton.Style.CONFIRM_ACCENT,
                Component.literal("Quit"), null,
                b -> Minecraft.getInstance().stop()));
        setInitialFocus(stay);
    }

    private static String langCode(Minecraft mc) {
        try {
            String code = mc.getLanguageManager().getSelected();
            return code.length() >= 2 ? code.substring(0, 2).toUpperCase() : "EN";
        } catch (Throwable t) {
            return "EN";
        }
    }

    private void openModsScreen(Minecraft mc) {
        try {
            Class<?> cls = Class.forName("com.terraformersmc.modmenu.gui.ModsScreen");
            mc.setScreen((Screen) cls.getConstructor(Screen.class).newInstance(this));
        } catch (Throwable e) {
            showToast(modCount + " mods, all humming.");
        }
    }

    private void showToast(String msg) {
        this.toast = msg;
        this.toastUntil = sky.time() + 2.2f;
    }

    // --- input ---

    @Override
    public boolean shouldCloseOnEsc() {
        return false; // like vanilla TitleScreen: ESC must not close into a null screen
    }

    @Override
    public boolean keyPressed(KeyEvent event) {
        if ((quitOpen || helpOpen) && event.key() == 256 /* GLFW_KEY_ESCAPE */) {
            quitOpen = false;
            helpOpen = false;
            rebuildWidgets();
            return true;
        }
        return super.keyPressed(event);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    // --- background: the living sky (rendering shared via CometSky) ---

    @Override
    public void extractBackground(GuiGraphicsExtractor gfx, int mouseX, int mouseY, float partialTick) {
        sky.tick(mouseX, mouseY, this.width, this.height);
        sky.render(gfx, this.width, this.height);
    }

    // --- foreground chrome + widgets ---

    @Override
    public void extractRenderState(GuiGraphicsExtractor gfx, int mouseX, int mouseY, float partialTick) {
        Font font = this.font;
        Matrix3x2fStack pose = gfx.pose();
        int padX = leftPad();
        int topY = Math.max(16, (int) (this.height * 0.085f));

        // wordmark: "Comet / Croft" with drop shadow, comet mark alongside
        int wordScale = wordmarkScale();
        int lineStep = font.lineHeight + 2;
        pose.pushMatrix();
        pose.translate(padX, topY);
        pose.scale(wordScale);
        gfx.text(font, "Comet", 0, 0, CREAM, true);
        gfx.text(font, "Croft", 0, lineStep, CREAM, true);
        pose.popMatrix();
        int wordBottom = topY + (lineStep + font.lineHeight) * wordScale;

        // little comet glyph beside the wordmark: bright head + diagonal tail
        int gx = padX + font.width("Comet") * wordScale + 12;
        int gy = topY + 2;
        gfx.fill(gx + 12, gy, gx + 16, gy + 4, 0xFFFFF3DC);
        for (int i = 1; i <= 6; i++) {
            int a = 220 - i * 32;
            gfx.fill(gx + 12 - i * 3, gy + 1 + i * 3, gx + 15 - i * 3, gy + 4 + i * 3, (a << 24) | 0xFFB454);
        }

        // subtitle, directly under the wordmark
        String tagline = "a homestead under a strange sky";
        gfx.text(font, tagline, padX, wordBottom + 6, SUBTITLE);

        // splash: the vanilla-splash spot — hanging off the wordmark's right
        // side, centered on the logo block, so it clearly belongs to the logo
        int wordW = Math.max(font.width("Comet"), font.width("Croft")) * wordScale;
        float splashCx = padX + wordW + 34 + font.width(splash) / 2f;
        float splashCy = topY + (lineStep + font.lineHeight) * wordScale / 2f;
        pose.pushMatrix();
        pose.translate(splashCx, splashCy);
        pose.rotate((float) Math.toRadians(-13));
        float pulse = 1f + 0.05f * (float) Math.sin(sky.time() * 5.5f);
        pose.scale(pulse);
        gfx.text(font, splash, -font.width(splash) / 2, -font.lineHeight / 2, SPLASH_GOLD, true);
        pose.popMatrix();

        // footer
        int fy = this.height - 12;
        String left = "Comet Croft v0.1.0 ◆ Minecraft 26.1.2 ◆ " + modCount + " mods";
        gfx.text(font, left, padX, fy, FOOTER);
        String right = "made under a strange sky";
        gfx.text(font, right, this.width - padX - font.width(right), fy, 0xFF6F7C9B);

        // toast
        if (toast != null && sky.time() < toastUntil) {
            int tw = font.width(toast);
            int tx = (this.width - tw) / 2, ty = this.height - 34;
            gfx.fill(tx - 8, ty - 5, tx + tw + 8, ty + 12, 0xEB0B1120);
            gfx.outline(tx - 8, ty - 5, tw + 16, 17, 0x4DFFB454);
            gfx.text(font, toast, tx, ty, CREAM);
        }

        // How to Play: scrim + panel, same chrome as the quit confirm
        if (helpOpen) {
            gfx.fill(0, 0, this.width, this.height, 0x8C04070E);
            int pw = Math.min(300, this.width - 40);
            int ph = 24 + helpBodyHeight() + 30;
            int panelX = (this.width - pw) / 2;
            int panelY = Math.max(8, (this.height - ph) / 2);
            gfx.fillGradient(panelX, panelY, panelX + pw, panelY + ph, 0xF7161E34, 0xF70C1222);
            gfx.outline(panelX, panelY, pw, ph, 0x29FFCD96);
            pose.pushMatrix();
            pose.translate(panelX + pw / 2f, panelY + 8);
            pose.scale(1.25f);
            String title = "How to Play";
            gfx.text(font, title, -font.width(title) / 2, 0, CREAM, true);
            pose.popMatrix();
            int ly = panelY + 24;
            for (String line : HELP_LINES) {
                if (!line.isEmpty()) {
                    boolean key = line.startsWith("R:") || line.startsWith("U:");
                    gfx.text(font, line, panelX + 14 + (key ? 10 : 0), ly, key ? LANTERN : SUBTITLE);
                }
                ly += font.lineHeight + 2;
            }
        }

        // quit confirm: scrim + panel under the confirm buttons
        if (quitOpen) {
            gfx.fill(0, 0, this.width, this.height, 0x8C04070E);
            int pw = quitPanelW();
            int panelX = (this.width - pw) / 2;
            int panelY = quitPanelY();
            gfx.fillGradient(panelX, panelY, panelX + pw, panelY + QUIT_PANEL_H, 0xF7161E34, 0xF70C1222);
            gfx.outline(panelX, panelY, pw, QUIT_PANEL_H, 0x29FFCD96);
            // lantern hairline along the panel's top edge, echoing the hero accent
            gfx.fill(panelX + 1, panelY + 1, panelX + pw - 1, panelY + 2, 0x40FFB454);
            // title at 2x: integer scale keeps the pixel font crisp
            pose.pushMatrix();
            pose.translate(panelX + pw / 2f, panelY + QUIT_PANEL_PAD);
            pose.scale(2.0f);
            String q = "Leave the croft?";
            gfx.text(font, q, -font.width(q) / 2, 0, CREAM, true);
            pose.popMatrix();
            String f2 = "The lantern will keep 'til you return.";
            gfx.text(font, f2, (this.width - font.width(f2)) / 2, panelY + QUIT_PANEL_PAD + 24, SUBTITLE);
        }

        // widgets on top
        super.extractRenderState(gfx, mouseX, mouseY, partialTick);
    }
}
