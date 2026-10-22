package local.t3l.launcher;

/** Verified mappings from the installed 0.1.1 launcher; no Maps destination. */
public final class AppTargets {
    public static final String AUTO = "gb.xxy.hr/.activities.DispatcherActivity";
    public static final String RADIO = "com.tw.radio/.RadioActivity";
    public static final String MUSIC = "com.tw.music/.MusicActivity";
    public static final String BLUETOOTH = "com.tw.bt/.ATBluetoothActivity";
    public static final String SETTINGS = "com.android.settings/.Settings";
    public static final String EQ = "com.tw.eq/.EQActivity";
    public static final String FACTORY = "com.dofun.variety/com.dofun.overseasvariety.Launcher";

    private AppTargets() {}

    public static String component(String action) {
        if ("auto".equals(action)) return AUTO;
        if ("radio".equals(action)) return RADIO;
        if ("music".equals(action)) return MUSIC;
        if ("bluetooth".equals(action)) return BLUETOOTH;
        if ("settings".equals(action)) return SETTINGS;
        if ("eq".equals(action)) return EQ;
        return null;
    }
}
