package local.t3l.launcher;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.TextUtils;
import android.text.style.RelativeSizeSpan;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.PrintWriter;
import java.util.LinkedHashMap;
import java.util.Map;

/** Native weighted layout, static vector artwork, no scrolling or animation. */
public final class DashboardView extends LinearLayout {
    public interface Listener { void action(String key); }

    public static final int BACKGROUND = Color.rgb(21, 25, 31);
    public static final int SURFACE = Color.rgb(36, 42, 51);
    public static final int ACCENT = Color.rgb(39, 200, 232);
    public static final int TEXT = Color.rgb(245, 247, 250);
    public static final int SECONDARY = Color.rgb(158, 170, 186);
    private static final int BORDER = Color.rgb(51, 59, 71);

    private final Listener listener;
    private final boolean compact;
    private final Map<String, View> targets = new LinkedHashMap<>();
    private final Map<String, TextView> labels = new LinkedHashMap<>();
    private TextView heroTime;
    private TextView heroDate;
    private String lastBluetooth = "";
    private String lastWifi = "";
    private String lastRadio = "FM Radio";

    public DashboardView(Context context, Listener listener) {
        super(context);
        this.listener = listener;
        compact = getResources().getConfiguration().screenHeightDp < 500
                || getResources().getConfiguration().screenWidthDp < 900;
        setOrientation(VERTICAL);
        setBackgroundColor(BACKGROUND);
        // No in-app header: the head unit's native system bar already shows
        // navigation, Bluetooth, Wi-Fi and the clock. Help/recovery is reachable
        // from the Apps drawer.
        setPadding(dp(16), dp(12), dp(16), dp(12));
        setClipToPadding(true);

        LinearLayout main = new LinearLayout(context);
        main.setOrientation(HORIZONTAL);
        LayoutParams mainParams = new LayoutParams(LayoutParams.MATCH_PARENT, 0, 1);
        mainParams.bottomMargin = dp(12);
        addView(main, mainParams);

        FrameLayout hero = hero();
        LayoutParams heroParams = new LayoutParams(0, LayoutParams.MATCH_PARENT, 39);
        heroParams.rightMargin = dp(12);
        main.addView(hero, heroParams);

        LinearLayout right = new LinearLayout(context);
        right.setOrientation(VERTICAL);
        main.addView(right, new LayoutParams(0, LayoutParams.MATCH_PARENT, 61));
        LinearLayout top = cardRow(
                card("radio", "Radio", "FM Radio", R.drawable.ic_radio, TEXT),
                card("music", "Music", "Local Playback", R.drawable.ic_music, Color.rgb(239, 91, 137)));
        LayoutParams topParams = new LayoutParams(LayoutParams.MATCH_PARENT, 0, 1);
        topParams.bottomMargin = dp(12);
        right.addView(top, topParams);
        right.addView(cardRow(
                card("bluetooth", "Bluetooth", "Calls & Audio", R.drawable.ic_bluetooth, ACCENT),
                card("apps", "Apps", "Installed Apps", R.drawable.ic_apps, TEXT)),
                new LayoutParams(LayoutParams.MATCH_PARENT, 0, 1));

        LinearLayout footer = cardRow(
                utility("settings", "Settings", "System", R.drawable.ic_settings),
                utility("eq", "EQ / Audio", "Sound Settings", R.drawable.ic_eq));
        addView(footer, new LayoutParams(LayoutParams.MATCH_PARENT, dp(compact ? 68 : 76)));
    }

    private FrameLayout hero() {
        FrameLayout hero = target("auto");
        GradientDrawable gradient = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[] {Color.rgb(0, 119, 141), Color.rgb(8, 66, 83), Color.rgb(11, 37, 47)});
        gradient.setCornerRadius(dp(15));
        hero.setBackground(gradient);
        hero.setClipToOutline(true);
        GradientDrawable outline = rounded(Color.TRANSPARENT, Color.rgb(25, 156, 180));
        hero.setForeground(outline);

        ImageView landscape = icon(R.drawable.hero_landscape, 0);
        landscape.setScaleType(ImageView.ScaleType.FIT_XY);
        hero.addView(landscape, frame(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT, Gravity.FILL));

        LinearLayout clock = new LinearLayout(getContext());
        clock.setOrientation(VERTICAL);
        heroTime = text("hero-time", "", compact ? 36 : 44, TEXT, true);
        heroTime.setIncludeFontPadding(false);
        clock.addView(heroTime);
        heroDate = text("hero-date", "", compact ? 15 : 18, Color.rgb(190, 217, 225), false);
        heroDate.setPadding(0, dp(5), 0, 0);
        clock.addView(heroDate);
        FrameLayout.LayoutParams clockParams = frame(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.TOP | Gravity.LEFT);
        clockParams.setMargins(dp(20), dp(20), dp(16), 0);
        hero.addView(clock, clockParams);

