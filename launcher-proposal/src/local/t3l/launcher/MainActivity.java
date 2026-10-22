package local.t3l.launcher;

import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothProfile;
import android.content.ActivityNotFoundException;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.net.wifi.SupplicantState;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;
import java.io.File;
import java.io.FileDescriptor;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

/** Same API-27 HOME/package. Passive status, visible-only clock, radio tile mirror, no service. */
public final class MainActivity extends Activity implements DashboardView.Listener {
    /** TXZNet protocol spoken by the factory radio app (same channels the stock launcher used). */
    private static final String TXZ_RADIO_SEND = "com.txznet.launcher.radio.action.send";
    private static final String TXZ_RADIO_RECV = "com.txznet.launcher.radio.action.recv";
    /** Helper script installed on the unit; falls back to direct vendor setprop calls. */
    private static final String ADB_SCRIPT = "/data/local/tmp/adb_tcp5555.sh";

    private final ClockLabels clockLabels = new ClockLabels();
    private DashboardView dashboard;
    private boolean listening;
    private int clockRefreshes;
    private String bluetoothStatus = "Android Bluetooth status unavailable";
    private String wifiStatus = "Wi-Fi status unavailable";
    /** Tuned station in the radio app's own units (FM: tenths of MHz), -1 = unknown. */
    private float radioValue = -1f;

    private final BroadcastReceiver updates = new BroadcastReceiver() {
        @Override public void onReceive(android.content.Context context, Intent intent) {
            String action = intent.getAction();
            if (Intent.ACTION_TIME_TICK.equals(action) || Intent.ACTION_TIME_CHANGED.equals(action)
                    || Intent.ACTION_DATE_CHANGED.equals(action) || Intent.ACTION_TIMEZONE_CHANGED.equals(action)) {
                updateClock();
            } else {
                updateStatus();
            }
        }
    };

