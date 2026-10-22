package local.t3l.launcher;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

/** Main-thread formatter, independent of Android for deterministic host tests. */
public final class ClockLabels {
    private final SimpleDateFormat time = new SimpleDateFormat("h:mm a", Locale.ENGLISH);
    private final SimpleDateFormat date = new SimpleDateFormat("dd MMMM yyyy", Locale.ENGLISH);
    private final Date instant = new Date();

    public String[] at(long millis, TimeZone zone) {
        time.setTimeZone(zone);
        date.setTimeZone(zone);
        instant.setTime(millis);
        return new String[] {time.format(instant), date.format(instant)};
    }
}
