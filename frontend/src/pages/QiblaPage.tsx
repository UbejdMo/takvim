import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { ErrorBox, Loading } from "../components/Status";
import { useQibla } from "../hooks/useApi";

type CompassStatus = "idle" | "active" | "denied" | "unsupported";

/** iOS exposes a true-north heading on the orientation event; this isn't in the standard lib. */
interface DeviceOrientationEventIOS extends DeviceOrientationEvent {
  webkitCompassHeading?: number;
}

/**
 * Qibla page: shows the great-circle bearing to the Kaaba for the selected city and, once the
 * user enables it, a live compass needle driven by the Device Orientation API.
 */
export default function QiblaPage({ city }: { city: string }) {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useQibla(city);
  const [heading, setHeading] = useState<number | null>(null);
  const [status, setStatus] = useState<CompassStatus>("idle");

  const handleOrientation = useCallback((event: DeviceOrientationEvent) => {
    const iosEvent = event as DeviceOrientationEventIOS;
    if (typeof iosEvent.webkitCompassHeading === "number") {
      setHeading(iosEvent.webkitCompassHeading);
    } else if (event.alpha !== null) {
      setHeading((360 - event.alpha) % 360);
    }
  }, []);

  useEffect(() => {
    return () => window.removeEventListener("deviceorientation", handleOrientation);
  }, [handleOrientation]);

  const enableCompass = () => {
    if (!("DeviceOrientationEvent" in window)) {
      setStatus("unsupported");
      return;
    }
    // iOS 13+ gates orientation behind an explicit permission prompt.
    const requestable = DeviceOrientationEvent as unknown as {
      requestPermission?: () => Promise<"granted" | "denied">;
    };
    if (typeof requestable.requestPermission === "function") {
      requestable
        .requestPermission()
        .then((result) => {
          if (result === "granted") {
            window.addEventListener("deviceorientation", handleOrientation);
            setStatus("active");
          } else {
            setStatus("denied");
          }
        })
        .catch(() => setStatus("denied"));
    } else {
      window.addEventListener("deviceorientation", handleOrientation);
      setStatus("active");
    }
  };

  if (isLoading) return <Loading />;
  if (isError || !data) return <ErrorBox />;

  // With no live heading, point the needle at the absolute bearing (north up).
  const rotation = heading === null ? data.bearing : data.bearing - heading;

  return (
    <>
      <h2>{t("qibla.title")}</h2>
      <div className="card center">
        <div className="compass">
          <div className="label-n">N</div>
          <div
            className="needle"
            style={{ transform: `translate(-50%, -100%) rotate(${rotation}deg)` }}
          />
          <div className="center-dot" />
        </div>
        <p>{t("qibla.bearing", { deg: Math.round(data.bearing) })}</p>
        <p className="muted">{t("qibla.distance", { km: Math.round(data.distance_km) })}</p>

        {status === "idle" && (
          <button type="button" onClick={enableCompass}>
            {t("qibla.enable")}
          </button>
        )}
        {status === "active" && <p className="muted">{t("qibla.instruction")}</p>}
        {status === "denied" && <p className="error">{t("qibla.permissionDenied")}</p>}
        {status === "unsupported" && <p className="error">{t("qibla.notSupported")}</p>}
      </div>
    </>
  );
}