    private final BroadcastReceiver radioListener = new BroadcastReceiver() {
        @Override public void onReceive(android.content.Context context, Intent intent) {
            if (!TXZ_RADIO_RECV.equals(intent.getAction())) return;
            int code = intent.getIntExtra("action", -1);
            float raw = intent.getFloatExtra("frequency", -1f);
            Log.i("T3LDrive", "radio recv action=" + code + " frequency=" + raw);
            if (code == 1) {
                String station = frequencyLabel(raw);
                if (station != null) {
                    radioValue = raw;
                    getSharedPreferences("state", MODE_PRIVATE).edit().putFloat("radioValue", raw).apply();
                    dashboard.radio(station);
                }
            }
        }
    };

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(DashboardView.BACKGROUND);
        getWindow().setNavigationBarColor(DashboardView.BACKGROUND);
        dashboard = new DashboardView(this, this);
        setContentView(dashboard);
        // The factory radio app publishes its station on this static channel;
        // keeping the listener alive for the whole activity lifetime means the
        // tile also updates while the radio app is foregrounded.
        registerReceiver(radioListener, new IntentFilter(TXZ_RADIO_RECV));
        float saved = getSharedPreferences("state", MODE_PRIVATE).getFloat("radioValue", -1f);
        String station = frequencyLabel(saved);
        if (station != null) {
            radioValue = saved;
            dashboard.radio(station);
        }
    }

    @Override protected void onResume() {
        super.onResume();
        if (!listening) {
            IntentFilter filter = new IntentFilter();
            filter.addAction(Intent.ACTION_TIME_TICK);
            filter.addAction(Intent.ACTION_TIME_CHANGED);
            filter.addAction(Intent.ACTION_TIMEZONE_CHANGED);
            filter.addAction(Intent.ACTION_DATE_CHANGED);
            filter.addAction(BluetoothAdapter.ACTION_STATE_CHANGED);
            filter.addAction(BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED);
            filter.addAction(WifiManager.WIFI_STATE_CHANGED_ACTION);
            filter.addAction(WifiManager.NETWORK_STATE_CHANGED_ACTION);
            try {
                registerReceiver(updates, filter);
                listening = true;
            } catch (SecurityException error) {
                Toast.makeText(this, "Live status updates unavailable", Toast.LENGTH_SHORT).show();
            }
        }
        updateClock();
        updateStatus();
        askRadioForStation();
    }

    @Override protected void onDestroy() {
        stopListening();
        try {
            unregisterReceiver(radioListener);
        } catch (IllegalArgumentException alreadyGone) {
            // Activity was destroyed twice; nothing to clean up.
        }
        super.onDestroy();
    }

    /** TXZNet action 10: query the radio app so the tile reflects a station chosen earlier. */
    private void askRadioForStation() {
        // The radio app answers only while its own activity exists; otherwise the
        // tile keeps the last value persisted on this device.
        sendBroadcast(new Intent(TXZ_RADIO_SEND).putExtra("action", 10));
    }

    @Override protected void onPause() {
        // The clock/status listeners stop, but the radio listener deliberately
        // stays registered for the activity lifetime so the tile keeps mirroring
        // station changes made while the radio app itself is foregrounded.
        stopListening();
        super.onPause();
    }

    /**
     * Tile label from the radio app's unit (MHz x 100, 105.3 MHz arrives as 10530).
     * Saved stations show by name; anything else falls back to the frequency with
     * an explicit empty state, so the driver sees both what is playing and that
     * the name simply is not in the unit's offline list.
     */
    private static String frequencyLabel(float value) {
        float mhz = -1f;
        if (value >= 8750f && value <= 10800f) {
            mhz = value / 100f;
        } else if (value >= 76f && value <= 108f) {
            mhz = value;
        }
        if (mhz >= 76f && mhz <= 108f) {
            String name = RadioStations.nameFor(mhz);
            if (name != null) {
                return name + String.format(Locale.US, " · %.1f MHz", mhz);
            }
            return String.format(Locale.US, "%.1f MHz · not in saved list", mhz);
        }
        if (value >= 522f && value <= 1800f) {
            return String.format(Locale.US, "AM %d kHz", Math.round(value));
        }
        return null;
    }

    private void stopListening() {
        if (listening) {
            unregisterReceiver(updates);
            listening = false;
        }
    }

    private void updateClock() {
        String[] labels = clockLabels.at(System.currentTimeMillis(), TimeZone.getDefault());
        dashboard.clock(labels[0], labels[1]);
        clockRefreshes++;
    }

    private void updateStatus() {
        boolean bluetoothOn = false;
        boolean bluetoothConnected = false;
        try {
            BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
            if (adapter == null) {
                bluetoothStatus = "Android Bluetooth unavailable; factory Bluetooth is separate";
            } else {
                bluetoothOn = adapter.isEnabled();
                if (bluetoothOn) {
                    bluetoothConnected = adapter.getProfileConnectionState(BluetoothProfile.HEADSET) == BluetoothProfile.STATE_CONNECTED
                            || adapter.getProfileConnectionState(BluetoothProfile.A2DP) == BluetoothProfile.STATE_CONNECTED;
                }
                bluetoothStatus = bluetoothConnected ? "Android Bluetooth connected"
                        : bluetoothOn ? "Android Bluetooth on, not connected" : "Android Bluetooth off; factory Bluetooth is separate";
            }
        } catch (SecurityException error) {
            bluetoothStatus = "Android Bluetooth status unavailable";
        }
        boolean wifiOn = false;
        boolean wifiConnected = false;
        try {
            WifiManager manager = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (manager != null) {
                wifiOn = manager.isWifiEnabled();
                WifiInfo info = wifiOn ? manager.getConnectionInfo() : null;
                wifiConnected = info != null && info.getSupplicantState() == SupplicantState.COMPLETED
                        && info.getNetworkId() >= 0;
                wifiStatus = wifiConnected ? "Wi-Fi connected" : wifiOn ? "Wi-Fi on, not connected" : "Wi-Fi off";
            } else {
                wifiStatus = "Wi-Fi unavailable";
            }
        } catch (SecurityException error) {
            wifiStatus = "Wi-Fi status unavailable";
        }
        dashboard.status(bluetoothStatus, bluetoothOn, bluetoothConnected, wifiStatus, wifiOn, wifiConnected);
    }

    @Override public void action(String key) {
        if ("apps".equals(key)) {
            showApps();
        } else {
            String target = AppTargets.component(key);
            if (target != null) launch(ComponentName.unflattenFromString(target));
        }
    }

    private void showAbout() {
        // This firmware's AlertDialog drops setItems when setMessage is used,
        // so the actions render as the dialog's primary list content.
        new AlertDialog.Builder(this).setTitle("T3L Drive · Help & recovery")
                .setItems(new CharSequence[] {
                        "State · " + bluetoothStatus + " · " + wifiStatus,
                        "Network ADB · enable (port 5555)",
                        "Network ADB · disable (close port 5555)",
                        "Factory Home / Recovery",
                        "System settings"
                }, new DialogInterface.OnClickListener() {
                    @Override public void onClick(DialogInterface dialog, int which) {
                        if (which == 1) adbTcp(true);
                        else if (which == 2) adbTcp(false);
                        else if (which == 3) factoryRecovery();
                        else if (which == 4) launch(ComponentName.unflattenFromString(AppTargets.SETTINGS));
                    }
                })
                .setPositiveButton("Close", null).show();
    }

    /** Turns the vendor debug bridge on or off without root (SELinux is permissive on this unit). */
    private void adbTcp(boolean enable) {
        String[] port = {"service.adb.tcp.port", enable ? "5555" : "-1"};
        boolean done = false;
        try {
            File script = new File(ADB_SCRIPT);
            if (script.exists() && script.canExecute()) {
                Process helper = new ProcessBuilder("/system/bin/sh", ADB_SCRIPT, enable ? "on" : "off").start();
                done = helper.waitFor() == 0;
            }
        } catch (Exception runError) {
            done = false;
        }
        if (!done) {
            try {
                Process setPort = new ProcessBuilder("/system/bin/setprop", port[0], port[1]).start();
                Process bounce = new ProcessBuilder("/system/bin/setprop", "ctl.restart", "adbd").start();
                done = setPort.waitFor() == 0 && bounce.waitFor() == 0;
            } catch (Exception setError) {
                done = false;
            }
        }
        Toast.makeText(this, done
                ? (enable ? "Network ADB enabled (port 5555)" : "Network ADB disabled")
                : "Could not change the ADB port", Toast.LENGTH_SHORT).show();
    }

    private void factoryRecovery() {
        ComponentName original = ComponentName.unflattenFromString(AppTargets.FACTORY);
        if (isAvailable(original)) {
            launch(original);
        } else {
            new AlertDialog.Builder(this).setTitle("Factory launcher is not installed")
                    .setMessage("It was removed for this Android user.\n\nIf the owner requests restoration, use the laptop's documented install-existing / enable procedure. Deleted Theme user data cannot be restored.\n\nNo root, MCU or power changes are needed for the existing recovery plan.")
                    .setPositiveButton("Close", null).show();
        }
    }

    private boolean isAvailable(ComponentName component) {
        if (component == null) return false;
        try {
            ActivityInfo activity = getPackageManager().getActivityInfo(component, 0);
            return activity.exported && activity.enabled && activity.applicationInfo.enabled;
        } catch (PackageManager.NameNotFoundException | SecurityException error) {
            return false;
        }
    }

    private void launch(ComponentName component) {
        if (!isAvailable(component)) {
            Toast.makeText(this, "App unavailable", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(Intent.ACTION_MAIN).setComponent(component);
        intent.addCategory(Intent.CATEGORY_LAUNCHER);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
        try {
            startActivity(intent);
        } catch (ActivityNotFoundException | SecurityException error) {
            Toast.makeText(this, "Cannot open this app", Toast.LENGTH_SHORT).show();
        }
    }

    private void showApps() {
        PackageManager manager = getPackageManager();
        Intent query = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
        final List<ResolveInfo> apps = new ArrayList<>();
        for (ResolveInfo candidate : manager.queryIntentActivities(query, 0)) {
            if (!candidate.activityInfo.packageName.equals("com.dofun.variety")
                    && !candidate.activityInfo.packageName.equals(getPackageName())) {
                apps.add(candidate);
            }
        }
        Collections.sort(apps, new ResolveInfo.DisplayNameComparator(manager));
        CharSequence[] labels = new CharSequence[apps.size()];
        for (int index = 0; index < apps.size(); index++) {
            labels[index] = apps.get(index).loadLabel(manager);
        }
        new AlertDialog.Builder(this).setTitle("Installed apps · use while parked")
                .setItems(labels, new DialogInterface.OnClickListener() {
                    @Override public void onClick(DialogInterface dialog, int index) {
                        ActivityInfo activity = apps.get(index).activityInfo;
                        launch(new ComponentName(activity.packageName, activity.name));
                    }
                })
                .setNeutralButton("Help / recovery", new DialogInterface.OnClickListener() {
                    @Override public void onClick(DialogInterface dialog, int which) { showAbout(); }
                })
                .setNegativeButton("Close", null).show();
    }

    @Override public void dump(String prefix, FileDescriptor fd, PrintWriter writer, String[] args) {
        super.dump(prefix, fd, writer, args);
        writer.println("T3L_LIFECYCLE listening=" + listening + " clockRefreshes=" + clockRefreshes
                + " timezone=" + TimeZone.getDefault().getID());
        if (dashboard != null) dashboard.diagnostics(writer);
    }
}