        ImageView arrow = icon(R.drawable.ic_projection, 0);
        FrameLayout.LayoutParams arrowParams = frame(dp(compact ? 102 : 130), dp(compact ? 102 : 130), Gravity.CENTER);
        arrowParams.topMargin = dp(compact ? 8 : 16);
        hero.addView(arrow, arrowParams);

        LinearLayout caption = new LinearLayout(getContext());
        caption.setOrientation(VERTICAL);
        TextView title = text("auto-title", "Android Auto", compact ? 24 : 28, TEXT, true);
        caption.addView(title);
        TextView subtitle = text("auto-subtitle", "Phone projection • Maps • Media", compact ? 12 : 14, Color.rgb(174, 202, 213), false);
        subtitle.setPadding(0, dp(3), 0, 0);
        caption.addView(subtitle);
        FrameLayout.LayoutParams captionParams = frame(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.BOTTOM | Gravity.LEFT);
        captionParams.setMargins(dp(20), 0, dp(38), dp(20));
        hero.addView(caption, captionParams);
        ImageView chevron = icon(R.drawable.ic_chevron, ACCENT);
        FrameLayout.LayoutParams chevronParams = frame(dp(13), dp(24), Gravity.BOTTOM | Gravity.RIGHT);
        chevronParams.setMargins(0, 0, dp(19), dp(27));
        hero.addView(chevron, chevronParams);
        hero.setContentDescription("Android Auto. Headunit Reloaded. Phone projection, Maps and Media");
        return hero;
    }

    private FrameLayout card(String key, String title, String subtitle, int resource, int color) {
        FrameLayout card = target(key);
        ImageView image = icon(resource, color);
        FrameLayout.LayoutParams imageParams = frame(dp(compact ? 36 : 43), dp(compact ? 36 : 43), Gravity.TOP | Gravity.LEFT);
        imageParams.setMargins(dp(20), dp(compact ? 15 : 19), 0, 0);
        card.addView(image, imageParams);

        TextView heading = text(key + "-title", title, compact ? 20 : 23, TEXT, false);
        FrameLayout.LayoutParams headingParams = frame(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.BOTTOM | Gravity.LEFT);
        headingParams.setMargins(dp(20), 0, dp(35), dp(compact ? 37 : 42));
        card.addView(heading, headingParams);
        TextView detail = text(key + "-subtitle", subtitle, compact ? 12 : 14, SECONDARY, false);
        FrameLayout.LayoutParams detailParams = frame(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.BOTTOM | Gravity.LEFT);
        detailParams.setMargins(dp(20), 0, dp(35), dp(compact ? 16 : 19));
        card.addView(detail, detailParams);
        addChevron(card);
        card.setContentDescription(title + ". " + subtitle);
        return card;
    }

    private FrameLayout utility(String key, String title, String subtitle, int resource) {
        FrameLayout card = target(key);
        ImageView image = icon(resource, TEXT);
        FrameLayout.LayoutParams imageParams = frame(dp(41), dp(41), Gravity.LEFT | Gravity.CENTER_VERTICAL);
        imageParams.leftMargin = dp(22);
        card.addView(image, imageParams);
        LinearLayout caption = new LinearLayout(getContext());
        caption.setOrientation(VERTICAL);
        caption.addView(text(key + "-title", title, compact ? 19 : 22, TEXT, false));
        TextView detail = text(key + "-subtitle", subtitle, compact ? 12 : 14, SECONDARY, false);
        detail.setPadding(0, dp(2), 0, 0);
        caption.addView(detail);
        FrameLayout.LayoutParams captionParams = frame(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.CENTER_VERTICAL);
        captionParams.setMargins(dp(82), 0, dp(44), 0);
        card.addView(caption, captionParams);
        ImageView chevron = icon(R.drawable.ic_chevron, SECONDARY);
        FrameLayout.LayoutParams arrow = frame(dp(12), dp(20), Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        arrow.rightMargin = dp(22);
        card.addView(chevron, arrow);
        card.setContentDescription(title + ". " + subtitle);
        return card;
    }

    private LinearLayout cardRow(View first, View second) {
        LinearLayout row = new LinearLayout(getContext());
        LayoutParams left = new LayoutParams(0, LayoutParams.MATCH_PARENT, 1);
        left.rightMargin = dp(12);
        row.addView(first, left);
        row.addView(second, new LayoutParams(0, LayoutParams.MATCH_PARENT, 1));
        return row;
    }

    private FrameLayout target(String key) {
        FrameLayout target = new FrameLayout(getContext());
        StateListDrawable states = new StateListDrawable();
        states.addState(new int[] {android.R.attr.state_pressed}, rounded(Color.rgb(44, 54, 65), ACCENT));
        states.addState(new int[] {android.R.attr.state_focused}, rounded(SURFACE, ACCENT));
        states.addState(new int[] {}, rounded(SURFACE, BORDER));
        target.setBackground(states);
        target.setMinimumWidth(dp(48));
        target.setMinimumHeight(dp(48));
        clickable(target, key);
        return target;
    }

    private void addChevron(FrameLayout target) {
        ImageView arrow = icon(R.drawable.ic_chevron, SECONDARY);
        FrameLayout.LayoutParams params = frame(dp(12), dp(20), Gravity.RIGHT | Gravity.BOTTOM);
        params.setMargins(0, 0, dp(18), dp(27));
        target.addView(arrow, params);
    }

    private void clickable(View view, final String key) {
        view.setClickable(true);
        view.setFocusable(true);
        view.setOnClickListener(new OnClickListener() {
            @Override public void onClick(View clicked) { listener.action(key); }
        });
        targets.put(key, view);
    }

    private TextView text(String key, String value, float size, int color, boolean bold) {
        TextView text = new TextView(getContext());
        text.setText(value);
        text.setTextColor(color);
        text.setTextSize(size);
        text.setTypeface(Typeface.create("sans-serif", bold ? Typeface.BOLD : Typeface.NORMAL));
        text.setMaxLines(1);
        text.setEllipsize(TextUtils.TruncateAt.END);
        labels.put(key, text);
        return text;
    }

    private ImageView icon(int resource, int tint) {
        ImageView image = new ImageView(getContext());
        image.setImageResource(resource);
        if (tint != 0) image.setColorFilter(tint);
        image.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        return image;
    }

    private GradientDrawable rounded(int fill, int stroke) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(fill);
        drawable.setCornerRadius(dp(15));
        drawable.setStroke(dp(1), stroke);
        return drawable;
    }

    private FrameLayout.LayoutParams frame(int width, int height, int gravity) {
        return new FrameLayout.LayoutParams(width, height, gravity);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    public void clock(String time, String date) {
        SpannableString hero = new SpannableString(time);
        int suffix = time.lastIndexOf(' ');
        if (suffix >= 0) hero.setSpan(new RelativeSizeSpan(0.55f), suffix + 1, time.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        heroTime.setText(hero);
        heroDate.setText(date);
        heroTime.setContentDescription(time);
        heroDate.setContentDescription(date);
    }

    public void status(String bluetooth, boolean bluetoothOn, boolean bluetoothConnected,
                       String wifi, boolean wifiOn, boolean wifiConnected) {
        // Status icons live in the head unit's native system bar; this launcher
        // keeps only the textual state for diagnostics and the About dialog.
        lastBluetooth = bluetooth;
        lastWifi = wifi;
    }

    /** Shows the station currently tuned in the factory radio app (TXZNet protocol). */
    public void radio(String station) {
        lastRadio = station;
        TextView view = labels.get("radio-subtitle");
        if (view != null) view.setText(station);
        View card = targets.get("radio");
        if (card != null) card.setContentDescription("Radio. " + station);
    }

    public void diagnostics(PrintWriter writer) {
        Rect box = new Rect();
        float density = getResources().getDisplayMetrics().density;
        writer.println("T3L_LAYOUT width=" + getWidth() + " height=" + getHeight() + " density=" + density + " compact=" + compact);
        for (Map.Entry<String, View> item : targets.entrySet()) {
            View view = item.getValue();
            view.getGlobalVisibleRect(box);
            writer.println("T3L_TARGET " + item.getKey() + " bounds=" + box.left + "," + box.top + "," + box.right + "," + box.bottom
                    + " dp=" + view.getWidth() / density + "x" + view.getHeight() / density);
        }
        for (Map.Entry<String, TextView> item : labels.entrySet()) {
            TextView view = item.getValue();
            boolean clipped = view.getLayout() != null && view.getLayout().getLineCount() > 0 && view.getLayout().getEllipsisCount(0) > 0;
            writer.println("T3L_LABEL " + item.getKey() + " clipped=" + clipped + " text=" + view.getText());
        }
        writer.println("T3L_STATUS bluetooth=" + lastBluetooth);
        writer.println("T3L_STATUS wifi=" + lastWifi);
        writer.println("T3L_STATUS radio=" + lastRadio);
    }
}
