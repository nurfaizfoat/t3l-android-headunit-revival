package local.t3l.launcher;

import java.util.HashMap;
import java.util.Map;

/**
 * Kuala Lumpur / Klang Valley and Seremban FM name table for the Radio tile,
 * keyed by frequency in tenths of MHz (1 decimal place). Data as of 2026-10-21,
 * transcribed from the owner's saved list (Selangor + Negeri Sembilan regions).
 * Frequencies present in both regions carry the same names, so one flat table
 * is enough; the first entry wins in the rare duplicate case.
 */
final class RadioStations {
    /** frequency|name pairs separated by ';'. Frequencies in MHz. */
    private static final String DATA =
        // Selangor / Klang Valley transmitter table
        "87.7|Radio Klasik;88.1|Eight FM;88.5|Nasional FM;88.9|goXUAN;89.3|Ai FM;"
        + "89.9|BFM 89.9;90.3|TraXX FM;90.7|Putra FM;91.1|Asyik FM;91.5|IKIM FM;"
        + "92.3|Minnal FM;92.9|HITZ;93.6|UFM;93.9|Bernama Radio;94.5|MIX;"
        + "95.8|Fly FM;96.7|SINAR;97.2|KL FM;97.6|Hot FM;98.8|988 FM;"
        + "99.3|RAAGA;100.9|Selangor FM;101.3|Kool FM;101.8|MY FM;102.5|Salam FM;"
        + "103.0|MELODY;103.3|ERA;104.1|Best FM;104.9|ZAYAN;105.3|Suria FM;"
        + "105.7|LITE;106.0|CityPlus FM;107.9|RAKITA;"
        // Negeri Sembilan / Seremban transmitter table
        + "87.9|Radio Klasik;88.3|Eight FM;88.7|TraXX FM;89.7|Ai FM;"
        + "90.5|Minnal FM;91.7|Nasional FM;92.6|Negeri FM;93.3|988 FM;"
        + "94.2|MIX;95.0|HITZ;96.9|SINAR;97.9|MELODY;98.6|Fly FM;99.5|Hot FM;"
        + "100.6|MY FM;101.5|RAAGA;102.7|IKIM FM;103.6|ERA;104.6|LITE;"
        + "106.0|CityPlus FM;107.0|Suria FM;"
        // Additional Negeri Sembilan transmitters
        + "95.7|Negeri FM;107.7|Negeri FM";

    private static final Map<Integer, String> BY_TENTHS = new HashMap<>();

    static {
        for (String entry : DATA.split(";")) {
            String[] parts = entry.split("\\|", 2);
            if (parts.length != 2) continue;
            int key = key(Float.parseFloat(parts[0]));
            if (!BY_TENTHS.containsKey(key)) BY_TENTHS.put(key, parts[1]);
        }
    }

    private RadioStations() { }

    private static int key(float mhz) {
        return Math.round(mhz * 10f);
    }

    /** Station name for the given frequency in MHz, or null when not saved. */
    static String nameFor(float mhz) {
        return BY_TENTHS.get(key(mhz));
    }
}
